class AIQuotaSummaryCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.content) {
      const card = document.createElement('ha-card');
      card.style.background = 'var(--ha-card-background, var(--card-background-color, #1e1e1e))';
      card.style.borderRadius = '12px';
      card.style.border = '1px solid var(--divider-color, rgba(255, 255, 255, 0.12))';
      
      this.content = document.createElement('div');
      this.content.style.padding = '16px';
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const entityId = this.config.entity;
    const state = hass.states[entityId];

    if (!state) {
      this.content.innerHTML = `
        <div style="color: var(--error-color);">
          Entity ${entityId} not found
        </div>
      `;
      return;
    }

    const attributes = state.attributes;
    const apiPayload = attributes.api_payload || {};
    const groups = attributes.groups || [];
    const provider = (attributes.provider || 'unknown').toLowerCase();
    
    // Extract basic info
    let keyPreview = apiPayload.key_preview || attributes.email || 'Unknown';
    let plan = attributes.plan || 'Free';
    let providerName = 'AI Quota';
    
    if (provider.includes('claude') || provider.includes('anthropic')) {
      providerName = 'Claude';
    } else if (provider.includes('codex') || provider.includes('openai') || provider.includes('chatgpt')) {
      providerName = 'Codex';
    } else if (provider.includes('trouter')) {
      providerName = 'Trouter';
    } else if (provider.includes('gemini')) {
      providerName = 'Gemini';
    }
    
    // Select Icon based on Provider
    let iconSvg = '';
    if (providerName === 'Claude') {
      iconSvg = `<svg viewBox="0 0 24 24" width="28" height="28" style="background: #e19076; border-radius: 4px; padding: 2px;">
                   <path fill="#fff" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                 </svg>`; // Generic placeholder logo for Anthropic
    } else if (providerName === 'Codex') {
      iconSvg = `<svg viewBox="0 0 24 24" width="28" height="28" style="background: #10a37f; border-radius: 4px; padding: 2px;">
                   <path fill="#fff" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14c-2.76 0-5-2.24-5-5h10c0 2.76-2.24 5-5 5z"/>
                 </svg>`; // Generic placeholder logo for OpenAI
    } else {
      iconSvg = `<ha-icon icon="mdi:robot-outline" style="color: var(--primary-color); --mdc-icon-size: 28px;"></ha-icon>`;
    }
    
    // Extract all models/quotas to display
    let quotas = [];
    if (groups && groups.length > 0) {
      groups.forEach(group => {
        if (group.models && group.models.length > 0) {
          quotas.push(...group.models);
        }
      });
    }

    // Build the quotas HTML
    let quotasHtml = '';
    if (quotas.length === 0) {
      quotasHtml = `<div class="empty-state">No quota data available</div>`;
    } else {
      quotas.forEach(q => {
        let pct = 0;
        if (q.percentage !== undefined && q.percentage !== null) {
          pct = Math.round(q.percentage);
        } else if (q.limit > 0) {
          pct = Math.round(((q.limit - (q.usage || 0)) / q.limit) * 100);
        }
        
        let color = '#4caf50'; // Green
        if (pct < 20) color = '#f44336'; // Red
        else if (pct < 50) color = '#ff9800'; // Orange
        else if (pct > 99) color = '#00e676'; // Bright green
        
        // Quota usage text
        let usageText = q.usageDisplay || `${q.usage || 0} / ${q.limit || 0}`;
        if (!q.usageDisplay && (q.usage === undefined || q.limit === undefined)) {
            usageText = "";
        }
        
        // Reset time string
        let timeStr = q.expiresIn || q.resetTime || 'N/A';
        if (timeStr.startsWith('20') && timeStr.includes('T')) {
           // It's an ISO date, try to format
           try {
               const dt = new Date(timeStr);
               const now = new Date();
               const diff = dt - now;
               if (diff > 0) {
                   const d = Math.floor(diff / (1000 * 60 * 60 * 24));
                   const h = Math.floor((diff / (1000 * 60 * 60)) % 24);
                   const m = Math.floor((diff / 1000 / 60) % 60);
                   if (d > 0) timeStr = `in ${d}d ${h}h`;
                   else timeStr = `in ${h}h ${m}m`;
               } else {
                   timeStr = 'Expired';
               }
           } catch(e) {}
        }
        if (timeStr && !timeStr.startsWith('in ') && timeStr !== 'N/A' && timeStr !== 'Expired') {
             // For trouter or generic cases, just display as is
             if (!timeStr.includes('Reset') && !timeStr.includes('$') && !timeStr.includes('tokens')) {
                 timeStr = `in ${timeStr}`;
             }
        }
        
        quotasHtml += `
          <div class="quota-row">
            <div class="quota-label">
              <div class="dot" style="background-color: ${color};"></div>
              <span class="quota-name">${q.name}</span>
            </div>
            <div class="quota-progress-container">
              <div class="quota-progress-text">
                <span class="quota-usage">${usageText}</span>
                <span class="quota-pct" style="color: ${color};">${pct}%</span>
              </div>
              <div class="quota-bar-bg">
                <div class="quota-bar-fill" style="width: ${pct}%; background-color: ${color};"></div>
              </div>
            </div>
            <div class="quota-time">${timeStr}</div>
          </div>
        `;
      });
    }

