# AI Quota Summary Card - Visual Guide

## Card Layout

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  CLAUDE - CC LITE                          [Service Type]║
║  Y6VC****0XJV                              [API Key]     ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║                        98%                [Percentage]    ║
║                                                           ║
║  ████████████████████████████████░░░░░░░  [Progress Bar] ║
║                                                           ║
║              $1.31 / $100.00              [Usage]        ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  ┌─────────────────────┬─────────────────────┐          ║
║  │ Expires in          │ Reset at            │          ║
║  │ 28 days             │ 2026-05-17 00:00   │          ║
║  └─────────────────────┴─────────────────────┘          ║
║                                                           ║
║  ┌─────────────────────┬─────────────────────┐          ║
║  │ Total Spent         │ Daily Spent         │          ║
║  │ $202.57             │ $1.31               │          ║
║  └─────────────────────┴─────────────────────┘          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

## Color Coding

### Green (60-100% remaining)
```
████████████████████████████████████░░░░  [90%]
Color: #4caf50 (Green)
Status: Healthy - plenty of quota remaining
```

### Orange (30-59% remaining)
```
████████████████████░░░░░░░░░░░░░░░░░░░░  [45%]
Color: #ff9800 (Orange)
Status: Warning - moderate usage
```

### Red (0-29% remaining)
```
████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  [20%]
Color: #f44336 (Red)
Status: Critical - low quota, consider upgrading
```

## Data Fields Explained

### Header Section
- **Service Type**: Shows the API service (e.g., "CLAUDE - CC LITE")
- **API Key**: Masked preview (e.g., "Y6VC****0XJV")

### Main Display
- **Percentage**: Large number showing remaining quota percentage
- **Progress Bar**: Visual representation with color coding
- **Usage**: Current spend vs. total quota in USD format

### Stats Grid
- **Expires in**: Days until API key expires
- **Reset at**: When the daily quota will reset
- **Total Spent**: Lifetime spending on this API key
- **Daily Spent**: Today's spending

## Example Scenarios

### Scenario 1: Fresh API Key (High Quota)
```
╔═══════════════════════════════════════════════════════════╗
║  CLAUDE - CC LITE                                         ║
║  Y6VC****0XJV                                            ║
╠═══════════════════════════════════════════════════════════╣
║                        98%                                ║
║  ████████████████████████████████████░░  [Green]         ║
║              $1.31 / $100.00                             ║
╠═══════════════════════════════════════════════════════════╣
║  Expires in: 28 days    │ Reset at: 2026-05-17 00:00    ║
║  Total Spent: $202.57   │ Daily Spent: $1.31            ║
╚═══════════════════════════════════════════════════════════╝
```

### Scenario 2: Moderate Usage
```
╔═══════════════════════════════════════════════════════════╗
║  CLAUDE - CC LITE                                         ║
║  Y6VC****0XJV                                            ║
╠═══════════════════════════════════════════════════════════╣
║                        45%                                ║
║  ████████████████████░░░░░░░░░░░░░░░░░  [Orange]        ║
║              $55.00 / $100.00                            ║
╠═══════════════════════════════════════════════════════════╣
║  Expires in: 15 days    │ Reset at: 2026-05-17 00:00    ║
║  Total Spent: $450.00   │ Daily Spent: $55.00           ║
╚═══════════════════════════════════════════════════════════╝
```

### Scenario 3: Low Quota (Critical)
```
╔═══════════════════════════════════════════════════════════╗
║  CLAUDE - CC LITE                                         ║
║  Y6VC****0XJV                                            ║
╠═══════════════════════════════════════════════════════════╣
║                        15%                                ║
║  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  [Red]           ║
║              $85.00 / $100.00                            ║
╠═══════════════════════════════════════════════════════════╣
║  Expires in: 5 days     │ Reset at: 2026-05-17 00:00    ║
║  Total Spent: $850.00   │ Daily Spent: $85.00           ║
╚═══════════════════════════════════════════════════════════╝
```

## Dashboard Layout Examples

### Single Card
```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

### Multiple Cards (Vertical Stack)
```yaml
type: vertical-stack
cards:
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_0
  
  - type: custom:ai-quota-summary-card
    entity: sensor.9router_claude_auth_1
```

### Multiple Cards (Horizontal Stack)
```yaml
type: horizontal-stack
cards:
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_0
  
  - type: custom:ai-quota-summary-card
    entity: sensor.9router_claude_auth_1
```

### Grid Layout (2x2)
```yaml
type: grid
columns: 2
cards:
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_0
  
  - type: custom:ai-quota-summary-card
    entity: sensor.9router_claude_auth_1
  
  - type: custom:ai-quota-summary-card
    entity: sensor.cliproxy_antigravity_auth_0
  
  - type: custom:ai-quota-summary-card
    entity: sensor.cliproxy_codex_auth_0
```

## Responsive Design

The card automatically adjusts to different screen sizes:

### Desktop (Wide)
- Full stats grid (2x2)
- Large percentage display
- All information visible

### Tablet (Medium)
- Stats grid adjusts to fit
- Percentage remains large
- Readable on smaller screens

### Mobile (Narrow)
- Stats may stack vertically
- Percentage still prominent
- Touch-friendly

## Customization Tips

### Change Colors
Edit `ai-quota-summary-card.js`:
```javascript
// Line ~95
let barColor = '#4caf50'; // Green
if (percentage < 30) {
  barColor = '#f44336'; // Red - change this
} else if (percentage < 60) {
  barColor = '#ff9800'; // Orange - change this
}
```

### Change Font Sizes
Edit CSS in `ai-quota-summary-card.js`:
```css
.percentage-display {
  font-size: 48px; /* Change this */
}

.usage-display {
  font-size: 18px; /* Change this */
}
```

### Change Grid Layout
Edit CSS in `ai-quota-summary-card.js`:
```css
.quota-stats {
  grid-template-columns: 1fr 1fr; /* Change to 1fr for single column */
}
```

## Integration with Home Assistant

### Automation Example
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
          title: "Low API Quota"
          message: "Your Trouter quota is below 20%!"
```

### Template Sensor Example
```yaml
template:
  - sensor:
      - name: "Trouter Quota Percentage"
        state: >
          {% set quota = state_attr('sensor.trouter_trouter_auth_0', 'api_payload').quota %}
          {% set remaining = quota.daily_remaining | float %}
          {% set total = quota.daily_quota | float %}
          {{ ((remaining / total) * 100) | round(0) }}
        unit_of_measurement: "%"
```

## Comparison with Original Dashboard

### Trouter.click Dashboard
- Shows all data in a web interface
- Requires browser access
- Multiple pages and sections

### AI Quota Summary Card
- Shows key data in Home Assistant
- Integrated with your smart home
- Single card view
- Can trigger automations
- Mobile app access
- Offline access (cached data)

## Benefits

✅ **At-a-glance monitoring**: See quota status instantly
✅ **Color-coded alerts**: Visual warning system
✅ **USD tracking**: Clear spending amounts
✅ **Expiration tracking**: Know when to renew
✅ **Reset tracking**: Plan usage around resets
✅ **Multiple keys**: Monitor all your API keys
✅ **Automation ready**: Trigger actions based on quota
✅ **Mobile friendly**: Check from anywhere

---

**Ready to install?** See `SETUP_SUMMARY_CARD.md` for step-by-step instructions!
