# 🎴 Two Cards Comparison

## You Have 2 Different Cards!

### Card 1: `ai-quota-card.js` (OLD - Original)
**Type**: `custom:ai-quota-card`
**Location**: `ai-quota-card.js` (root folder)

### Card 2: `ai-quota-summary-card.js` (NEW - Summary)
**Type**: `custom:ai-quota-summary-card`
**Location**: `custom_components/ai_quota/www/ai-quota-summary-card.js`

---

## 📊 Feature Comparison

| Feature | OLD Card (`ai-quota-card`) | NEW Card (`ai-quota-summary-card`) |
|---------|---------------------------|-----------------------------------|
| **Purpose** | Detailed quota display with multiple models | Simple summary with key metrics |
| **Data Source** | Can fetch directly OR use backend | Uses backend integration only |
| **Configuration** | Complex (provider, proxy_url, auth_index) | Simple (just entity) |
| **Display** | Shows all models/limits in detail | Shows summary: %, $, expiration |
| **Size** | Large, detailed | Compact, clean |
| **Auto-Install** | ❌ Manual setup required | ✅ Auto-installs with integration |
| **Best For** | Power users who want all details | Quick overview of quota status |

---

## 🎯 OLD Card (`ai-quota-card`)

### Configuration
```yaml
type: custom:ai-quota-card
provider: antigravity
auth_index: 0
backend: true  # Uses integration data
# OR
proxy_url: https://ai.wolfz.shop/v0/management/api-call
proxy_token: YOUR_TOKEN
```

### What It Shows
```
╔═══════════════════════════════════════╗
║ Antigravity (Auth: 0)                 ║
║ Plan: Free                            ║
╠═══════════════════════════════════════╣
║ Gemini Pro                            ║
║   gemini-1.5-pro: 95%                ║
║   gemini-1.5-pro-002: 98%            ║
║                                       ║
║ Gemini Flash                          ║
║   gemini-1.5-flash: 100%             ║
║   gemini-1.5-flash-002: 100%         ║
║                                       ║
║ GPT-4                                 ║
║   gpt-4o: 87%                        ║
║   gpt-4o-mini: 92%                   ║
╚═══════════════════════════════════════╝
```

**Shows**: All individual models with their percentages

---

## ✨ NEW Card (`ai-quota-summary-card`)

### Configuration
```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

### What It Shows
```
╔═══════════════════════════════════╗
║ CLAUDE - CC LITE                  ║
║ Y6VC****0XJV                     ║
╠═══════════════════════════════════╣
║              98%                  ║
║ ████████████████████░░░░         ║
║         $1.31 / $100.00          ║
╠═══════════════════════════════════╣
║ Expires: 28d │ Reset: 2026-05-17║
║ Total: $202  │ Daily: $1.31     ║
╚═══════════════════════════════════╝
```

**Shows**: Summary with key metrics (%, $, expiration)

---

## 🤔 Which One Should You Use?

### Use OLD Card (`ai-quota-card`) When:
- ✅ You want to see ALL models and their individual quotas
- ✅ You're using CLIProxy with multiple providers
- ✅ You need detailed breakdown of each model
- ✅ You want to see Antigravity, Claude, Codex details

**Example**: Monitoring Antigravity with 10+ models

### Use NEW Card (`ai-quota-summary-card`) When:
- ✅ You want a quick overview of quota status
- ✅ You're using Trouter.click or 9Router
- ✅ You want to see spending in USD
- ✅ You want to track expiration dates
- ✅ You want a clean, simple display

**Example**: Monitoring Trouter API key status

---

## 💡 Recommendation

### For Trouter/9Router Users:
**Use NEW Card** (`ai-quota-summary-card`)
- Shows API key, spending, expiration
- Perfect for Trouter's billing model
- Auto-installs with integration

### For CLIProxy Users:
**Use OLD Card** (`ai-quota-card`)
- Shows all provider models
- Detailed quota breakdown
- Better for multiple models

### For Both:
**Use BOTH Cards!**
- OLD card for detailed view
- NEW card for quick summary

---

## 📋 Side-by-Side Example

### Dashboard with BOTH Cards

```yaml
type: vertical-stack
cards:
  # Quick summary at top
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_0
  
  # Detailed view below
  - type: custom:ai-quota-card
    provider: antigravity
    auth_index: 0
    backend: true
```

**Result**:
```
┌─────────────────────────────────┐
│ CLAUDE - CC LITE                │  ← NEW: Quick summary
│ Y6VC****0XJV                   │
│ 98% | $1.31 / $100.00         │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Antigravity (Auth: 0)           │  ← OLD: Detailed view
│ Gemini Pro: 95%                 │
│ Gemini Flash: 100%              │
│ GPT-4: 87%                      │
└─────────────────────────────────┘
```

---

## 🔧 Setup Differences

### OLD Card Setup
```
1. Copy ai-quota-card.js to /config/www/
2. Add resource manually:
   Settings → Dashboards → Resources
   URL: /local/ai-quota-card.js
3. Add card with provider config
```

### NEW Card Setup
```
1. Install integration
2. Restart Home Assistant
3. Card auto-installs!
4. Just add card with entity
```

---

## 📊 Data Source Differences

### OLD Card
- Can fetch data directly from APIs
- OR use integration backend
- Requires provider, auth_index, proxy_url config

### NEW Card
- Uses integration backend ONLY
- Reads from sensor entity
- Just needs entity ID

---

## 🎯 Summary

| Aspect | OLD Card | NEW Card |
|--------|----------|----------|
| **Complexity** | High | Low |
| **Detail Level** | Very detailed | Summary only |
| **Setup** | Manual | Auto |
| **Best For** | Power users | Quick overview |
| **Data** | All models | Key metrics |
| **Size** | Large | Compact |

---

## 💡 My Recommendation

**Keep BOTH cards!**

1. **Use NEW card** for Trouter/9Router monitoring
   - Quick glance at spending and expiration
   - Clean, simple display

2. **Use OLD card** for CLIProxy providers
   - Detailed model breakdown
   - See all quotas at once

3. **Or use BOTH together**
   - NEW card at top for summary
   - OLD card below for details

---

## 🚀 What's Next?

1. **Deploy the integration** with NEW card (auto-installs)
2. **Keep OLD card** in `/config/www/` for detailed views
3. **Use both** depending on your needs!

The NEW card is perfect for your Trouter setup, while the OLD card is great for detailed CLIProxy monitoring! 🎉
