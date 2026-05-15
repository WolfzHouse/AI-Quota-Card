# AI Web Quota Integration for Home Assistant

Monitor your AI API quotas directly in Home Assistant with beautiful, auto-installing cards!

## ✨ Features

- 🎯 **Single API Key Field** - One field for all data sources (no confusion!)
- 🚀 **Auto-Installing Card** - Card registers automatically (no manual setup!)
- 📊 **Beautiful Dashboard** - Clean, modern UI with color-coded progress bars
- 💰 **USD Tracking** - Clear spending display ($6 / $100)
- ⏰ **Expiration Alerts** - Know when your API key expires
- 🔄 **Reset Tracking** - See when quotas reset
- 🌐 **Multi-Source Support** - CLIProxy, Trouter.click, and 9Router

## 🎉 Quick Install (3 Steps!)

### 1. Copy Files
```bash
# Copy the integration folder to Home Assistant
cp -r custom_components/ai_quota /config/custom_components/
```

### 2. Restart Home Assistant
```
Settings → System → Restart
```

### 3. Add Integration
```
Settings → Devices & Services → + Add Integration → "AI Web Quota"
```

**That's it!** The card auto-installs and is ready to use! 🎊

## 📸 Screenshots

### Configuration (Simple!)
```
┌─────────────────────────────────────┐
│ Data Source: [Trouter.click ▼]     │
│ Provider: [Trouter ▼]              │
│ Auth Index: [0]                     │
│ API Key: [____________________]     │  ← One field for all!
│ Account Name: [________]            │
└─────────────────────────────────────┘
```

### Card Display (Beautiful!)
```
╔═══════════════════════════════════════╗
║ CLAUDE - CC LITE                      ║
║ Y6VC****0XJV                         ║
╠═══════════════════════════════════════╣
║              98%                      ║
║ ████████████████████████░░░░░        ║
║         $1.31 / $100.00              ║
╠═══════════════════════════════════════╣
║ Expires: 28 days │ Reset: 2026-05-17║
║ Total: $202.57   │ Daily: $1.31     ║
╚═══════════════════════════════════════╝
```

## 🔧 Configuration

### Supported Data Sources

#### 1. Trouter.click
```yaml
Data Source: Trouter.click
Provider: Trouter
Auth Index: 0
API Key: Y6VCB0J1-GNCV-ZRR3-XT2J-5M9Y56B60XJV
```

#### 2. 9Router
```yaml
Data Source: 9Router
Provider: Trouter
Auth Index: 0
API Key: YOUR-9ROUTER-API-KEY
```

#### 3. CLIProxy
```yaml
Data Source: CLIProxy
Provider: Antigravity / Claude / Codex / etc.
Auth Index: 0
API Key: YOUR-CLIPROXY-TOKEN
CLIProxy API URL: https://ai.wolfz.shop/v0/management/api-call
```

## 📱 Using the Card

The card is **automatically registered** when you install the integration!

### Add to Dashboard

1. Edit Dashboard
2. Add Card
3. Search for "AI Quota Summary"
4. Select your entity
5. Done!

### Card Configuration

```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

### Multiple Cards

```yaml
type: vertical-stack
cards:
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_0
  
  - type: custom:ai-quota-summary-card
    entity: sensor.9router_claude_auth_1
```

## 🎨 Card Features

- ✅ **API Key Display** - Masked preview (Y6VC****0XJV)
- ✅ **Percentage Bar** - Color-coded (green/orange/red)
- ✅ **USD Spending** - Current vs. total ($6 / $100)
- ✅ **Expiration** - Days until key expires
- ✅ **Reset Time** - When quota resets
- ✅ **Spend Tracking** - Total and daily amounts

### Color Coding

- 🟢 **Green (60-100%)** - Plenty of quota
- 🟠 **Orange (30-59%)** - Moderate usage
- 🔴 **Red (0-29%)** - Low quota, upgrade or wait

## 🤖 Automation Example

```yaml
automation:
  - alias: "Low Quota Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.trouter_trouter_auth_0
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Low API Quota"
          message: "Your Trouter quota is below 20%!"
```

## 📦 What's Included

```
custom_components/ai_quota/
├── __init__.py              # Auto-registers card
├── manifest.json            # Integration metadata
├── config_flow.py           # Configuration UI
├── coordinator.py           # Data fetching
├── sensor.py                # Sensor entities
├── const.py                 # Constants
├── strings.json             # UI strings
├── translations/
│   └── en.json             # English translations
└── www/
    └── ai-quota-summary-card.js  # Auto-installing card!
```

## 🔄 Updating

1. Replace files in `/config/custom_components/ai_quota/`
2. Restart Home Assistant
3. Done! (Card updates automatically)

## 🗑️ Uninstalling

1. Settings → Devices & Services
2. Find "AI Web Quota"
3. Click three dots → Delete
4. Remove `/config/custom_components/ai_quota/`
5. Restart Home Assistant

## 🆚 Comparison

### Before (Old Way)
- ❌ Two API key fields (confusing!)
- ❌ Manual card installation
- ❌ Manual resource registration
- ❌ Cache clearing needed
- ❌ 7 installation steps

### Now (New Way)
- ✅ One API key field (simple!)
- ✅ Auto-installing card
- ✅ Auto-registering resource
- ✅ No cache issues
- ✅ 3 installation steps

## 🐛 Troubleshooting

### Card not showing
**Solution**: Restart Home Assistant again
```
Settings → System → Restart
```

### No data in card
**Solution**: Check entity state
```
Developer Tools → States → Search for your entity
```

### Integration not found
**Solution**: Verify folder structure
```
/config/custom_components/ai_quota/manifest.json must exist
```

### Old card cached
**Solution**: Hard refresh browser
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

## 📚 Documentation

- [Easy Installation Guide](EASY_INSTALL.md) - Step-by-step with screenshots
- [API Key Consolidation](API_KEY_CONSOLIDATION.md) - Technical details
- [Visual Guide](VISUAL_GUIDE_CARD.md) - Card examples and customization
- [Setup Guide](SETUP_SUMMARY_CARD.md) - Advanced configuration

## 🤝 Contributing

Found a bug? Have a feature request? Open an issue!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Credits

- Built for Home Assistant
- Supports Trouter.click, 9Router, and CLIProxy
- Auto-installing card technology

## 🌟 Support

If you find this useful, give it a star! ⭐

---

**Made with ❤️ for the Home Assistant community**

**Version**: 1.0.0  
**Last Updated**: May 16, 2026
