# Visual Configuration Guide

> **Historical — describes the v1.1.0 config flow** (provider name + auth index +
> CLIProxy token). The 2.0.x integration no longer works this way, so read this as a
> record of how setup used to look rather than as instructions. API keys shown are
> placeholders.

## 🎨 New Configuration Flow

### Step 1: Add Integration
```
Settings → Devices & Services → Add Integration
Search: "AI Web Quota"
```

### Step 2: Configuration Form

```
╔═══════════════════════════════════════════════════════════╗
║  Add AI Web Quota Integration                        [?] [X]║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  Configure the data source, provider, and authentication  ║
║  parameters.                                              ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Data Source *                                       │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │ CLIProxy                                    ▼   │ │ ║
║  │ │ ├─ CLIProxy                                     │ │ ║
║  │ │ ├─ Trouter.click                                │ │ ║
║  │ │ └─ 9Router                                      │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Provider Name *                                     │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │ Antigravity                                 ▼   │ │ ║
║  │ │ ├─ Antigravity                                  │ │ ║
║  │ │ ├─ Claude (Anthropic)                           │ │ ║
║  │ │ ├─ Codex (OpenAI)                               │ │ ║
║  │ │ ├─ Gemini CLI                                   │ │ ║
║  │ │ ├─ Kiro (CodeWhisperer)                         │ │ ║
║  │ │ ├─ GitHub Copilot                               │ │ ║
║  │ │ └─ Trouter                                      │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Auth Index / File ID *                              │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │ 0                                               │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ CLIProxy API Token                              [👁] │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │ ••••••••••••••••••••••••••••••••••••••••••••••  │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Trouter/9Router API Key                         [👁] │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │                                                 │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Account Email or Alias (Optional)                   │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │                                                 │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ CLIProxy API URL                                    │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │ https://ai.wolfz.shop/v0/management/api-call   │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║                                          ┌──────────────┐ ║
║                                          │   Submit     │ ║
║                                          └──────────────┘ ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 📝 Configuration Examples

### Example 1: CLIProxy with Claude

```
╔═══════════════════════════════════════════════════════════╗
║  Data Source: CLIProxy                                     ║
║  Provider Name: Claude (Anthropic)                         ║
║  Auth Index: 0                                             ║
║  CLIProxy API Token: sk-cliproxy-xxxxxxxxxxxxx             ║
║  Trouter/9Router API Key: [empty]                          ║
║  Account Name: My Claude Pro Account                       ║
║  CLIProxy API URL: https://ai.wolfz.shop/v0/management/...║
╚═══════════════════════════════════════════════════════════╝

Result: "CLIProxy - Claude (Anthropic) (Auth: 0)"
```

### Example 2: Trouter.click

```
╔═══════════════════════════════════════════════════════════╗
║  Data Source: Trouter.click                                ║
║  Provider Name: Trouter                                    ║
║  Auth Index: 0                                             ║
║  CLIProxy API Token: [empty]                               ║
║  Trouter/9Router API Key: XXXXXXXX-XXXX-XXXX-XXXX-XXXX...  ║
║  Account Name: Trouter Claude Account                      ║
║  CLIProxy API URL: https://ai.wolfz.shop/v0/management/...║
╚═══════════════════════════════════════════════════════════╝

Result: "Trouter.click - Trouter (Auth: 0)"
```

### Example 3: 9Router

```
╔═══════════════════════════════════════════════════════════╗
║  Data Source: 9Router                                      ║
║  Provider Name: Trouter                                    ║
║  Auth Index: 0                                             ║
║  CLIProxy API Token: [empty]                               ║
║  Trouter/9Router API Key: XXXXX-XXXX-XXXX-XXXX-XXXXXXXX   ║
║  Account Name: 9Router Main Account                        ║
║  CLIProxy API URL: https://ai.wolfz.shop/v0/management/...║
╚═══════════════════════════════════════════════════════════╝

