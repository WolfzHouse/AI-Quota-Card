class AIQuotaStandaloneCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._data = null;
    this._updateInterval = null;
  }

  setConfig(config) {
    if (!config.provider) {
      throw new Error('You need to define a provider');
    }
    if (!config.api_key) {
      throw new Error('You need to define an api_key');
    }
    
    this._config = {
      provider: config.provider,
      api_key: config.api_key,
      auth_index: config.auth_index || '0',
      data_source: config.data_source || 'cliproxy',
      proxy_url: config.proxy_url || 'https://api.openai-proxy.live',
      account_name: config.account_name || '',
      update_interval: config.update_interval || 300, // 5 minutes default
    };
    
    this._fetchData();
    this._startAutoUpdate();
  }

  _startAutoUpdate() {
    if (this._updateInterval) {
      clearInterval(this._updateInterval);
    }
    this._updateInterval = setInterval(() => {
      this._fetchData();
    }, this._config.update_interval * 1000);
  }

  disconnectedCallback() {
    if (this._updateInterval) {
      clearInterval(this._updateInterval);
    }
  }

  async _fetchData() {
    try {
      const { data_source, provider, auth_index, api_key, proxy_url } = this._config;

      let url, headers, options;

      if (data_source === 'cliproxy') {
        // CLIProxy API
        url = `${proxy_url}/dashboard/billing/usage?provider=${provider}&auth=${auth_index}`;
        headers = {
          'Authorization': `Bearer ${api_key}`,
          'Content-Type': 'application/json'
        };
      } else if (data_source === 'trouter') {
        // Trouter.click API - use Home Assistant proxy to bypass CORS
        url = `https://trouter.click/api/proxy/me?view=dashboard`;
        headers = {
          'Authorization': `Bearer ${api_key}`,
          'Accept': '*/*',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        };
      } else if (data_source === '9router') {
        // 9Router API - use Home Assistant proxy to bypass CORS
        url = `https://9router.com/api/proxy/me?view=dashboard`;
        headers = {
          'Authorization': `Bearer ${api_key}`,
          'Accept': '*/*',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        };
      }

      // Use Home Assistant's fetch to bypass CORS
      options = {
        method: 'GET',
        headers: headers,
        mode: 'cors',
        credentials: 'omit'
      };

      const response = await fetch(url, options);

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`API Error: ${response.status} - ${text.substring(0, 100)}`);
      }

      const data = await response.json();
      this._data = this._parseData(data, data_source);
      this._render();
    } catch (error) {
      console.error('Error fetching quota data:', error);
      this._data = { error: error.message };
      this._render();
    }
  }

  _parseData(data, dataSource) {
    const parsed = {
      percentage: 0,
      used: 0,
      total: 0,
      currency: 'USD',
      expires_at: null,
      reset_at: null,
      daily_spent: 0,
      total_spent: 0,
    };

    try {
      if (dataSource === 'cliproxy') {
        // CLIProxy format
        parsed.used = data.total_usage || 0;
        parsed.total = data.total_granted || 100;
        parsed.percentage = parsed.total > 0 ? (parsed.used / parsed.total) * 100 : 0;
        parsed.expires_at = data.access_until ? new Date(data.access_until * 1000) : null;
        parsed.reset_at = data.reset_time ? new Date(data.reset_time * 1000) : null;
        parsed.daily_spent = data.daily_cost || 0;
        parsed.total_spent = data.total_usage || 0;
      } else if (dataSource === 'trouter' || dataSource === '9router') {
        // Trouter/9Router format
        const quota = data.quota || {};
        const usage = data.usage || {};
        const timestamps = data.timestamps || {};

        if (quota.type === 'duration') {
          // Duration-based quota (in seconds)
          const dailyQuota = parseFloat(quota.daily_quota || 0);
          const dailyRemaining = parseFloat(quota.daily_remaining || 0);
          const dailySpent = parseFloat(quota.daily_spent || 0);

          parsed.total = dailyQuota / 3600; // Convert to hours
          parsed.used = dailySpent / 3600;
          parsed.percentage = dailyQuota > 0 ? (dailyRemaining / dailyQuota) * 100 : 0;
          parsed.daily_spent = dailySpent / 3600;
          parsed.total_spent = parsed.used;
          parsed.currency = 'hours';
          parsed.reset_at = quota.next_reset_at ? new Date(quota.next_reset_at) : null;
        } else if (quota.type === 'usd') {
          // USD-based quota
          const totalQuota = parseFloat(quota.total_quota || 0);
          const totalRemaining = parseFloat(quota.total_remaining || 0);
          const totalSpent = parseFloat(quota.total_spent || 0);
          const dailySpent = parseFloat(quota.daily_spent || 0);

          parsed.total = totalQuota;
          parsed.used = totalSpent;
          parsed.percentage = totalQuota > 0 ? (totalRemaining / totalQuota) * 100 : 0;
          parsed.daily_spent = dailySpent;
          parsed.total_spent = totalSpent;
          parsed.currency = 'USD';
          parsed.reset_at = quota.next_reset_at ? new Date(quota.next_reset_at) : null;
        }

        // Parse timestamps
        if (timestamps.expires_at) {
          parsed.expires_at = new Date(timestamps.expires_at);
        }
      }
    } catch (error) {
      console.error('Error parsing data:', error);
    }

    return parsed;
  }

  _formatDate(date) {
    if (!date) return 'N/A';
    const now = new Date();
    const diff = date - now;
    
    if (diff < 0) return 'Expired';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    return `${hours}h`;
  }

  _maskApiKey(key) {
    if (!key || key.length < 8) return '****';
    return key.substring(0, 4) + '****' + key.substring(key.length - 4);
  }

  _getPercentageColor(percentage) {
    if (percentage >= 90) return '#f44336'; // red
    if (percentage >= 70) return '#ff9800'; // orange
    if (percentage >= 50) return '#ffc107'; // amber
    return '#4caf50'; // green
  }

  _render() {
    const { provider, api_key, account_name } = this._config;
    const data = this._data;

    if (!data) {
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div class="card-content">
            <div class="loading">Loading...</div>
          </div>
        </ha-card>
      `;
      return;
    }

    if (data.error) {
      this.shadowRoot.innerHTML = `
        <style>
          .error { color: #f44336; padding: 16px; }
        </style>
        <ha-card>
          <div class="card-content">
            <div class="error">Error: ${data.error}</div>
          </div>
        </ha-card>
      `;
      return;
    }

    const percentageColor = this._getPercentageColor(data.percentage);
    const maskedKey = this._maskApiKey(api_key);

    this.shadowRoot.innerHTML = `
      <style>
        ha-card {
          padding: 16px;
        }
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          padding-bottom: 8px;
          border-bottom: 1px solid var(--divider-color);
        }
        .provider-name {
          font-size: 1.2em;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .api-key {
          font-size: 0.9em;
          color: var(--secondary-text-color);
          font-family: monospace;
        }
        .quota-section {
          margin: 16px 0;
        }
        .percentage-container {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }
        .percentage-circle {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5em;
          font-weight: bold;
          color: white;
          background: ${percentageColor};
        }
        .usage-info {
          flex: 1;
        }
        .usage-amount {
          font-size: 1.3em;
          font-weight: 500;
          color: var(--primary-text-color);
          margin-bottom: 4px;
        }
        .usage-label {
          font-size: 0.9em;
          color: var(--secondary-text-color);
        }
        .info-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-top: 16px;
        }
        .info-item {
          padding: 8px;
          background: var(--secondary-background-color);
          border-radius: 8px;
        }
        .info-label {
          font-size: 0.85em;
          color: var(--secondary-text-color);
          margin-bottom: 4px;
        }
        .info-value {
          font-size: 1em;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .account-name {
          font-size: 0.9em;
          color: var(--secondary-text-color);
          margin-top: 8px;
          font-style: italic;
        }
        .loading {
          text-align: center;
          padding: 20px;
          color: var(--secondary-text-color);
        }
      </style>
      <ha-card>
        <div class="card-content">
          <div class="card-header">
            <div>
              <div class="provider-name">${provider}</div>
              ${account_name ? `<div class="account-name">${account_name}</div>` : ''}
            </div>
            <div class="api-key">${maskedKey}</div>
          </div>
          
          <div class="quota-section">
            <div class="percentage-container">
              <div class="percentage-circle">
                ${data.percentage.toFixed(0)}%
              </div>
              <div class="usage-info">
                <div class="usage-amount">
                  ${data.currency === 'hours'
                    ? `${data.used.toFixed(2)}h / ${data.total.toFixed(2)}h`
                    : `$${data.used.toFixed(2)} / $${data.total.toFixed(2)}`
                  }
                </div>
                <div class="usage-label">Quota Usage</div>
              </div>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">Expires in</div>
              <div class="info-value">${this._formatDate(data.expires_at)}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Reset at</div>
              <div class="info-value">${this._formatDate(data.reset_at)}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Daily Spent</div>
              <div class="info-value">${data.currency === 'hours'
                ? `${data.daily_spent.toFixed(2)}h`
                : `$${data.daily_spent.toFixed(2)}`
              }</div>
            </div>
            <div class="info-item">
              <div class="info-label">Total Spent</div>
              <div class="info-value">${data.currency === 'hours'
                ? `${data.total_spent.toFixed(2)}h`
                : `$${data.total_spent.toFixed(2)}`
              }</div>
            </div>
          </div>
        </div>
      </ha-card>
    `;
  }

  getCardSize() {
    return 4;
  }

  static getConfigElement() {
    return document.createElement("ai-quota-standalone-card-editor");
  }

  static getStubConfig() {
    return {
      provider: "openai",
      api_key: "",
      auth_index: "0",
      data_source: "cliproxy",
      proxy_url: "https://api.openai-proxy.live",
      account_name: "",
      update_interval: 300
    };
  }
}

customElements.define('ai-quota-standalone-card', AIQuotaStandaloneCard);

// Register the card
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'ai-quota-standalone-card',
  name: 'AI Quota Standalone Card',
  description: 'Display AI API quota information without backend integration',
  preview: true,
});

console.info(
  '%c AI-QUOTA-STANDALONE-CARD %c Standalone card loaded ',
  'color: white; background: #2196F3; font-weight: 700;',
  'color: #2196F3; background: white; font-weight: 700;'
);
