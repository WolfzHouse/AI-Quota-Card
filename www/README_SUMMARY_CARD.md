# AI Quota Summary Card

A beautiful, clean Lovelace card for displaying AI quota information from Trouter.click, 9Router, or CLIProxy sources.

## Features

- **API Key Display**: Shows masked API key preview
- **Visual Progress Bar**: Color-coded percentage indicator (green/orange/red)
- **Usage Display**: Shows current spend vs. total quota in USD
- **Expiration Info**: Days remaining until API key expires
- **Reset Time**: When the quota will reset
- **Spend Tracking**: Both daily and lifetime spend amounts

## Installation

### Method 1: Manual Installation

1. Copy `ai-quota-summary-card.js` to your Home Assistant `www` folder:
   ```
   /config/www/ai-quota-summary-card.js
   ```

2. Add the resource to your Lovelace dashboard:
   - Go to **Settings** → **Dashboards** → **Resources**
   - Click **Add Resource**
   - URL: `/local/ai-quota-summary-card.js`
   - Resource type: **JavaScript Module**

### Method 2: HACS (if available)

1. Add this repository as a custom repository in HACS
2. Install "AI Quota Summary Card"
3. Restart Home Assistant

## Usage

### Basic Configuration

Add the card to your Lovelace dashboard:

```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

### Full Example

```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

## Card Display

The card shows:

1. **Header Section**:
   - Service type (e.g., "CLAUDE - CC Lite")
   - API key preview (e.g., "Y6VC****0XJV")

2. **Main Section (Compact)**:
   - Top info row with usage on the left (e.g., `$3.98 / $100.00`)
   - Remaining percentage on the right (e.g., `96%`)
   - Color-coded progress bar directly below

3. **Stats Grid**:
   - **Expires in**: Days until API key expires
   - **Reset at**: When daily quota resets
   - **Total Spent**: Lifetime spending
   - **Daily Spent**: Today's spending

## Color Coding

- **Green** (60-100%): Plenty of quota remaining
- **Orange** (30-59%): Moderate usage
- **Red** (0-29%): Low quota, consider upgrading or waiting for reset

## Supported Data Sources

This card works with entities from:
- **Trouter.click**: Full support for all metrics
- **9Router**: Full support for all metrics
- **CLIProxy**: Limited support (depends on provider data)

## Troubleshooting

### Card not showing

1. Verify the resource is loaded:
   - Open browser console (F12)
   - Look for any JavaScript errors
   - Check that `/local/ai-quota-summary-card.js` is accessible

2. Clear browser cache:
   - Hard refresh: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)

3. Verify entity exists:
   - Go to **Developer Tools** → **States**
   - Search for your entity ID
   - Confirm it has `api_payload` attribute

### Data not displaying correctly

1. Check entity attributes:
   ```yaml
   # The entity should have these attributes:
   api_payload:
     key_preview: "Y6VC****0XJV"
     service_type: "claude"
     sub_service_type_name: "CC Lite"
     quota:
       type: "duration"
       daily_quota: 10000
       daily_remaining: 9869
       daily_spent: 131
       next_reset_at: "2026-05-17T00:00:00+08:00"
     usage:
       total_spent: 20257
       daily_spent: 131
     timestamps:
       expires_at: "2026-06-12T08:05:03.324Z"
   ```

2. Ensure you're using a Trouter or 9Router data source for full functionality

## Customization

You can modify the card's appearance by editing `ai-quota-summary-card.js`:

- **Colors**: Change `barColor` values in the JavaScript
- **Font sizes**: Modify CSS classes like `.percentage-display`
- **Layout**: Adjust grid columns in `.quota-stats`

## Example Dashboard Layout

```yaml
views:
  - title: AI Quotas
    cards:
      - type: custom:ai-quota-summary-card
        entity: sensor.trouter_trouter_auth_0
      
      - type: custom:ai-quota-summary-card
        entity: sensor.9router_claude_auth_0
      
      - type: horizontal-stack
        cards:
          - type: custom:ai-quota-summary-card
            entity: sensor.cliproxy_antigravity_auth_0
          - type: custom:ai-quota-summary-card
            entity: sensor.cliproxy_codex_auth_0
```

## Screenshots

The card displays a clean, modern interface similar to the Trouter.click dashboard, with:
- Compact top row for usage + percentage
- Color-coded progress bar
- Clear USD spending amounts
- Expiration and reset information

## Support

For issues or feature requests, please check:
1. Home Assistant logs: **Settings** → **System** → **Logs**
2. Browser console: Press F12 and check for errors
3. Entity state: **Developer Tools** → **States**

## License

This card is part of the AI Quota integration for Home Assistant.
