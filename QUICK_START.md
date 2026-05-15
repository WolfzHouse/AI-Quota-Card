# 🚀 Quick Start - AI Quota Integration

## Installation (3 Steps!)

### 1️⃣ Copy Files
```bash
# Copy integration folder
cp -r custom_components/ai_quota /config/custom_components/
```

### 2️⃣ Restart
```
Settings → System → Restart
```

### 3️⃣ Configure
```
Settings → Devices & Services → + Add Integration → "AI Web Quota"
```

**Done!** Card auto-installs! 🎊

---

## Configuration

```yaml
Data Source: Trouter.click
Provider: Trouter
Auth Index: 0
API Key: YOUR-API-KEY-HERE
Account Name: My Account (optional)
```

---

## Add Card

```
Dashboard → Edit → + Add Card → Search "AI Quota Summary"
```

Or manually:
```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

---

## What You Get

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

---

## Features

✅ Auto-installing card (no manual setup!)
✅ Single API key field (no confusion!)
✅ Color-coded progress bar
✅ USD spending tracking
✅ Expiration countdown
✅ Reset time display

---

## Troubleshooting

**Card not showing?**
→ Restart HA again + hard refresh (Ctrl+Shift+R)

**No data?**
→ Developer Tools → States → Check entity

**Integration not found?**
→ Verify `/config/custom_components/ai_quota/manifest.json` exists

---

## Documentation

- 📖 [README.md](README.md) - Full documentation
- 🎯 [EASY_INSTALL.md](EASY_INSTALL.md) - Detailed guide
- 🎨 [VISUAL_GUIDE_CARD.md](VISUAL_GUIDE_CARD.md) - Examples
- 🔧 [API_KEY_CONSOLIDATION.md](API_KEY_CONSOLIDATION.md) - Technical

---

**That's it! Enjoy your AI quota monitoring! 🎉**
