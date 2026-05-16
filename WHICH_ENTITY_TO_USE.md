# 🔍 Which Entity to Use for the Summary Card?

## ❓ The Problem

You have MANY sensors:
- `sensor.ai_quota_trouter_0_daily_spend`
- `sensor.ai_quota_trouter_0_lifetime_spend`
- `sensor.ai_quota_trouter_0_api_key_status`
- etc.

But the **NEW summary card** needs ONE sensor with ALL the data!

---

## ✅ Solution: Find the Main Sensor

The summary card needs a sensor with the `api_payload` attribute containing all Trouter data.

### Step 1: Check Which Sensor Has `api_payload`

1. Go to **Developer Tools** → **States**
2. Search for: `ai_quota_trouter`
3. Click on each sensor
4. Look for one that has `api_payload` in attributes
5. That's the one you need!

### Step 2: Look for These Sensor Names

The main sensor is usually named like:
- `sensor.trouter_trouter_auth_0` ← This one!
- `sensor.ai_quota_trouter_0`
- `sensor.ai_quota_trouter_auth_0`

**NOT** the individual metric sensors like:
- ❌ `sensor.ai_quota_trouter_0_daily_spend`
- ❌ `sensor.ai_quota_trouter_0_lifetime_spend`

---

## 🎯 Quick Test

### Try This Configuration:

```yaml
type: custom:ai-quota-summary-card
entity: sensor.ai_quota_trouter_0
```

If that doesn't work, try:
```yaml
type: custom:ai_quota_summary_card
entity: sensor.trouter_trouter_auth_0
```

---

## 🔧 Alternative: Use the OLD Card Instead

Since you have individual sensors, the **OLD card** might work better!

```yaml
type: custom:ai-quota-card
provider: trouter
auth_index: 0
backend: true
```

This card will automatically find and display all your Trouter sensors!

---

## 📊 Understanding Your Sensors

You have **2 types** of sensors:

### Type 1: Individual Metric Sensors (What you see)
```
sensor.ai_quota_trouter_0_daily_spend          → $1.31
sensor.ai_quota_trouter_0_lifetime_spend       → $202.57
sensor.ai_quota_trouter_0_api_key_status       → Active
sensor.ai_quota_trouter_0_daily_duration_quota → 98%
```

**Use with**: OLD card (`custom:ai-quota-card`)

### Type 2: Main Sensor with api_payload (Hidden?)
```
sensor.trouter_trouter_auth_0
  attributes:
    api_payload:
      key_preview: "Y6VC****0XJV"
      quota: {...}
      usage: {...}
      timestamps: {...}
```

**Use with**: NEW card (`custom:ai-quota-summary-card`)

---

## 💡 Recommendation

Based on your screenshot, I recommend:

### Option 1: Use OLD Card (Easier!)

```yaml
type: custom:ai-quota-card
provider: trouter
auth_index: 0
backend: true
```

**Why**: It will automatically find and display all your individual sensors!

### Option 2: Find Main Sensor for NEW Card

1. Developer Tools → States
2. Search: `trouter`
3. Find sensor with `api_payload` attribute
4. Use that entity ID:
   ```yaml
   type: custom:ai-quota-summary-card
   entity: sensor.FOUND_ENTITY_ID_HERE
   ```

---

## 🎨 Example Dashboard

### Using OLD Card (Works with your sensors):

```yaml
type: custom:ai-quota-card
provider: trouter
auth_index: 0
backend: true
```

This will show:
```
╔═══════════════════════════════════╗
║ Trouter (Auth: 0)                 ║
║ Plan: CC Lite                     ║
╠═══════════════════════════════════╣
║ Daily Duration Quota              ║
║ 98%                               ║
║                                   ║
║ Daily Spend                       ║
║ $1.31                             ║
║                                   ║
║ Lifetime Spend                    ║
║ $202.57                           ║
║                                   ║
║ API Key Status                    ║
║ Active                            ║
╚═══════════════════════════════════╝
```

---

## 🔍 How to Find the Main Sensor

### Method 1: Developer Tools
```
1. Developer Tools → States
2. Filter: "trouter"
3. Click each sensor
4. Look for "api_payload" in attributes
5. That's your main sensor!
```

### Method 2: Check Integration
```
1. Settings → Devices & Services
2. Click "AI Web Quota"
3. Look for main sensor (not the individual metrics)
```

---

## ❓ Still Confused?

### Just use the OLD card!

```yaml
type: custom:ai-quota-card
provider: trouter
auth_index: 0
backend: true
```

It's designed to work with multiple individual sensors and will display everything beautifully! 🎉

---

**TL;DR**: Use the **OLD card** with `provider: trouter` - it's perfect for your setup! The NEW card needs a special main sensor that might not be visible in your list.
