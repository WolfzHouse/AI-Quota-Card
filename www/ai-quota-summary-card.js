class AIQuotaSummaryCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    this.config = config;
  }

  set hass(hass) {
    if (!this.content) {
      const card = document.createElement('ha-card');
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
    if (!isNaN(stateValue)) {
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

      if (dailyQuota > 0 && percentage === 0) {
        percentage = Math.round((dailyRemaining / dailyQuota) * 100);
      }
      
      // Duration is in seconds, convert to hours
      const usedHours = (dailySpentVal / 3600).toFixed(2);
      const totalHours = (dailyQuota / 3600).toFixed(2);
      quotaDisplay = `${usedHours}h / ${totalHours}h`;
      
    } else if (quota.type === 'usd') {
      const totalQuota = parseFloat(quota.total_quota || 0);
      const totalRemaining = parseFloat(quota.total_remaining || 0);
      const totalSpentQuota = parseFloat(quota.total_spent || 0);

      if (totalQuota > 0 && percentage === 0) {
        percentage = Math.round((totalRemaining / totalQuota) * 100);
      }
      
      const usedAmount = (totalSpentQuota / 100).toFixed(2);
      const totalAmount = (totalQuota / 100).toFixed(2);
      quotaDisplay = `$${usedAmount} / $${totalAmount}`;
      
    } else if (quota.type === 'count') {
      const remaining = parseFloat(quota.remaining_quota || 0);
      quotaDisplay = `${remaining} requests remaining`;
      if (percentage === 0) {
        percentage = remaining > 0 ? 100 : 0;
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
  }

  getCardSize() {
    return 4;
  }
}

customElements.define('ai-quota-summary-card', AIQuotaSummaryCard);

// Register the card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'ai-quota-summary-card',
  name: 'AI Quota Summary Card',
  description: 'Display AI quota information in a clean summary format',
  preview: true,
});
