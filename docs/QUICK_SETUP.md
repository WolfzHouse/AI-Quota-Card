# AI Quota Integration - Quick Setup Guide

> **Historical — describes the v1.1.0 config flow** (provider name + auth index +
> CLIProxy token). The 2.0.x integration no longer works this way, so read this as a
> record of how setup used to look rather than as instructions. API keys shown are
> placeholders.

## 🎯 What's New?

The integration now supports **3 data sources** for collecting AI quota information:

1. **CLIProxy** - Proxy-based collection (original method)
2. **Trouter.click** - Direct API integration
3. **9Router** - Direct API integration

---

## 🚀 Quick Setup

### Step 1: Choose Your Data Source

When adding the integration, you'll now see a **Data Source** dropdown at the top:

```
┌─────────────────────────────────────────┐
│ Data Source *                           │
│ ┌─────────────────────────────────────┐ │
│ │ CLIProxy                        ▼   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Provider Name *                         │
│ ┌─────────────────────────────────────┐ │
│ │ Antigravity                     ▼   │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Step 2: Fill in the Required Fields

**For CLIProxy:**
- ✅ Data Source: CLIProxy
- ✅ Provider Name: (Select your provider)
- ✅ Auth Index: 0
- ✅ CLIProxy API Token: (Your proxy token)
- ⚪ Trouter/9Router API Key: (Leave empty)

**For Trouter.click:**
- ✅ Data Source: Trouter.click
- ✅ Provider Name: Trouter
- ✅ Auth Index: 0
- ⚪ CLIProxy API Token: (Leave empty)
- ✅ Trouter/9Router API Key: (Your Trouter API key)

**For 9Router:**
- ✅ Data Source: 9Router
- ✅ Provider Name: Trouter
- ✅ Auth Index: 0
- ⚪ CLIProxy API Token: (Leave empty)
- ✅ Trouter/9Router API Key: (Your 9Router API key)

---

## 📊 Integration Title Format

The integration will be named based on your selections:

```
[Data Source] - [Provider] (Auth: [Index])
```

**Examples:**
- `CLIProxy - Claude (Anthropic) (Auth: 0)`
- `Trouter.click - Trouter (Auth: 0)`
- `9Router - Trouter (Auth: 0)`

---

## 🔑 Finding Your API Keys

### CLIProxy Token
1. Access your CLIProxyAPI management interface
2. Generate or copy your management token
3. Use it in the "CLIProxy API Token" field

### Trouter.click API Key
1. Open https://trouter.click/dashboard
2. Press F12 to open DevTools
3. Go to Network tab
4. Refresh the page
5. Find the request to `/api/proxy/me?view=dashboard`
6. Copy the Bearer token from Authorization header
7. Format: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

### 9Router API Key
1. Open https://9router.com/dashboard
2. Follow the same steps as Trouter.click
3. Copy the Bearer token from the API request

---

## 📈 What Data You'll Get

### CLIProxy Data Source
Depends on the provider you select:
- **Claude**: 5-hour limit, 7-day limit, per-model weekly limits (Fable / Opus / Sonnet), Extra usage
- **Codex**: 5-hour limit, Weekly limit
- **Gemini CLI**: Model-specific quotas
- **Antigravity**: Model quotas by group
- **Kiro/Copilot**: Usage quotas

### Trouter.click / 9Router Data Sources
Always provides:
1. ⏱️ **Daily Duration Quota** - Time remaining
2. 💰 **Lifetime Spend** - Total spending
3. 💵 **Daily Spend** - Today's spending
4. 📊 **Total Requests** - Request statistics
5. 🔢 **Token Usage** - Token consumption
6. 🔑 **API Key Status** - Key validity
7. 📦 **Service Type** - Your plan

For 9Router Claude connections the quota rows mirror 9Router's own Quota Tracker,
in this order: **Session (5h)**, **Weekly (7d)**, **Weekly Fable (7d)**,
**Weekly Opus (7d)**, **Weekly Sonnet (7d)**.

---

## 🔄 Migration Between Data Sources

You can have multiple integrations running simultaneously:

```
✅ CLIProxy - Claude (Auth: 0)
✅ Trouter.click - Trouter (Auth: 0)
✅ 9Router - Trouter (Auth: 0)
```

Each will create its own set of sensors with unique IDs.

---

## ⚙️ Configuration Fields Reference

| Field | CLIProxy | Trouter.click | 9Router | Description |
|-------|----------|---------------|---------|-------------|
| **Data Source** | Required | Required | Required | Where to fetch data from |
| **Provider Name** | Required | Required | Required | AI provider to monitor |
| **Auth Index** | Required | Optional | Optional | Auth file index (usually 0) |
| **CLIProxy API Token** | Required | Not used | Not used | Your proxy token |
| **Trouter/9Router API Key** | Not used | Required | Required | Your API key |
| **Account Name** | Optional | Optional | Optional | Friendly name |
| **CLIProxy API URL** | Optional | Not used | Not used | Custom proxy URL |

---

## 🛠️ Troubleshooting

### "Data source is required"
- Make sure you selected a data source from the dropdown

### "API key is required"
- For Trouter/9Router: Fill in the "Trouter/9Router API Key" field
- For CLIProxy: Fill in the "CLIProxy API Token" field

### "HTTP error 404"
- CLIProxy: Check your proxy URL
- Trouter/9Router: Verify the API endpoint is accessible

### Sensors not updating
- Check Home Assistant logs
- Verify your API keys are valid
- Wait 15 minutes for the next update cycle

---

## 📝 Example Configurations

### Example 1: Monitor Claude via CLIProxy
```yaml
Data Source: CLIProxy
Provider Name: Claude (Anthropic)
Auth Index: 0
CLIProxy API Token: sk-cliproxy-xxxxxxxxxxxxx
Account Name: My Claude Pro
CLIProxy API URL: https://ai.wolfz.shop/v0/management/api-call
```

### Example 2: Monitor Trouter Usage
```yaml
Data Source: Trouter.click
Provider Name: Trouter
Auth Index: 0
Trouter/9Router API Key: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Account Name: Trouter Claude Account
```

### Example 3: Monitor 9Router Usage
```yaml
Data Source: 9Router
Provider Name: Trouter
Auth Index: 0
Trouter/9Router API Key: XXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Account Name: 9Router Main
```

---

## 🎉 You're All Set!

After configuration:
1. ✅ Integration will appear in Devices & Services
2. ✅ Sensors will be created automatically
3. ✅ Data updates every 15 minutes
4. ✅ View your quota in Home Assistant dashboard

---

## 📚 Additional Resources

- **Full Documentation**: See `DATA_SOURCES.md`
- **Trouter Setup**: See `TROUTER_SETUP.md`
- **Home Assistant Logs**: Settings → System → Logs
- **Integration Settings**: Settings → Devices & Services → AI Web Quota
