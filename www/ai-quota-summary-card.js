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
      
      this.content = document.createElement('div');
      this.content.style.padding = '16px';
      card.appendChild(this.content);
      this.appendChild(card);
    }

    this.render();
  }

  handleRefresh(e) {
    e.stopPropagation();
    const entityId = this.config.entity;
    this._hass.callService('homeassistant', 'update_entity', {
      entity_id: entityId
    });
    
    // Visual feedback
    const button = e.currentTarget;
    button.style.transform = 'rotate(360deg)';
    button.style.transition = 'transform 0.5s ease';
    setTimeout(() => {
      button.style.transform = 'rotate(0deg)';
    }, 500);
  }

  handleCardClick() {
    const entityId = this.config.entity;
    const event = new Event('hass-more-info', {
      bubbles: true,
      composed: true,
    });
    event.detail = { entityId };
    this.dispatchEvent(event);
  }

  render() {
    const entityId = this.config.entity;
    const state = this._hass.states[entityId];

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
    
    // Detect format: 9Router has items with usageDisplay and expiresIn
    const is9Router = groups.length > 0 && 
                      groups[0].models && 
                      groups[0].models.length > 0 && 
                      groups[0].models[0].usageDisplay !== undefined;
    
    if (is9Router) {
      this.render9Router(state, attributes, groups);
    } else {
      this.renderTrouter(state, attributes, apiPayload);
    }
  }

  render9Router(state, attributes, groups) {
    const provider = attributes.provider || 'Unknown';
    const email = attributes.email || 'Unknown';
    const plan = attributes.plan || '';
    
    // Get provider icon
    const providerIcons = {
      'claude': '🤖',
      'codex': '💻',
      'openai': '🔮',
      'gemini': '✨'
    };
    const icon = providerIcons[provider.toLowerCase()] || '🔧';
    
    let quotaItemsHTML = '';
    
    if (groups.length > 0 && groups[0].models) {
      groups[0].models.forEach(model => {
        const percentage = model.percentage || 0;
        const name = model.name || 'Unknown';
        const usage = model.usage || 0;
        const limit = model.limit || 100;
        const usageDisplay = model.usageDisplay || `${usage}/${limit}`;
        const expiresIn = model.expiresIn || '';
        const resetTime = model.resetTime || '';
        
        // Determine color based on percentage
        let barColor = '#4caf50'; // Green
        if (percentage < 30) {
          barColor = '#f44336'; // Red
        } else if (percentage < 60) {
          barColor = '#ff9800'; // Orange
        }
        
        quotaItemsHTML += `
          <div class="quota-item">
            <div class="quota-item-header">
              <span class="quota-dot" style="background-color: ${barColor};"></span>
              <span class="quota-name">${name}</span>
              <span class="quota-usage">${usageDisplay}</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" style="width: ${percentage}%; background-color: ${barColor};"></div>
            </div>
            <div class="quota-item-footer">
              <span class="quota-percentage">${percentage}%</span>
              ${expiresIn ? `<span class="quota-expires">in ${expiresIn}</span>` : ''}
            </div>
          </div>
        `;
      });
    }
    
    this.content.innerHTML = `
      <style>
        .quota-card-9router {
          font-family: var(--paper-font-body1_-_font-family);
          cursor: pointer;
        }
        .quota-header-9router {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
          padding-bottom: 12px;
          border-bottom: 1px solid var(--divider-color);
        }
        .provider-icon {
          font-size: 32px;
        }
        .provider-info {
          flex: 1;
        }
        .provider-name {
          font-size: 18px;
          font-weight: 600;
          color: var(--primary-text-color);
          text-transform: capitalize;
        }
        .provider-email {
          font-size: 13px;
          color: var(--secondary-text-color);
          margin-top: 2px;
        }
        .refresh-button {
          font-size: 20px;
          color: var(--secondary-text-color);
          cursor: pointer;
          padding: 8px;
          border-radius: 50%;
          transition: background-color 0.2s;
          background: none;
          border: none;
        }
        .refresh-button:hover {
          background-color: var(--divider-color);
        }
        .quota-item {
          margin-bottom: 16px;
          padding: 12px;
          background-color: var(--card-background-color);
          border-radius: 8px;
          border: 1px solid var(--divider-color);
        }
        .quota-item-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }
        .quota-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        .quota-name {
          flex: 1;
          font-size: 14px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .quota-usage {
          font-size: 13px;
          color: var(--secondary-text-color);
        }
        .progress-bar-container {
          height: 6px;
          background-color: var(--divider-color);
          border-radius: 3px;
          overflow: hidden;
          margin-bottom: 6px;
        }
        .progress-bar-fill {
          height: 100%;
          transition: width 0.3s ease;
        }
        .quota-item-footer {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
        }
        .quota-percentage {
          color: var(--primary-text-color);
          font-weight: 500;
        }
        .quota-expires {
          color: var(--secondary-text-color);
        }
        .card-hint {
          text-align: center;
          font-size: 11px;
          color: var(--secondary-text-color);
          margin-top: 8px;
          opacity: 0.7;
        }
      </style>
      
      <div class="quota-card-9router" onclick="this.getRootNode().host.handleCardClick()">
        <div class="quota-header-9router">
          <div class="provider-icon">${icon}</div>
          <div class="provider-info">
            <div class="provider-name">${provider}</div>
            <div class="provider-email">${email}</div>
          </div>
          <button class="refresh-button" onclick="event.stopPropagation(); this.getRootNode().host.handleRefresh(event)" title="Refresh data">
            🔄
          </button>
        </div>
        
        ${quotaItemsHTML}
        
        <div class="card-hint">Tap card to view history</div>
      </div>
    `;
  }

  renderTrouter(state, attributes, apiPayload) {
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
    
    // Try to get percentage from state first
    const stateValue = parseFloat(state.state);
    if (!isNaN(stateValue)) {
      percentage = Math.round(stateValue);
    }
    
    // Get data from api_payload
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
    }
    
    // Get spending info
    if (usage.total_spent) {
      totalSpent = (usage.total_spent / 100).toFixed(2);
    }
    if (usage.daily_spent) {
      dailySpent = (usage.daily_spent / 100).toFixed(2);
    }
    
    // Get expiration info
    if (timestamps.expires_at) {
      try {
        const expiresAt = new Date(timestamps.expires_at);
        const now = new Date();
        const diff = expiresAt - now;
        
        if (diff > 0) {
          const days = Math.floor(diff / (1000 * 60 * 60 * 24));
          const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          
          if (days > 0) {
            expiresDisplay = `${days}d ${hours}h`;
          } else {
            expiresDisplay = `${hours}h`;
          }
        }
      } catch (e) {}
    }
    
    // Get reset time
    if (quota.next_reset_at) {
      try {
        const resetAt = new Date(quota.next_reset_at);
        const now = new Date();
        const diff = resetAt - now;
        
        if (diff > 0) {
          const hours = Math.floor(diff / (1000 * 60 * 60));
          const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
          resetTimeRemaining = `${hours}h ${minutes}m`;
        }
      } catch (e) {}
    }
    
    // Determine color
    let barColor = '#4caf50';
    if (percentage < 30) {
      barColor = '#f44336';
    } else if (percentage < 60) {
      barColor = '#ff9800';
    }
    
    this.content.innerHTML = `
      <style>
        .quota-card {
          font-family: var(--paper-font-body1_-_font-family);
          cursor: pointer;
        }
        .quota-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        .service-type {
          font-size: 14px;
          font-weight: 600;
          color: var(--primary-text-color);
        }
        .api-key {
          font-size: 12px;
          color: var(--secondary-text-color);
          margin-top: 4px;
        }
        .refresh-button {
          font-size: 20px;
          color: var(--secondary-text-color);
          cursor: pointer;
          padding: 8px;
          border-radius: 50%;
          transition: background-color 0.2s;
          background: none;
          border: none;
        }
        .refresh-button:hover {
          background-color: var(--divider-color);
        }
        .quota-main {
          margin-bottom: 16px;
        }
        .quota-info-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        .spending-display {
          font-size: 18px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .percentage-display {
          font-size: 18px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .progress-bar {
          height: 8px;
          background-color: var(--divider-color);
          border-radius: 4px;
          overflow: hidden;
          margin: 8px 0;
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
        .card-hint {
          text-align: center;
          font-size: 11px;
          color: var(--secondary-text-color);
          margin-top: 12px;
          opacity: 0.7;
        }
      </style>
      
      <div class="quota-card" onclick="this.getRootNode().host.handleCardClick()">
        <div class="quota-header">
          <div>
            <div class="service-type">${serviceType.toUpperCase()} ${subServiceName ? '- ' + subServiceName : ''}</div>
            <div class="api-key">${keyPreview}</div>
          </div>
          <button class="refresh-button" onclick="event.stopPropagation(); this.getRootNode().host.handleRefresh(event)" title="Refresh data">
            🔄
          </button>
        </div>
        
        <div class="quota-main">
          <div class="quota-info-row">
            <div class="spending-display">${quotaDisplay || ''}</div>
            <div class="percentage-display">${percentage}%</div>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${percentage}%"></div>
          </div>
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
        
        <div class="card-hint">Tap card to view history</div>
      </div>
    `;
  }

  getCardSize() {
    return 4;
  }
}

const CARD_TAG = 'ai-quota-summary-card';
const ExistingCard = customElements.get(CARD_TAG);

if (!ExistingCard) {
  customElements.define(CARD_TAG, AIQuotaSummaryCard);
} else {
  // Upgrade existing tag in-place (keeps old tag, updates behavior)
  ExistingCard.prototype.setConfig = AIQuotaSummaryCard.prototype.setConfig;
  const hassDescriptor = Object.getOwnPropertyDescriptor(AIQuotaSummaryCard.prototype, 'hass');
  if (hassDescriptor) {
    Object.defineProperty(ExistingCard.prototype, 'hass', hassDescriptor);
  }
  ExistingCard.prototype.getCardSize = AIQuotaSummaryCard.prototype.getCardSize;
}

// Register the card with Home Assistant
window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === CARD_TAG)) {
  window.customCards.push({
    type: CARD_TAG,
    name: 'AI Quota Summary Card',
    description: 'Display AI quota information for Trouter and 9Router with history',
    preview: true,
  });
}
