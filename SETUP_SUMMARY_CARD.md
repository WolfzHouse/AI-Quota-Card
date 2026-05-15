# Quick Setup Guide - AI Quota Summary Card

## Step 1: Copy the Card File

Copy the card JavaScript file to your Home Assistant www folder:

**From**: `d:\HASS\AI Quota\AI Quota Card\www\ai-quota-summary-card.js`
**To**: `/config/www/ai-quota-summary-card.js`

(In Home Assistant, `/config` is your main configuration directory)

## Step 2: Add Resource to Lovelace

1. Open Home Assistant
2. Go to **Settings** → **Dashboards**
3. Click the three dots menu (⋮) in the top right
4. Select **Resources**
5. Click **+ Add Resource**
6. Fill in:
   - **URL**: `/local/ai-quota-summary-card.js`
   - **Resource type**: JavaScript Module
7. Click **Create**

## Step 3: Add Card to Dashboard

1. Go to your dashboard
2. Click **Edit Dashboard** (pencil icon)
3. Click **+ Add Card**
4. Scroll down and select **Custom: AI Quota Summary Card**
   (or search for "ai-quota-summary-card")
5. Configure the card:
   ```yaml
   type: custom:ai-quota-summary-card
   entity: sensor.trouter_trouter_auth_0
   ```
   (Replace `sensor.trouter_trouter_auth_0` with your actual entity ID)
6. Click **Save**

## Step 4: Find Your Entity ID

If you don't know your entity ID:

1. Go to **Developer Tools** → **States**
2. Search for "ai_quota" or "trouter"
3. Find your sensor entity (e.g., `sensor.trouter_trouter_auth_0`)
4. Copy the entity ID

## Example Card Configuration

```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

## What You'll See

The card will display:
- ✅ **API Key**: Y6VC****0XJV (masked)
- ✅ **Percentage**: Large number showing remaining quota (e.g., 98%)
- ✅ **Progress Bar**: Color-coded (green/orange/red)
- ✅ **Usage**: $1.31 / $100.00
- ✅ **Expires in**: 28 days
- ✅ **Reset at**: 2026-05-17 00:00:00
- ✅ **Total Spent**: $202.57
- ✅ **Daily Spent**: $1.31

## Troubleshooting

### Card doesn't appear
- Clear browser cache: `Ctrl + Shift + R`
- Check browser console (F12) for errors
- Verify resource is added correctly

### No data showing
- Verify entity exists in **Developer Tools** → **States**
- Check that entity has `api_payload` attribute
- Ensure integration is working (check **Settings** → **Devices & Services**)

### Wrong entity ID
- Go to **Developer Tools** → **States**
- Search for your integration name
- Copy the correct entity ID

## Multiple Cards

You can add multiple cards for different API keys:

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

## Next Steps

1. ✅ Consolidate API key fields (DONE)
2. ✅ Create summary card (DONE)
3. 📋 Copy card file to Home Assistant
4. 📋 Add resource to Lovelace
5. 📋 Add card to dashboard
6. 📋 Enjoy your beautiful quota display!
