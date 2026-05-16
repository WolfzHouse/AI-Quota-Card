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
    
    // Extract data from API payload
    const keyPreview = apiPayload.key_preview || 'Unknown';
    const serviceType = apiPayload.service_type || '';
    const subServiceName = apiPayload.sub_service_type_name || '';
    const quota = apiPayload.quota || {};
    const usage = apiPayload.usage || {};
    const timestamps = apiPayload.timestamps || {};
    
    // Calculate percentage
    let percentage = 0;
    let usedAmount = 0;
    let totalAmount = 0;
    let quotaDisplay = '';
    
    if (quota.type === 'duration') {
      const dailyQuota = parseFloat(quota.daily_quota || 0);
      const dailyRemaining = parseFloat(quota.daily_remaining || 0);
      const dailySpent = parseFloat(quota.daily_spent || 0);
      
      if (dailyQuota > 0) {
        percentage = Math.round((dailyRemaining / dailyQuota) * 100);
        usedAmount = dailySpent / 100; // Convert cents to dollars
        totalAmount = dailyQuota / 100;
      }
    } else if (quota.type === 'count') {
      const remaining = parseFloat(quota.remaining_quota || 0);
      quotaDisplay = `${remaining} requests remaining`;
    }
    
    // Get spend information
    const totalSpent = (parseFloat(usage.total_spent || 0) / 100).toFixed(2);
    const dailySpent = (parseFloat(usage.daily_spent || 0) / 100).toFixed(2);
    
    // Get expiration date
    const expiresAt = timestamps.expires_at || '';
    let expiresDisplay = '';
    if (expiresAt) {
      try {
        const expireDate = new Date(expiresAt);
        const now = new Date();
        const daysLeft = Math.ceil((expireDate - now) / (1000 * 60 * 60 * 24));
        expiresDisplay = `${daysLeft} days`;
      } catch (e) {
        expiresDisplay = expiresAt;
      }
    }
    
    // Get reset time
    const nextReset = quota.next_reset_at || '';
    let resetDisplay = '';
    if (nextReset) {
      try {
        const resetDate = new Date(nextReset);
        resetDisplay = resetDate.toLocaleString();
      } catch (e) {
        resetDisplay = nextReset;
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
          ${quota.type === 'duration' ? `
            <div class="usage-display">$${dailySpent} / $${totalAmount.toFixed(2)}</div>
          ` : `
            <div class="usage-display">${quotaDisplay}</div>
          `}
        </div>
        
        <div class="quota-stats">
          ${expiresDisplay ? `
            <div class="stat-item">
              <div class="stat-label">Expires in</div>
              <div class="stat-value">${expiresDisplay}</div>
            </div>
          ` : ''}
          ${resetDisplay ? `
            <div class="stat-item">
              <div class="stat-label">Reset at</div>
              <div class="stat-value">${resetDisplay}</div>
            </div>
          ` : ''}
          ${totalSpent ? `
            <div class="stat-item">
              <div class="stat-label">Total Spent</div>
              <div class="stat-value">$${totalSpent}</div>
            </div>
          ` : ''}
          <div class="stat-item">
            <div class="stat-label">Daily Spent</div>
            <div class="stat-value">$${dailySpent}</div>
          </div>
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
