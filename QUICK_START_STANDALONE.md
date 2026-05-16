# Quick Start: Standalone Card (No Backend)

This is the **fastest way** to get AI quota monitoring in Home Assistant - no integration setup required!

## 3-Step Setup

### Step 1: Add the Card File

Copy `ai-quota-standalone-card.js` to your Home Assistant:

```
/config/www/ai-quota-standalone-card.js
```

### Step 2: Register the Resource

1. Go to **Settings** → **Dashboards** → **Resources** (top right menu)
2. Click **"+ Add Resource"**
3. Enter:
   - **URL**: `/local/ai-quota-standalone-card.js`
   - **Resource type**: `JavaScript Module`
4. Click **Create**

### Step 3: Add the Card

Edit your dashboard and add this YAML:

```yaml
type: custom:ai-quota-standalone-card
provider: openai
api_key: YOUR_API_KEY_HERE
auth_index: "0"
data_source: cliproxy
account_name: My OpenAI Account
```

**That's it!** The card will start fetching and displaying your quota data.

## Common Configurations

### For CLIProxy Users

```yaml
type: custom:ai-quota-standalone-card
provider: openai
api_key: sk-proj-xxxxxxxxxxxxxxxxxxxxx
auth_index: "0"
data_source: cliproxy
proxy_url: https://api.openai-proxy.live
```

### For Trouter.click Users

```yaml
type: custom:ai-quota-standalone-card
provider: trouter
api_key: your-trouter-api-key
auth_index: "0"
data_source: trouter
```

### For 9Router Users

```yaml
type: custom:ai-quota-standalone-card
provider: openai
api_key: your-9router-api-key
auth_index: "0"
data_source: 9router
```

## Multiple Accounts

Want to monitor multiple accounts? Just add multiple cards:

```yaml
type: vertical-stack
cards:
  - type: custom:ai-quota-standalone-card
    provider: openai
    api_key: sk-proj-account1-xxxxx
    account_name: Personal
    
  - type: custom:ai-quota-standalone-card
    provider: anthropic
    api_key: sk-ant-xxxxx
    account_name: Claude
```

## Troubleshooting

**Card not showing?**
- Clear browser cache (Ctrl+F5)
- Check the resource was added correctly
- Look for errors in browser console (F12)

**"You need to define a provider" error?**
- Make sure you have both `provider` and `api_key` in your config

**Data not loading?**
- Verify your API key is correct
- Check the `data_source` matches your API provider
- Look for error messages in the card

## Next Steps

- Adjust `update_interval` to control refresh frequency (default: 300 seconds)
- Add `account_name` to label different accounts
- Check the full [STANDALONE_CARD_GUIDE.md](STANDALONE_CARD_GUIDE.md) for all options

## Need More Features?

If you need:
- Historical data tracking
- Automations based on quota
- Multiple sensors
- Server-side API calls

Consider installing the **full AI Quota Integration** instead. See the main README for details.
