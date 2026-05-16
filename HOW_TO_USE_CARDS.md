# 📖 How to Use Both Cards - Step by Step

## 🎯 Quick Answer

You're getting errors because you need to add the required parameters!

---

## ✨ NEW Card (Summary Card)

### Error You're Seeing:
```
Configuration error
You need to define an entity
```

### ✅ Correct Configuration:

```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

### 📝 Step-by-Step:

1. **Edit Dashboard** (click pencil icon)
2. **Add Card** (click + button)
3. **Manual Card** (scroll to bottom)
4. **Paste this YAML**:
   ```yaml
   type: custom:ai-quota-summary-card
   entity: sensor.trouter_trouter_auth_0
   ```
5. **Replace entity** with YOUR entity ID:
   - Go to **Developer Tools** → **States**
   - Search for "trouter" or "ai_quota"
   - Copy your entity ID (e.g., `sensor.trouter_trouter_auth_0`)
6. **Click Save**

### 🎨 What You'll See:
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

## 🔧 OLD Card (Detailed Card)

### Error You're Seeing:
```
Configuration error
You need to define provider
```

### ✅ Correct Configuration:

```yaml
type: custom:ai-quota-card
provider: trouter
auth_index: 0
backend: true
```

### 📝 Step-by-Step:

1. **Edit Dashboard**
2. **Add Card**
3. **Manual Card**
4. **Paste this YAML**:
   ```yaml
   type: custom:ai-quota-card
   provider: trouter
   auth_index: 0
   backend: true
   ```
5. **Adjust provider** if needed:
   - `trouter` for Trouter.click
   - `antigravity` for Antigravity
   - `claude` for Claude
   - `codex` for Codex
6. **Click Save**

### 🎨 What You'll See:
```
╔═══════════════════════════════════╗
║ Trouter (Auth: 0)                 ║
║ Plan: CC Lite                     ║
╠═══════════════════════════════════╣
║ Daily Duration Quota              ║
║ 98% remaining                     ║
║ 0.13h / 2.78h | Reset: ...       ║
║                                   ║
║ Lifetime Spend                    ║
║ $202.57                           ║
║                                   ║
║ Daily Spend                       ║
║ $1.31                             ║
╚═══════════════════════════════════╝
```

---

## 🎯 Complete Examples

### Example 1: Just NEW Card (Recommended for Trouter)

```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

**Why**: Simple, clean, shows everything you need!

---

### Example 2: Just OLD Card (For Detailed View)

```yaml
type: custom:ai-quota-card
provider: trouter
auth_index: 0
backend: true
```

**Why**: Shows more detailed breakdown of all metrics

---

### Example 3: BOTH Cards Together (Best!)

```yaml
type: vertical-stack
cards:
  # Quick summary at top
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_0
  
  # Detailed view below
  - type: custom:ai-quota-card
    provider: trouter
    auth_index: 0
    backend: true
```

**Why**: Get both quick overview AND detailed info!

---

## 🔍 How to Find Your Entity ID

### Method 1: Developer Tools
1. Go to **Developer Tools** (in sidebar)
2. Click **States** tab
3. Search for: `ai_quota` or `trouter`
4. Copy the entity ID (e.g., `sensor.trouter_trouter_auth_0`)

### Method 2: Integration Page
1. Go to **Settings** → **Devices & Services**
2. Find **AI Web Quota** integration
3. Click on it
4. See list of entities
5. Copy entity ID

---

## 📋 Configuration Cheat Sheet

### NEW Card (ai-quota-summary-card)
```yaml
type: custom:ai-quota-summary-card
entity: sensor.PROVIDER_PROVIDER_auth_INDEX
```

**Required**:
- `entity` - Your sensor entity ID

**Optional**: None!

---

### OLD Card (ai-quota-card)
```yaml
type: custom:ai-quota-card
provider: PROVIDER_NAME
auth_index: INDEX_NUMBER
backend: true
```

**Required**:
- `provider` - Provider name (trouter, antigravity, claude, etc.)
- `auth_index` - Auth index number (usually 0)
- `backend: true` - Use integration data

**Optional**:
- `refresh_interval` - Auto-refresh interval in seconds

---

## 🎨 Multiple Cards Example

### For Multiple API Keys

```yaml
type: vertical-stack
cards:
  # Trouter Account 1
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_0
  
  # Trouter Account 2
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_1
  
  # 9Router Account
  - type: custom:ai-quota-summary-card
    entity: sensor.9router_trouter_auth_0
```

---

## 🐛 Troubleshooting

### Error: "You need to define an entity"
**Solution**: Add `entity:` line with your sensor ID
```yaml
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0  ← Add this!
```

### Error: "You need to define provider"
**Solution**: Add `provider:` and `backend: true`
```yaml
type: custom:ai-quota-card
provider: trouter  ← Add this!
auth_index: 0      ← Add this!
backend: true      ← Add this!
```

### Error: "Entity not found"
**Solution**: Check entity ID in Developer Tools → States

### Card not showing
**Solution**: 
1. Restart Home Assistant
2. Clear browser cache (Ctrl+Shift+R)
3. Check card is registered in Settings → Dashboards → Resources

---

## ✅ Quick Setup Checklist

### For NEW Card:
- [ ] Integration installed and configured
- [ ] Home Assistant restarted
- [ ] Entity exists (check Developer Tools → States)
- [ ] Card added with `entity:` parameter
- [ ] Entity ID is correct

### For OLD Card:
- [ ] Integration installed and configured
- [ ] Card file in `/config/www/` (if not using auto-install)
- [ ] Resource registered (if not using auto-install)
- [ ] Card added with `provider:`, `auth_index:`, `backend: true`
- [ ] Provider name matches your integration

---

## 🎉 Final Example (Copy & Paste Ready!)

### For Trouter.click:

```yaml
# Simple version (NEW card only)
type: custom:ai-quota-summary-card
entity: sensor.trouter_trouter_auth_0
```

### For Multiple Views:

```yaml
# Both cards together
type: vertical-stack
cards:
  - type: custom:ai-quota-summary-card
    entity: sensor.trouter_trouter_auth_0
  
  - type: custom:ai-quota-card
    provider: trouter
    auth_index: 0
    backend: true
```

---

**Just replace `sensor.trouter_trouter_auth_0` with YOUR entity ID and you're done!** 🎊
