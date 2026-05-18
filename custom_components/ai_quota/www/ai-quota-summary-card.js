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

    const provider = (state.attributes.provider || 'unknown').toLowerCase();
    
    if (provider.includes('trouter')) {
      const attributes = state.attributes;
    const apiPayload = attributes.api_payload || {};
    const groups = attributes.groups || [];
    
    // Extract basic info
    let keyPreview = apiPayload.key_preview || attributes.email || 'Unknown';
    let serviceType = apiPayload.service_type || '';
    let subServiceName = apiPayload.sub_service_type_name || attributes.plan || '';
    
    // Initialize display variables
    let percentage = 0;
    let quotaDisplay = '';
    let totalSpent = '0.00';
    let dailySpent = '0.00';
    let expiresDisplay = '';
    let resetTimeRemaining = '';
    
    // Try to get percentage from state first (main sensor value)
    const stateValue = parseFloat(state.state);
    if (!isNaN(stateValue) && stateValue > 0) {
      percentage = Math.round(stateValue);
    }
    
    // Get data from api_payload if available
    const usage = apiPayload.usage || {};
    const quota = apiPayload.quota || {};
    const timestamps = apiPayload.timestamps || {};
    
    // Calculate quota display based on type
    if (quota.type === 'duration') {
      const dailyQuota = parseFloat(quota.daily_quota || 0);
      const dailyRemaining = parseFloat(quota.daily_remaining || 0);
      const dailySpentVal = parseFloat(quota.daily_spent || 0);

      if (dailyQuota > 0) {
        if (percentage === 0) {
          percentage = Math.round((dailyRemaining / dailyQuota) * 100);
        }
        
        // Duration is in seconds, convert to hours
        const usedHours = (dailySpentVal / 3600).toFixed(2);
        const totalHours = (dailyQuota / 3600).toFixed(2);
        quotaDisplay = `${usedHours}h / ${totalHours}h`;
      }
      
    } else if (quota.type === 'usd') {
      const totalQuota = parseFloat(quota.total_quota || 0);
      const totalRemaining = parseFloat(quota.total_remaining || 0);
      const totalSpentQuota = parseFloat(quota.total_spent || 0);

      if (totalQuota > 0) {
        if (percentage === 0) {
          percentage = Math.round((totalRemaining / totalQuota) * 100);
        }
        
        const usedAmount = (totalSpentQuota / 100).toFixed(2);
        const totalAmount = (totalQuota / 100).toFixed(2);
        quotaDisplay = `$${usedAmount} / $${totalAmount}`;
      }
      
    } else if (quota.type === 'count') {
      const remaining = parseFloat(quota.remaining_quota || 0);
      quotaDisplay = `${remaining} requests remaining`;
      if (percentage === 0 && remaining > 0) {
        percentage = 100;
      }
    }
    
    // If still no percentage, try to extract from groups (last resort)
    if (percentage === 0 && groups.length > 0) {
      const firstGroup = groups[0];
      if (firstGroup.models && firstGroup.models.length > 0) {
        const firstModel = firstGroup.models[0];
        if (firstModel.percentage !== undefined && firstModel.percentage !== null) {
          percentage = Math.round(firstModel.percentage);
        }
      }
    }
    
    // If still no quota display, try to extract from groups
    if (!quotaDisplay && groups.length > 0) {
      const firstGroup = groups[0];
      if (firstGroup.models && firstGroup.models.length > 0) {
        const firstModel = firstGroup.models[0];
        
        // Check if resetTime contains usage info (like "1.23h / 10.00h")
        if (firstModel.resetTime && (firstModel.resetTime.includes('/') || firstModel.resetTime.includes('$'))) {
          quotaDisplay = firstModel.resetTime;
        }
        
        // Use model name as fallback
        if (!quotaDisplay) {
          quotaDisplay = firstModel.name || '';
        }
      }
    }
    
    // Get spend information
    if (usage.total_spent !== undefined) {
      totalSpent = (parseFloat(usage.total_spent) / 100).toFixed(2);
    }
    if (usage.daily_spent !== undefined) {
      dailySpent = (parseFloat(usage.daily_spent) / 100).toFixed(2);
    }
    
    // Get expiration date
    const expiresAt = timestamps.expires_at || '';
    if (expiresAt) {
      try {
        const expireDate = new Date(expiresAt);
        const now = new Date();
        const daysLeft = Math.ceil((expireDate - now) / (1000 * 60 * 60 * 24));
        expiresDisplay = daysLeft > 0 ? `${daysLeft} days` : 'Expired';
      } catch (e) {
        expiresDisplay = expiresAt;
      }
    }
    
    // Get reset time
    const nextReset = quota.next_reset_at || '';
    if (nextReset) {
      try {
        const resetDate = new Date(nextReset);
        const now = new Date();
        const diffMs = resetDate - now;

        if (diffMs > 0) {
          const hours = Math.floor(diffMs / (1000 * 60 * 60));
          const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
          resetTimeRemaining = `${hours}h ${minutes}m`;
        } else {
          resetTimeRemaining = 'Ready to reset';
        }
      } catch (e) {
        resetTimeRemaining = '';
      }
    }
    
    // Determine color based on percentage
    let barColor = '#4caf50'; // Green
    if (percentage < 30) {
      barColor = '#f44336'; // Red
    } else if (percentage < 60) {
      barColor = '#ff9800'; // Orange
    }
    
    // Build the card HTML
    this.content.innerHTML = `
      <style>
        .quota-card {
          font-family: var(--paper-font-body1_-_font-family);
        }
        .quota-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          padding-bottom: 12px;
          border-bottom: 1px solid var(--divider-color);
        }
        .api-key {
          font-size: 14px;
          color: var(--secondary-text-color);
          font-family: monospace;
        }
        .service-type {
          font-size: 12px;
          color: var(--primary-color);
          font-weight: 500;
          text-transform: uppercase;
        }
        .quota-main {
          margin-bottom: 16px;
        }
        .percentage-display {
          font-size: 48px;
          font-weight: 300;
          color: var(--primary-text-color);
          text-align: center;
          margin: 16px 0;
        }
        .progress-bar {
          width: 100%;
          height: 8px;
          background-color: var(--divider-color);
          border-radius: 4px;
          overflow: hidden;
          margin: 12px 0;
        }
        .progress-fill {
          height: 100%;
          background-color: ${barColor};
          transition: width 0.3s ease;
        }
        .quota-stats {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-top: 16px;
        }
        .stat-item {
          padding: 12px;
          background-color: var(--card-background-color);
          border-radius: 8px;
          border: 1px solid var(--divider-color);
        }
        .stat-label {
          font-size: 12px;
          color: var(--secondary-text-color);
          margin-bottom: 4px;
        }
        .stat-value {
          font-size: 16px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .usage-display {
          text-align: center;
          font-size: 18px;
          color: var(--secondary-text-color);
          margin: 8px 0;
        }
      </style>
      
      <div class="quota-card">
        <div class="quota-header">
          <div>
            <div class="service-type">${serviceType.toUpperCase()} ${subServiceName ? '- ' + subServiceName : ''}</div>
            <div class="api-key">${keyPreview}</div>
          </div>
        </div>
        
        <div class="quota-main">
          <div class="percentage-display">${percentage}%</div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${percentage}%"></div>
          </div>
          ${quotaDisplay ? `<div class="usage-display">${quotaDisplay}</div>` : ''}
        </div>

        <div class="quota-stats">
          ${expiresDisplay ? `
            <div class="stat-item">
              <div class="stat-label">Expires in</div>
              <div class="stat-value">${expiresDisplay}</div>
            </div>
          ` : ''}
          ${resetTimeRemaining ? `
            <div class="stat-item">
              <div class="stat-label">Reset in</div>
              <div class="stat-value">${resetTimeRemaining}</div>
            </div>
          ` : ''}
          ${totalSpent && parseFloat(totalSpent) > 0 ? `
            <div class="stat-item">
              <div class="stat-label">Total Spent</div>
              <div class="stat-value">$${totalSpent}</div>
            </div>
          ` : ''}
          ${dailySpent && parseFloat(dailySpent) > 0 ? `
            <div class="stat-item">
              <div class="stat-label">Daily Spent</div>
              <div class="stat-value">$${dailySpent}</div>
            </div>
          ` : ''}
        </div>
      </div>
    `;
    } else {
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
