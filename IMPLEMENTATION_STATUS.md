# Multi-Device Hub Implementation - Status Report

## Current Status: DONE ✅ (Updated v2.0.6)

The multi-device hub architecture is fully implemented and stable.

---

## ✅ Completed

### 1. Config Flow
- ✅ Simplified setup flow with data-source based configuration
- ✅ Supports `cliproxy`, `trouter`, and `9router`
- ✅ Entry title uses data source + URL
- ✅ Unique ID based on data source + URL

### 2. Coordinator (Multi-connection)
- ✅ Reworked `_async_update_data()` for hub-and-spoke model
- ✅ 9Router login via password/session
- ✅ Auto-discovery from `/api/providers/client`
- ✅ Per-connection usage fetch from `/api/usage/{connection_id}`
- ✅ Per-connection error isolation (one failure does not break all)
- ✅ Returns normalized connection dictionary for sensor creation

### 3. Sensor Platform
- ✅ Creates one Hub device per integration entry
- ✅ Creates one child device + sensor per discovered connection
- ✅ Links child devices to hub with `via_device`

### 4. 9Router Data Source
- ✅ Added robust 9Router quota parser
- ✅ Supports both formats observed in real API responses:
  - `quotas` map with named windows (`session`, `weekly`, etc.)
  - optional `extraUsage` block (Claude Code style)
- ✅ Human-readable reset countdown formatting

### 5. Summary Card UI (Compact Trouter Layout)
- ✅ Reduced Trouter card visual height
- ✅ Moved usage string (e.g. `$3.98 / $100.00`) to top-left above progress bar
- ✅ Moved percentage (e.g. `96%`) to top-right above progress bar
- ✅ Matched font height between usage and percentage text

### 6. Versioning / Cache Busting
- ✅ Integration version: `2.0.6`
- ✅ Summary card cache-busting version: `2.0.6`

---

## ⚠️ Notes

- This architecture is a major change from old single-account style entries.
- If users still have legacy entries, they may need to remove and re-add integration entries.

---

## 📋 Recommended Next Steps

1. Update to latest HACS version.
2. Restart Home Assistant.
3. Verify entities under each discovered provider connection.
4. Confirm summary card layout changes in dashboard.