    this.content.innerHTML = `
      <style>
        .router-card {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          color: var(--primary-text-color);
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 24px;
        }
        .header-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .provider-logo {
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .provider-info {
          display: flex;
          flex-direction: column;
        }
        .provider-title {
          font-size: 16px;
          font-weight: 600;
          line-height: 1.2;
        }
        .provider-email {
          font-size: 12px;
          color: var(--secondary-text-color, #9e9e9e);
          margin-top: 2px;
        }
        .header-actions {
          display: flex;
          gap: 8px;
          color: var(--secondary-text-color, #9e9e9e);
        }
        .action-btn {
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          transition: background-color 0.2s;
        }
        .action-btn:hover {
          background-color: var(--secondary-background-color, rgba(255,255,255,0.1));
          color: var(--primary-text-color);
        }
        .quota-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .quota-row {
          display: flex;
          align-items: center;
          gap: 16px;
        }
        .quota-label {
          display: flex;
          align-items: center;
          gap: 8px;
          width: 140px;
          flex-shrink: 0;
        }
        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        .quota-name {
          font-size: 13px;
          font-weight: 500;
        }
        .quota-progress-container {
          flex-grow: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .quota-progress-text {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: var(--secondary-text-color, #9e9e9e);
        }
        .quota-usage {
          font-family: monospace;
        }
        .quota-pct {
          font-weight: 600;
        }
        .quota-bar-bg {
          width: 100%;
          height: 4px;
          background-color: var(--divider-color, rgba(255, 255, 255, 0.1));
          border-radius: 2px;
          overflow: hidden;
        }
        .quota-bar-fill {
          height: 100%;
          transition: width 0.3s ease;
        }
        .quota-time {
          font-size: 12px;
          color: var(--secondary-text-color, #9e9e9e);
          width: 90px;
          text-align: right;
          flex-shrink: 0;
        }
        .empty-state {
          text-align: center;
          color: var(--secondary-text-color);
          padding: 20px 0;
          font-style: italic;
        }
      </style>
      
      <div class="router-card">
        <div class="header">
          <div class="header-left">
            <div class="provider-logo">
              ${iconSvg}
            </div>
            <div class="provider-info">
              <div class="provider-title">${providerName}</div>
              <div class="provider-email">${keyPreview}</div>
            </div>
          </div>
          <div class="header-actions">
            <div class="action-btn" id="refresh-btn" title="Refresh">
              <ha-icon icon="mdi:refresh" style="--mdc-icon-size: 20px;"></ha-icon>
            </div>
            <div class="action-btn" id="more-info-btn" title="More Info">
              <ha-icon icon="mdi:dots-vertical" style="--mdc-icon-size: 20px;"></ha-icon>
            </div>
          </div>
        </div>
        
        <div class="quota-list">
          ${quotasHtml}
        </div>
      </div>
    `;
    
    // Add event listeners
    const refreshBtn = this.content.querySelector('#refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this._hass.callService('homeassistant', 'update_entity', {
          entity_id: this.config.entity
        });
      });
    }
    
    const moreInfoBtn = this.content.querySelector('#more-info-btn');
    if (moreInfoBtn) {
      moreInfoBtn.addEventListener('click', () => {
        const event = new Event('hass-more-info', {
          bubbles: true,
          cancelable: false,
          composed: true,
        });
        event.detail = { entityId: this.config.entity };
        this.dispatchEvent(event);
      });
    }
  }

  getCardSize() {
    return 4;
  }
}

customElements.define('ai-quota-summary-card', AIQuotaSummaryCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'ai-quota-summary-card',
  name: 'AI Quota Summary Card',
  description: 'Display AI quota information in a clean summary format',
  preview: true,
});
