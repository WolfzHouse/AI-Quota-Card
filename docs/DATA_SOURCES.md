# AI Quota Integration - Data Sources

> **Historical — describes the v1.1.0 config flow** (provider name + auth index +
> CLIProxy token). The 2.0.x integration no longer works this way, so read this as a
> record of how setup used to look rather than as instructions. API keys shown are
> placeholders.

## Overview

The AI Quota integration now supports multiple data sources for collecting quota information. Each data source has its own authentication method and API endpoints.

## Available Data Sources

### 1. CLIProxy (Default)
**Description**: Uses CLIProxyAPI as a proxy to fetch quota data from various AI providers.

**Use Cases**:
- When you have OAuth tokens stored in CLIProxyAPI
- For providers: Antigravity, Claude, Codex, Gemini CLI, Kiro, Copilot
- When you want centralized token management

**Required Fields**:
- **Data Source**: Select "CLIProxy"
- **Provider Name**: Select your AI provider (Antigravity, Claude, Codex, etc.)
- **Auth Index**: The auth file index (usually "0")
- **CLIProxy API Token**: Your CLIProxyAPI management token
- **CLIProxy API URL**: Default is `https://ai.wolfz.shop/v0/management/api-call`

**How It Works**:
1. Integration sends a request to CLIProxyAPI
2. CLIProxyAPI uses your stored OAuth tokens to fetch quota data
3. Data is returned and parsed by the integration

---

### 2. Trouter.click
**Description**: Direct API integration with Trouter.click for real-time quota monitoring.

**Use Cases**:
- When you have a Trouter.click account
- For monitoring Claude API usage through Trouter
- Direct API access without proxy

**Required Fields**:
- **Data Source**: Select "Trouter.click"
- **Provider Name**: Select "Trouter"
- **Auth Index**: Enter "0" (not used but required)
- **Trouter/9Router API Key**: Your Trouter API key (Bearer token)
- **Account Name**: (Optional) Friendly name for your account

**How It Works**:
1. Integration makes direct API call to `https://trouter.click/api/proxy/me?view=dashboard`
2. Uses your Bearer token for authentication
3. Returns quota, usage, and spending data

**Finding Your API Key**:
1. Open browser DevTools (F12) on trouter.click/dashboard
2. Go to Network tab
3. Look for the request to `/api/proxy/me?view=dashboard`
4. Copy the Bearer token from the Authorization header

---

### 3. 9Router
**Description**: Direct API integration with 9Router for quota monitoring.

**Use Cases**:
- When you have a 9Router account
- For monitoring AI API usage through 9Router
- Direct API access without proxy

**Required Fields**:
- **Data Source**: Select "9Router"
- **Provider Name**: Select your provider
- **Auth Index**: Enter "0" (not used but required)
- **Trouter/9Router API Key**: Your 9Router API key (Bearer token)
- **Account Name**: (Optional) Friendly name for your account

**How It Works**:
1. Integration makes direct API call to `https://9router.com/api/proxy/me?view=dashboard`
2. Uses your Bearer token for authentication
3. Returns quota, usage, and spending data

**Note**: 9Router uses the same API structure as Trouter.click

---

## Configuration Examples

### Example 1: CLIProxy with Claude
```
Data Source: CLIProxy
Provider Name: Claude (Anthropic)
Auth Index: 0
CLIProxy API Token: your-cliproxy-token-here
Account Name: My Claude Account
CLIProxy API URL: https://ai.wolfz.shop/v0/management/api-call
```

### Example 2: Trouter.click
```
Data Source: Trouter.click
Provider Name: Trouter
Auth Index: 0
Trouter/9Router API Key: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Account Name: Trouter Claude
```

### Example 3: 9Router
```
Data Source: 9Router
Provider Name: Trouter
Auth Index: 0
Trouter/9Router API Key: your-9router-api-key-here
Account Name: 9Router Account
```

---

## Comparison Table

| Feature | CLIProxy | Trouter.click | 9Router |
|---------|----------|---------------|---------|
| **Authentication** | Proxy Token | Direct API Key | Direct API Key |
| **Providers Supported** | Multiple | Trouter only | Multiple |
| **Token Management** | Centralized | Direct | Direct |
| **Setup Complexity** | Medium | Easy | Easy |
| **Update Frequency** | 15 minutes | 15 minutes | 15 minutes |
| **Requires Proxy** | Yes | No | No |

---

## Choosing the Right Data Source

### Use CLIProxy when:
- ✅ You already have CLIProxyAPI set up
- ✅ You want to monitor multiple providers from one place
- ✅ You prefer centralized OAuth token management
- ✅ You're using providers like Claude, Codex, Gemini CLI, etc.

### Use Trouter.click when:
- ✅ You have a Trouter.click account
- ✅ You want direct API access without a proxy
- ✅ You need real-time quota monitoring for Claude through Trouter
- ✅ You want detailed spending and token usage statistics

### Use 9Router when:
- ✅ You have a 9Router account
- ✅ You want direct API access without a proxy
- ✅ You need quota monitoring through 9Router's infrastructure

---

## Sensors Created

### CLIProxy Data Source
Creates sensors based on the selected provider:
- Quota percentages for each model/limit
- Reset times
- Usage statistics (provider-dependent)

### Trouter.click / 9Router Data Sources
Creates the following sensors:
1. **Daily Duration Quota** - Time-based quota remaining
2. **Lifetime Spend** - Total spending
3. **Daily Spend** - Today's spending
4. **Total Requests** - Request count statistics
5. **Token Usage** - Token consumption breakdown
6. **API Key Status** - Key validity and expiration
7. **Service Type** - Your service plan

---

## Troubleshooting

### CLIProxy Issues
- **Error: "HTTP error 404"**: Check your CLIProxy API URL and token
- **Error: "Invalid authentication"**: Verify your proxy token is correct
- **No data**: Ensure your OAuth tokens are stored in CLIProxyAPI

### Trouter.click / 9Router Issues
- **Error: "API key is required"**: Fill in the Trouter/9Router API Key field
- **Error: "API error 401"**: Your API key is invalid or expired
- **Error: "API error 404"**: The API endpoint might have changed
- **No data**: Verify your API key is active on the dashboard

---

## Migration Guide

### From CLIProxy to Trouter.click
1. Get your Trouter API key from the dashboard
2. Add a new integration instance
3. Select "Trouter.click" as data source
4. Enter your API key
5. Remove the old CLIProxy integration if no longer needed

### From Trouter.click to CLIProxy
1. Set up CLIProxyAPI with your OAuth tokens
2. Add a new integration instance
3. Select "CLIProxy" as data source
4. Enter your proxy token
5. Remove the old Trouter integration if no longer needed

---

## Security Notes

- **CLIProxy**: Your proxy token has access to all stored OAuth tokens
- **Trouter.click / 9Router**: Your API key is stored securely in Home Assistant
- All API keys are encrypted in Home Assistant's configuration
- Never share your API keys or tokens publicly
- Regularly rotate your API keys for security

---

## Support

For issues or questions:
1. Check Home Assistant logs: Settings → System → Logs
2. Look for entries containing "AI Quota"
3. Verify your data source configuration
4. Ensure your API keys/tokens are valid and active
