# Trouter Integration Setup Guide

> **Historical — describes the v1.1.0 config flow** (provider name + auth index +
> CLIProxy token). The 2.0.x integration no longer works this way, so read this as a
> record of how setup used to look rather than as instructions. API keys shown are
> placeholders.

## Overview
The Trouter provider has been successfully added to the AI Quota integration. It monitors your Trouter API usage, quota, spending, and token consumption.

## What's Been Added

### 1. Provider Configuration
- Added "Trouter" to the list of available providers
- Configured direct API access to `https://trouter.click/api/proxy/me?view=dashboard`

### 2. Sensors Created
The integration will create the following sensors for Trouter:

1. **Daily Duration Quota** - Shows remaining time quota percentage
   - Format: `X.XXh / Y.YYh | Reset: [timestamp]`
   - Example: `0.04h / 2.78h | Reset: 2026-05-17T00:00:00+08:00`

2. **Lifetime Spend** - Total amount spent
   - Format: `$XXX.XX`
   - Example: `$202.57`

3. **Daily Spend** - Today's spending
   - Format: `$X.XX`
   - Example: `$1.31`

4. **Total Requests** - Request statistics
   - Format: `XXX total (X today)`
   - Example: `386 total (9 today)`

5. **Token Usage** - Token consumption breakdown
   - Format: `XX,XXX,XXX tokens (I:XX,XXX,XXX O:XXX,XXX)`
   - Includes input, output, cache read, and cache write tokens

6. **API Key Status** - Key validity indicator
   - Shows: Active (100%) or Inactive (0%)
   - Format: `Expires: YYYY-MM-DD HH:MM`

7. **Service Type** - Your service plan
   - Format: `SERVICE - PLAN NAME`
   - Example: `CLAUDE - CC Lite`

## Setup Instructions

### Step 1: Restart Home Assistant
Restart Home Assistant to load the updated integration code.

### Step 2: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"AI Web Quota"**
4. Click on it to start configuration

### Step 3: Configure Trouter

Fill in the configuration form:

- **Provider**: Select **"Trouter"** from the dropdown
- **Auth Index**: Enter `0` (default)
- **Proxy Token**: Leave empty (not needed for Trouter)
- **Trouter API Key**: Enter your Trouter API key
  - Format: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`
  - This is the Bearer token from your Trouter dashboard
- **Account Name**: (Optional) A friendly name like "My Trouter Account"
- **Proxy URL**: Leave as default (not used for Trouter)

### Step 4: Save and Verify

1. Click **Submit**
2. The integration will create a device named "Trouter Quota (Auth 0)"
3. Check that all sensors are created and showing data
4. Sensors update every 15 minutes

## Finding Your Trouter API Key

Your Trouter API key is the Bearer token used to authenticate with the API:

1. Open your browser's Developer Tools (F12)
2. Go to the **Network** tab
3. Visit https://trouter.click/dashboard
4. Look for the request to `/api/proxy/me?view=dashboard`
5. Check the **Request Headers**
6. Find the `Authorization` header
7. Copy the value after `Bearer ` (without the "Bearer " prefix)

Example:
```
Authorization: Bearer XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```
Your API key is: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

## Troubleshooting

### Error: "Trouter API key is required"
- Make sure you filled in the **Trouter API Key** field during setup
- The key should be in the format: `XXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

### Error: "Trouter API error 401"
- Your API key is invalid or expired
- Get a new API key from the Trouter dashboard

### Error: "Trouter API error 404"
- The API endpoint might have changed
- Check if you can access https://trouter.click/dashboard in your browser

### Sensors not updating
- Check Home Assistant logs for errors
- Verify your API key is still valid
- The integration updates every 15 minutes by default

## Data Privacy

The Trouter integration:
- Makes direct API calls to Trouter (does NOT use the proxy)
- Stores your API key securely in Home Assistant's configuration
- Only fetches data when Home Assistant requests an update (every 15 minutes)

## Files Modified

1. `const.py` - Added Trouter provider and API key configuration
2. `config_flow.py` - Added Trouter API key input field
3. `coordinator.py` - Added direct API call handler and data parser for Trouter

## Support

If you encounter issues:
1. Check Home Assistant logs: Settings → System → Logs
2. Look for entries containing "AI Quota" or "Trouter"
3. Verify your API key is correct and active
