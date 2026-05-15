# 🎉 Easy Installation Guide - AI Quota Integration with Auto-Card

## What's New?

The card now **auto-installs** when you install the integration! No manual resource registration needed!

## Installation Steps

### Step 1: Copy Integration Files

Copy the entire `custom_components/ai_quota` folder to your Home Assistant:

```
From: d:\HASS\AI Quota\AI Quota Card\custom_components\ai_quota
To:   /config/custom_components/ai_quota
```

Your folder structure should look like:
```
/config/
  └── custom_components/
      └── ai_quota/
          ├── __init__.py
          ├── manifest.json
          ├── config_flow.py
          ├── coordinator.py
          ├── sensor.py
          ├── const.py
          ├── strings.json
          ├── translations/
          │   └── en.json
          └── www/
              └── ai-quota-summary-card.js  ← Card auto-loads!
```

### Step 2: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart** (top right)
3. Wait for Home Assistant to restart

### Step 3: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for **"AI Web Quota"**
4. Click on it to configure

### Step 4: Configure Integration

Fill in the form:
```
Data Source: [Trouter.click ▼]
Provider Name: [Trouter ▼]
Auth Index: 0
API Key: YOUR-TROUTER-API-KEY-HERE
Account Name: My Account (optional)
CLIProxy API URL: (leave default if using Trouter/9Router)
```

Click **Submit**

### Step 5: Add Card to Dashboard

The card is **automatically registered**! Just add it:

1. Go to your dashboard
2. Click **Edit Dashboard** (pencil icon)
3. Click **+ Add Card**
4. Search for **"AI Quota Summary"**
5. Select your entity:
   ```yaml
   type: custom:ai-quota-summary-card
   entity: sensor.trouter_trouter_auth_0
   ```
6. Click **Save**

## That's It! 🎉

No manual resource registration needed!
No copying files to www folder!
No clearing cache!

Just install → restart → configure → use!

## What Happens Automatically?

When you install the integration:

✅ **Card auto-registers** - No manual resource setup
✅ **Card auto-loads** - Available immediately after restart
✅ **Card auto-updates** - Updates with integration updates
✅ **No cache issues** - Proper versioning handled

## Verify Installation

### Check Integration
1. Go to **Settings** → **Devices & Services**
2. Look for **AI Web Quota**
3. Should show your configured entities

### Check Card
1. Go to **Settings** → **Dashboards** → **Resources**
2. Look for `/ai_quota/ai-quota-summary-card.js`
3. Should be automatically registered

### Check Entity
1. Go to **Developer Tools** → **States**
2. Search for your entity (e.g., `sensor.trouter_trouter_auth_0`)
3. Should show data with `api_payload` attribute

## Multiple API Keys

Add multiple integrations for different API keys:

1. **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search **"AI Web Quota"**
4. Configure with different API key
5. Repeat for each API key

Then add multiple cards:
```yaml
type: vertical-stack
cards:
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_0
  
  - type: custom:ai-quota-summary-card
    entity: sensor.9router_claude_auth_1
  
  - type: custom:ai-quota-summary-card
    entity: sensor.cliproxy_antigravity_auth_0
```

## Troubleshooting

### Card not showing in card picker

**Solution**: Restart Home Assistant again
```
Settings → System → Restart
```

### Card shows but no data

**Solution**: Check entity state
1. **Developer Tools** → **States**
2. Find your entity
3. Verify `api_payload` exists
4. Check integration logs

### Integration not found

**Solution**: Verify folder structure
```
/config/custom_components/ai_quota/
```
Must contain all files including `manifest.json`

### Old card still showing

**Solution**: Clear browser cache
- Windows/Linux: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

## Updating

To update the integration:

1. Replace files in `/config/custom_components/ai_quota/`
2. Restart Home Assistant
3. Card updates automatically!

No need to:
- ❌ Re-register resources
- ❌ Clear cache
- ❌ Reconfigure integration
- ❌ Recreate cards

## Uninstalling

To remove the integration:

1. **Settings** → **Devices & Services**
2. Find **AI Web Quota**
3. Click three dots → **Delete**
4. Remove folder: `/config/custom_components/ai_quota/`
5. Restart Home Assistant

The card resource will be automatically cleaned up.

## Features

### Single API Key Field ✅
- One field for all data sources
- No confusion about which field to use
- Works with CLIProxy, Trouter, and 9Router

### Auto-Installing Card ✅
- No manual resource registration
- No copying to www folder
- No cache clearing needed
- Just install and use!

### Beautiful Display ✅
- API Key (masked)
- Percentage with color-coded bar
- USD spending ($6 / $100)
- Expiration countdown
- Reset time
- Total and daily spend

## Support

If you need help:

1. **Check logs**: Settings → System → Logs
2. **Check entity**: Developer Tools → States
3. **Check browser console**: Press F12
4. **Restart**: Settings → System → Restart

## Comparison

### Before (Manual Installation)
```
1. Copy integration files
2. Restart HA
3. Copy card to www folder
4. Add resource manually
5. Clear browser cache
6. Configure integration
7. Add card
```

### Now (Auto Installation)
```
1. Copy integration files
2. Restart HA
3. Configure integration
4. Add card
```

**50% fewer steps!** 🎉

---

**Enjoy your easy-to-use AI Quota monitoring!**
