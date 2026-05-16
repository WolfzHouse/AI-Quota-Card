# AI Quota Standalone Card

A completely self-contained Lovelace card that displays AI API quota information **without requiring the backend integration**. This card makes API calls directly from the frontend and works independently.

## Features

- ✅ **No Backend Required** - Works without installing the custom component
- ✅ **Direct API Calls** - Fetches data directly from CLIProxy, Trouter.click, or 9Router
- ✅ **Auto-Updates** - Configurable refresh interval
- ✅ **Beautiful UI** - Color-coded percentage display, masked API keys
- ✅ **Multiple Data Sources** - Supports CLIProxy, Trouter.click, and 9Router

## Installation

### Method 1: Manual Installation

1. Download `ai-quota-standalone-card.js`
2. Copy it to your `www` folder in Home Assistant: `/config/www/ai-quota-standalone-card.js`
3. Add the resource in your Lovelace dashboard:
   - Go to Settings → Dashboards → Resources
   - Click "Add Resource"
   - URL: `/local/ai-quota-standalone-card.js`
   - Resource type: JavaScript Module

### Method 2: HACS (if you have the integration installed)

The card is automatically registered when you install the AI Quota Integration via HACS.

## Configuration

### Basic Configuration

```yaml
type: custom:ai-quota-standalone-card
provider: openai
api_key: sk-xxxxxxxxxxxxxxxxxxxxx
auth_index: "0"
data_source: cliproxy
```

### Full Configuration Options

```yaml
type: custom:ai-quota-standalone-card
provider: openai                              # Required: Provider name (openai, anthropic, gemini, etc.)
api_key: sk-xxxxxxxxxxxxxxxxxxxxx             # Required: Your API key
auth_index: "0"                               # Optional: Auth index or file ID (default: "0")
data_source: cliproxy                         # Optional: cliproxy, trouter, or 9router (default: cliproxy)
proxy_url: https://api.openai-proxy.live      # Optional: CLIProxy URL (default: https://api.openai-proxy.live)
account_name: My OpenAI Account               # Optional: Display name for the account
update_interval: 300                          # Optional: Update interval in seconds (default: 300 = 5 minutes)
```

## Configuration Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `provider` | Yes | - | Provider name (e.g., openai, anthropic, gemini) |
| `api_key` | Yes | - | Your API key for authentication |
| `auth_index` | No | "0" | Auth index or file ID |
| `data_source` | No | cliproxy | Data source: `cliproxy`, `trouter`, or `9router` |
| `proxy_url` | No | https://api.openai-proxy.live | CLIProxy API URL (only used when data_source is cliproxy) |
| `account_name` | No | - | Optional display name for the account |
| `update_interval` | No | 300 | Auto-update interval in seconds |

## Examples

### Example 1: CLIProxy (Default)

```yaml
type: custom:ai-quota-standalone-card
provider: openai
api_key: sk-proj-xxxxxxxxxxxxxxxxxxxxx
auth_index: "0"
account_name: Production OpenAI
```

### Example 2: Trouter.click

```yaml
type: custom:ai-quota-standalone-card
provider: trouter
api_key: your-trouter-api-key
auth_index: "0"
data_source: trouter
account_name: Trouter Account
```

### Example 3: 9Router

```yaml
type: custom:ai-quota-standalone-card
provider: openai
api_key: your-9router-api-key
auth_index: "0"
data_source: 9router
update_interval: 600
```

### Example 4: Multiple Cards for Different Accounts

```yaml
type: vertical-stack
cards:
  - type: custom:ai-quota-standalone-card
    provider: openai
    api_key: sk-proj-account1-xxxxx
    auth_index: "0"
    account_name: Personal Account
    
  - type: custom:ai-quota-standalone-card
    provider: openai
    api_key: sk-proj-account2-xxxxx
    auth_index: "0"
    account_name: Work Account
    
  - type: custom:ai-quota-standalone-card
    provider: anthropic
    api_key: sk-ant-xxxxx
    auth_index: "0"
    account_name: Claude API
```

## What the Card Displays

- **Provider Name** - The API provider (OpenAI, Anthropic, etc.)
- **API Key** - Masked for security (shows first 4 and last 4 characters)
- **Account Name** - Optional custom name for the account
- **Percentage Circle** - Color-coded usage percentage:
  - 🟢 Green: 0-49%
  - 🟡 Amber: 50-69%
  - 🟠 Orange: 70-89%
  - 🔴 Red: 90-100%
- **Usage Amount** - Current usage vs total quota in USD
- **Expires in** - Time until quota expires
- **Reset at** - Time until quota resets
- **Daily Spent** - Amount spent today
- **Total Spent** - Total amount spent

## Comparison: Standalone Card vs Integration

| Feature | Standalone Card | With Integration |
|---------|----------------|------------------|
| Installation | Just add JS file | Install custom component |
| Configuration | In card YAML | In HA integration UI |
| Sensors | No sensors created | Creates individual sensors |
| Automations | Not possible | Can trigger automations |
| History | No history tracking | Full history in HA |
| API Calls | From browser | From HA server |
| Updates | Manual refresh interval | Coordinator-based |
| Best For | Quick setup, simple display | Advanced use, automations |

## Troubleshooting

### Card Not Showing

1. Check that the resource is added correctly in Lovelace resources
2. Clear browser cache (Ctrl+F5)
3. Check browser console for errors (F12)

### "Error: You need to define a provider"

Make sure you have `provider` in your card configuration.

### "Error: You need to define an api_key"

Make sure you have `api_key` in your card configuration.

### API Error Messages

- **401 Unauthorized** - Check your API key is correct
- **404 Not Found** - Check provider name and auth_index
- **CORS Error** - The API endpoint may not allow browser requests

### Data Not Updating

- Check the `update_interval` setting
- Verify your API key is still valid
- Check browser console for error messages

## Security Notes

⚠️ **Important Security Considerations:**

1. **API Key Exposure**: The API key is stored in your Lovelace configuration and sent from your browser. While it's masked in the UI, it's visible in the YAML configuration.

2. **Browser-Based Requests**: API calls are made directly from your browser, which means:
   - Your API key is exposed in browser network requests
   - CORS policies may block some API endpoints
   - API usage is tied to your browser session

3. **Recommendations**:
   - Use read-only or limited-scope API keys when possible
   - Consider using the full integration (with backend) for production use
   - Monitor your API usage regularly
   - Don't share your Lovelace configuration publicly

## Support

For issues, questions, or feature requests, please check:
- The main integration documentation
- Home Assistant community forums
- GitHub issues (if available)

## License

This card is part of the AI Quota Integration project.