Result: "9Router - Trouter (Auth: 0)"
```

---

## 🎯 Field Visibility Logic

### When Data Source = CLIProxy
```
✅ Data Source (Required)
✅ Provider Name (Required)
✅ Auth Index (Required)
✅ CLIProxy API Token (Required - Fill this!)
⚪ Trouter/9Router API Key (Optional - Leave empty)
⚪ Account Name (Optional)
⚪ CLIProxy API URL (Optional)
```

### When Data Source = Trouter.click
```
✅ Data Source (Required)
✅ Provider Name (Required)
⚪ Auth Index (Optional - Usually 0)
⚪ CLIProxy API Token (Optional - Leave empty)
✅ Trouter/9Router API Key (Required - Fill this!)
⚪ Account Name (Optional)
⚪ CLIProxy API URL (Optional - Not used)
```

### When Data Source = 9Router
```
✅ Data Source (Required)
✅ Provider Name (Required)
⚪ Auth Index (Optional - Usually 0)
⚪ CLIProxy API Token (Optional - Leave empty)
✅ Trouter/9Router API Key (Required - Fill this!)
⚪ Account Name (Optional)
⚪ CLIProxy API URL (Optional - Not used)
```

---

## 🔄 Options Flow (Edit Integration)

```
╔═══════════════════════════════════════════════════════════╗
║  Edit AI Web Quota Settings                          [?] [X]║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  Update the data source, tokens, account alias, or proxy  ║
║  URL for this integration.                                ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Data Source                                         │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │ CLIProxy                                    ▼   │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ CLIProxy API Token                              [👁] │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │ ••••••••••••••••••••••••••••••••••••••••••••••  │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Trouter/9Router API Key                         [👁] │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │                                                 │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Account Email or Alias (Optional)                   │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │ My Account                                      │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ CLIProxy API URL                                    │ ║
║  │ ┌─────────────────────────────────────────────────┐ │ ║
║  │ │ https://ai.wolfz.shop/v0/management/api-call   │ │ ║
║  │ └─────────────────────────────────────────────────┘ │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║                                          ┌──────────────┐ ║
║                                          │   Submit     │ ║
║                                          └──────────────┘ ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 📊 Integration List View

After configuration, your integrations will appear like this:

```
╔═══════════════════════════════════════════════════════════╗
║  Devices & Services                                        ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  🔌 AI Web Quota                                           ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ 📊 CLIProxy - Claude (Anthropic) (Auth: 0)          │ ║
║  │    7 entities                                        │ ║
║  │    [Configure] [Options] [Delete]                    │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ 📊 Trouter.click - Trouter (Auth: 0)                │ ║
║  │    7 entities                                        │ ║
║  │    [Configure] [Options] [Delete]                    │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ 📊 9Router - Trouter (Auth: 0)                       │ ║
║  │    7 entities                                        │ ║
║  │    [Configure] [Options] [Delete]                    │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🎨 Sensor Entities

### CLIProxy - Claude Example
```
sensor.cliproxy_claude_5_hour_limit_quota
sensor.cliproxy_claude_7_day_limit_quota
sensor.cliproxy_claude_extra_usage_quota
sensor.cliproxy_claude_extra_usage_reset
```

### Trouter.click Example
```
sensor.trouter_daily_duration_quota
sensor.trouter_lifetime_spend
sensor.trouter_daily_spend
sensor.trouter_total_requests
sensor.trouter_token_usage
sensor.trouter_api_key_status
sensor.trouter_service_type
```

---

## 🎯 Quick Decision Tree

```
Do you have CLIProxyAPI set up?
│
├─ YES → Use CLIProxy data source
│         ├─ Multiple providers supported
│         └─ Centralized token management
│
└─ NO → Do you have Trouter/9Router account?
         │
         ├─ Trouter.click → Use Trouter.click data source
         │                   └─ Direct API access
         │
         └─ 9Router → Use 9Router data source
                      └─ Direct API access
```

---

## ✅ Validation Rules

### Data Source: CLIProxy
```
✓ CLIProxy API Token must not be empty
✓ Provider must be selected
✓ Auth Index must be provided
```

### Data Source: Trouter.click
```
✓ Trouter/9Router API Key must not be empty
✓ Provider must be selected
✓ API Key format: XXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

### Data Source: 9Router
```
✓ Trouter/9Router API Key must not be empty
✓ Provider must be selected
✓ API Key format: XXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

---

## 🎊 Success Indicators

After successful configuration:

```
✅ Integration appears in Devices & Services
✅ Title shows: "[Data Source] - [Provider] (Auth: X)"
✅ Entities are created automatically
✅ First data fetch happens within 15 minutes
✅ Sensors show current quota values
```

---

**Tip:** You can have multiple integrations with different data sources running simultaneously!
