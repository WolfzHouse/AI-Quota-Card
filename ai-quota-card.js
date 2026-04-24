class AIQuotaCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.data = { items: [], loading: false, error: null, plan: null };
  }

  setConfig(config) {
    if (!config.proxy_url) {
      throw new Error("You need to define proxy_url");
    }
    if (!config.provider) {
      throw new Error("You need to define provider");
    }
    this.config = config;
    this.fetchQuota();
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.shadowRoot.innerHTML && this.config) {
        this.render();
    }
  }

  async fetchQuota() {
    this.data.loading = true;
    this.data.error = null;
    this.render();

    try {
      const { proxy_url, provider, auth_index, email } = this.config;
      let targetUrl = '';
      let headers = {};
      let method = 'GET';
      let payloadData = undefined;

      const p = provider.toLowerCase();

      if (p === 'claude') {
        targetUrl = 'https://api.anthropic.com/api/oauth/usage';
        headers = { 'anthropic-beta': 'oauth-2025-04-20', 'Accept': 'application/json' };
      } else if (p === 'codex') {
        targetUrl = 'https://chatgpt.com/backend-api/wham/usage';
        headers = { 'User-Agent': 'codex_cli_rs/0.76.0 (Debian 13.0.0; x86_64) WindowsTerminal' };
      } else if (p === 'antigravity') {
        targetUrl = 'https://daily-cloudcode-pa.sandbox.googleapis.com/v1internal:fetchAvailableModels';
        headers = { 'User-Agent': 'antigravity/1.11.5 windows/amd64' };
        method = 'POST';
        payloadData = '{}';
      } else if (p === 'gemini-cli') {
        targetUrl = 'https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota';
        headers = { 'Content-Type': 'application/json' };
        method = 'POST';
        payloadData = JSON.stringify({ project: this.config.gemini_project_id || '' });
      } else {
        throw new Error(`Unsupported provider: ${provider}`);
      }

      const proxyApiUrl = `${proxy_url.replace(/\/$/, '')}/v0/management/api-call`;

      const reqHeaders = { 'Content-Type': 'application/json' };
      if (this.config.proxy_token) {
        reqHeaders['Authorization'] = `Bearer ${this.config.proxy_token}`;
      }

      const reqBody = {
        authIndex: String(auth_index || '0'),
        method: method,
        url: targetUrl,
        header: {
          'Authorization': 'Bearer $TOKEN$',
          'Content-Type': 'application/json',
          ...headers
        }
      };

      if (payloadData) {
        reqBody.data = payloadData;
      }

      const response = await fetch(proxyApiUrl, {
        method: 'POST',
        headers: reqHeaders,
        body: JSON.stringify(reqBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      const statusCode = result.status_code || result.statusCode;
      
      let rawBody = result.body;
      if (typeof rawBody === 'string') {
        try { rawBody = JSON.parse(rawBody); } catch (e) {}
      }

      if (statusCode >= 200 && statusCode < 300) {
         this.data.items = this.parseResponse(p, rawBody);
         this.data.plan = (p === 'codex' && rawBody?.plan_type) ? rawBody.plan_type : 'Free';
      } else {
        throw new Error(`API Error ${statusCode}: ${JSON.stringify(rawBody || result.bodyText).substring(0, 50)}`);
      }
    } catch (error) {
      this.data.error = error.message;
    } finally {
      this.data.loading = false;
      this.render();
    }
  }

  parseResponse(provider, data) {
    if (!data) return [];
    
    const formatResetTime = (targetMs) => {
      const d = new Date(targetMs);
      if (isNaN(d.getTime())) return '-';
      const abs = `${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')}, ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
      
      const diff = targetMs - Date.now();
      if (diff <= 0) return `${abs} (Ready)`;
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      
      let rel = '';
      if (days > 0) rel = `${days}d ${hours}h`;
      else if (hours > 0) rel = `${hours}h ${minutes}m`;
      else rel = `${minutes}m`;
      
      return `${abs} (${rel})`;
    };
    
    if (provider === 'claude') {
      const models = [];
      const addUsage = (key, name) => {
        const usage = data[key];
        if (usage && usage.utilization !== undefined) {
          const u = parseFloat(usage.utilization);
          if (!isNaN(u)) {
             let rt = '';
             if (usage.resets_at) {
                const ms = new Date(usage.resets_at).getTime();
                rt = formatResetTime(ms);
             }
             models.push({ name, percentage: Math.max(0, Math.min(100, 100 - u)), resetTime: rt });
          }
        }
      };
      addUsage('five_hour', '5-hour limit');
      addUsage('seven_day', '7-day limit');
      addUsage('seven_day_sonnet', '7-day-sonnet limit');
      addUsage('seven_day_opus', '7-day-opus limit');
      
      let extraUsageDisplay = null;
      const extra = data.extra_usage;
      if (extra && extra.is_enabled) {
        if (extra.used_credits !== undefined && extra.monthly_limit !== undefined) {
          extraUsageDisplay = `$${extra.used_credits} / $${extra.monthly_limit}`;
        }
      }
      
      return [{ name: 'Claude Quota', models: models, extra_usage: extraUsageDisplay }];
    } 
    

    else if (provider === 'codex') {
       const limits = [];
       
       const processWin = (name, win) => {
          if (!win) return;
          let pct = 0;
          if (win.used_percent !== undefined) {
             pct = 100 - win.used_percent;
          } else {
             const remaining = win.remaining_count || 0;
             const total = win.total_count || 1;
             pct = Math.round((Number(remaining) / Math.max(Number(total), 1)) * 100);
          }
          pct = Math.max(0, Math.min(100, pct));
          
          let resetTime = '-';
          if (win.reset_at && win.reset_at > 0) {
             const targetMs = win.reset_at < 10000000000 ? win.reset_at * 1000 : win.reset_at;
             resetTime = formatResetTime(targetMs);
          } else if (win.reset_after_seconds && win.reset_after_seconds > 0) {
             const targetMs = Date.now() + (win.reset_after_seconds * 1000);
             resetTime = formatResetTime(targetMs);
          }
          
          limits.push({ name, percentage: pct, resetTime: resetTime });
       };
       
       const rl = data.rate_limit || {};
       const crl = data.code_review_rate_limit || {};
       
       const planType = typeof data.plan_type === 'string' ? data.plan_type.toLowerCase() : 'plus';
       
       // Process main windows
       if (planType === 'free') {
           processWin('Weekly limit', rl.primary_window || data['5_hour_window'] || data['weekly_window']);
       } else {
           processWin('5-hour limit', rl.primary_window || data['5_hour_window']);
           processWin('Weekly limit', rl.secondary_window || data['weekly_window']);
       }
       
       // Process code review windows
       processWin('Code review weekly limit', crl.primary_window || data['code_review_window']);

       return [{ name: 'Codex Quota', models: limits }];
    }
    
    else if (provider === 'gemini-cli') {
       if (!Array.isArray(data.buckets)) return [];
       const limits = data.buckets.map(b => {
          let pct = Number(b.remainingFraction ?? b.remaining_fraction ?? 0) * 100;
          let rt = '';
          if (b.resetTime || b.reset_time) {
             const rtStr = b.resetTime || b.reset_time;
             const d = new Date(rtStr);
             if (!isNaN(d.getTime())) rt = formatResetTime(d.getTime());
          }
          return { name: String(b.modelId ?? b.model_id ?? 'Unknown'), percentage: Math.round(pct), resetTime: rt };
       });
       return [{ name: 'Gemini CLI Quota', models: limits }];
    }
    
    else if (provider === 'antigravity') {
      if (!data.models) return [];
      const grouped = {};
      Object.entries(data.models).forEach(([key, val]) => {
         if (val.isInternal || key.startsWith('chat_') || key === 'tab_flash_lite_preview' || key === 'tab_jump_flash_lite_preview') return;
         let name = val.displayName || val.display_name || key;
         if (!val.displayName && !val.display_name) {
             if (key === 'rev19-uic3-1p') name = 'Gemini 2.5 Computer Use';
             else if (key === 'gemini-3-pro-image') name = 'Gemini 3 Pro Image';
             else if (key === 'gemini-2.5-flash-lite') name = 'Gemini 2.5 Flash Lite';
             else if (key === 'gemini-2.5-flash') name = 'Gemini 2.5 Flash';
         }
         
         const ri = val.quotaInfo || val;
         const resetStr = ri.resetTime || ri.reset_time || '';
         let resetTime = '';
         if (resetStr) {
            const d = new Date(resetStr);
            if (!isNaN(d.getTime())) resetTime = formatResetTime(d.getTime());
         }
         
         const source = val.quotaInfo || val;
         let rem = source.remainingFraction ?? source.remaining_fraction ?? source.remaining;
         
         let parsedRemaining = null;
         if (typeof rem === 'number') {
           parsedRemaining = rem;
         } else if (typeof rem === 'string') {
           const parsed = parseFloat(rem);
           if (!isNaN(parsed)) parsedRemaining = parsed;
         }
         
         if (parsedRemaining === null) {
           parsedRemaining = resetStr ? 0 : 1;
         }
         
         let groupName = 'Other';
         const lName = name.toLowerCase();
         if (lName.includes('gemini') && lName.includes('pro')) groupName = 'Gemini Pro';
         else if (lName.includes('gemini') && lName.includes('flash')) groupName = 'Gemini Flash';
         else if (lName.includes('gemini')) groupName = 'Gemini';
         else if (lName.includes('gpt-4')) groupName = 'GPT-4';
         else if (lName.includes('gpt-3.5')) groupName = 'GPT-3.5';
         else if (lName.includes('gpt') || lName.includes('o1')) groupName = 'GPT';
         else if (lName.includes('claude')) groupName = 'Claude';
         
         if (!grouped[groupName]) grouped[groupName] = [];
         grouped[groupName].push({ name, percentage: Math.round(parsedRemaining * 100), resetTime });
      });
      
      return Object.entries(grouped).map(([name, items]) => {
         const avg = items.reduce((s, i) => s + i.percentage, 0) / items.length;
         const rt = items.find(i => i.resetTime)?.resetTime || '';
         return { name, models: items, percentage: Math.round(avg), resetTime: rt };
      }).sort((a,b) => a.name.localeCompare(b.name));
    }
    
    return [];
  }

  getStyles() {
    return `
      :host {
        --bg-card: #202020;
        --border-color: #333333;
        --text-color: #d4d4d4;
        --text-muted: #8c8c8c;
        --meter-bg: #404040;
        --meter-green: #2ecc71;
        --meter-yellow: #f1c40f;
        --color-destructive: #e74c3c;
        --bg-muted: #2a2a2a;
        --badge-bg: #383838;
      }
      ha-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        color: var(--text-color);
        border-radius: 8px;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      }
      .header {
        background: var(--bg-muted);
        border-bottom: 1px solid var(--border-color);
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .header-info {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .title-row {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
      }
      .title-row svg {
        width: 16px;
        height: 16px;
        color: var(--meter-green);
      }
      .badges-row {
        display: flex;
        align-items: center;
        gap: 8px;
      }
      .badge {
        background: var(--badge-bg);
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 4px;
        color: #e0e0e0;
      }
      .badge svg {
        width: 12px;
        height: 12px;
      }
      .refresh-btn {
        background: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-color);
        padding: 6px 10px;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        transition: all 0.2s;
      }
      .refresh-btn:hover {
        background: var(--badge-bg);
      }
      .refresh-btn svg {
        width: 14px;
        height: 14px;
      }
      .refresh-btn.loading svg {
        animation: spin 1s linear infinite;
      }
      @keyframes spin {
        100% { transform: rotate(360deg); }
      }
      .content {
        padding: 16px;
      }
      .error-box {
        color: var(--color-destructive);
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        margin-bottom: 12px;
      }
      .error-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--color-destructive);
      }
      .group {
        margin-bottom: 16px;
      }
      .group:last-child {
        margin-bottom: 0;
      }
      .group-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        margin-bottom: 8px;
      }
      .group-title {
        font-weight: 500;
        color: #fff;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .group-count {
        color: var(--text-muted);
        font-size: 11px;
      }
      .group-stats {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 12px;
      }
      .group-pct {
        font-weight: 600;
      }
      .pct-high { color: var(--meter-green); }
      .pct-low { color: var(--meter-yellow); }
      .group-reset {
        background: var(--badge-bg);
        padding: 2px 6px;
        border-radius: 4px;
        color: var(--text-muted);
      }
      .progress-bar {
        background: var(--meter-bg);
        border-radius: 4px;
        height: 6px;
        width: 100%;
        overflow: hidden;
      }
      .progress-fill {
        height: 100%;
        transition: width 0.5s ease-out;
      }
      .bg-high { background: var(--meter-green); }
      .bg-low { background: var(--meter-yellow); }
      .sub-items {
         margin-top: 8px;
         display: flex;
         flex-direction: column;
         gap: 8px;
         padding-left: 12px;
         border-left: 2px solid var(--border-color);
      }
      .plan-info {
         font-size: 12px;
         color: var(--text-muted);
         margin-bottom: 10px;
      }
    `;
  }

  render() {
    const { provider, email, auth_index } = this.config || {};
    const { items, loading, error, plan } = this.data;

    const displayEmail = email || '********@*****.com';
    const displayIndex = auth_index !== undefined ? `Auth Index: ${auth_index}` : 'Auth 0';

    const providerTitle = provider ? provider.charAt(0).toUpperCase() + provider.slice(1) : 'Unknown';

    let contentHtml = '';

    if (error) {
      contentHtml += `
        <div class="error-box">
          <div class="error-dot"></div>
          ${error}
        </div>
      `;
    } else if (items.length === 0 && !loading) {
      contentHtml += `<div style="font-size:13px; color:var(--text-muted); font-style:italic;">No usage data found</div>`;
    } else {
      if (plan) {
         contentHtml += `<div class="plan-info">Plan: <strong>${plan}</strong></div>`;
      }
      
      const isAntigravity = provider && provider.toLowerCase() === 'antigravity';
      
      items.forEach(group => {
        let pct = group.percentage !== undefined ? group.percentage : group.models[0]?.percentage || 0;
        let pClass = pct > 20 ? 'pct-high' : 'pct-low';
        let bClass = pct > 20 ? 'bg-high' : 'bg-low';

        contentHtml += `<div class="group">`;
        
        if (group.extra_usage) {
           contentHtml += `<div class="plan-info" style="margin-bottom: 12px;">Extra Usage: <strong>${group.extra_usage}</strong></div>`;
        }

        contentHtml += `
            <div class="group-header">
              <div class="group-title">
                ${group.name}
                ${isAntigravity ? `<span class="group-count">(${group.models.length})</span>` : ''}
              </div>
              <div class="group-stats">
                <span class="${pClass}">${pct}% left</span>
                ${group.resetTime ? `<span class="group-reset">${group.resetTime}</span>` : ''}
              </div>
            </div>
            <div class="progress-bar">
               <div class="progress-fill ${bClass}" style="width: ${pct}%"></div>
            </div>
        `;
        
        if (isAntigravity) {
           contentHtml += `<div class="sub-items">`;
           group.models.forEach(m => {
              let mpClass = m.percentage > 20 ? 'pct-high' : 'pct-low';
              let mbClass = m.percentage > 20 ? 'bg-high' : 'bg-low';
              contentHtml += `
                <div class="group">
                  <div class="group-header">
                    <div class="group-title" style="font-weight: 400; font-size: 12px;">${m.name}</div>
                    <div class="group-stats">
                      <span class="${mpClass}">${m.percentage}%</span>
                      ${m.resetTime ? `<span class="group-reset" style="font-size:10px">${m.resetTime}</span>` : ''}
                    </div>
                  </div>
                  <div class="progress-bar" style="height: 4px;">
                     <div class="progress-fill ${mbClass}" style="width: ${m.percentage}%"></div>
                  </div>
                </div>
              `;
           });
           contentHtml += `</div>`;
        } else {
           contentHtml += `<div class="sub-items">`;
           group.models.forEach(m => {
              let mpClass = m.percentage > 20 ? 'pct-high' : 'pct-low';
              let mbClass = m.percentage > 20 ? 'bg-high' : 'bg-low';
              contentHtml += `
                <div class="group">
                  <div class="group-header">
                    <div class="group-title" style="font-weight: 400; font-size: 12px;">${m.name}</div>
                    <div class="group-stats">
                      <span class="${mpClass}">${m.percentage}%</span>
                      ${m.resetTime ? `<span class="group-reset" style="font-size:10px">${m.resetTime}</span>` : ''}
                    </div>
                  </div>
                  <div class="progress-bar" style="height: 4px;">
                     <div class="progress-fill ${mbClass}" style="width: ${m.percentage}%"></div>
                  </div>
                </div>
              `;
           });
           contentHtml += `</div>`;
        }
        
        contentHtml += `</div>`;
      });
    }

    this.shadowRoot.innerHTML = `
      <style>${this.getStyles()}</style>
      <ha-card>
        <div class="header">
          <div class="header-info">
            <div class="title-row">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
              ${displayEmail}
            </div>
            <div class="badges-row">
              <div class="badge">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                ${providerTitle} Quota
              </div>
              <div class="badge" style="background: transparent; color: var(--text-muted);">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                ${displayIndex}
              </div>
            </div>
          </div>
          <button class="refresh-btn ${loading ? 'loading' : ''}" id="refreshBtn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
            Refresh
          </button>
        </div>
        <div class="content">
          ${contentHtml}
        </div>
      </ha-card>
    `;

    this.shadowRoot.getElementById('refreshBtn').addEventListener('click', () => {
      this.fetchQuota();
    });
  }
}

customElements.define('ai-quota-card', AIQuotaCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "ai-quota-card",
  name: "AI Quota Card",
  preview: true,
  description: "A custom card to display AI API quotas."
});
