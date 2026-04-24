# AI Quota — Home Assistant Integration

A native **Home Assistant custom integration** and **Lovelace card** to monitor AI API quotas for Claude, Codex, Gemini CLI, Antigravity, and more — powered by your [`CLIProxyAPI`](https://github.com/WolfzHouse/CLIProxyAPI) backend.

The integration automatically creates backend sensors for each quota tier and provides a beautiful Lovelace card to display them on your dashboard!

## Features

- 🤖 **Multi-provider support**: Claude (Anthropic), Codex (OpenAI), Gemini CLI, Antigravity, GitHub Copilot, Kiro
- 📊 **Native HA sensors**: Each quota limit becomes a real sensor — use them in automations, history graphs, and alerts
- 🖥️ **Lovelace card**: Auto-registered on install, no manual resource setup needed
- 🔄 **Hybrid mode**: Card can display data directly from backend sensors (no extra API calls) or fetch independently
- ⚙️ **UI-based setup**: Add and configure hubs directly from Settings → Devices & Services

---

## Installation

[![Open your Home Assistant instance and add a custom repository.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=WolfzHouse&repository=AI-Quota-Card&category=integration)

### Via HACS (Recommended)
1. Open **HACS** in your Home Assistant.
2. Click the three dots → **Custom repositories**.
3. Add this repository URL and select category: **Integration**.
4. Download the **AI Quota Card** integration.
5. **Restart Home Assistant** completely.
6. Go to **Settings → Devices & Services → Add Integration** → search for **"AI Web Quota"**.

### Manual Installation
1. Copy the `custom_components/ai_quota/` folder into your HA config directory at `/config/custom_components/ai_quota/`.
2. **Restart Home Assistant**.
3. Go to **Settings → Devices & Services → Add Integration** → search for **"AI Web Quota"**.

> **Note:** The Lovelace card (`ai-quota-card`) is registered automatically on startup. No manual resource configuration is needed.

---

## Setting Up a Hub

After installation, click **+ Add Integration** and fill in:

| Field | Description |
|---|---|
| **Provider** | AI provider: `claude`, `codex`, `gemini-cli`, `antigravity`, `copilot`, `kiro` |
| **Auth Index** | The account index configured in your CLIProxyAPI (default: `0`) |
| **CLIProxy Token** | Your CLIProxyAPI management token |
| **Account Name** *(optional)* | Display alias shown on the card header |
| **CLIProxy URL** *(optional)* | Your proxy URL (default: `https://ai.wolfz.shop`) |

You can add **multiple hubs** — one per provider/account combination.

To edit a hub after creation, click **Configure** on it in the integrations page. Note: only the token, alias and URL can be changed — provider and auth index are fixed after creation.

---

## Dashboard Card

After a restart, a new `custom:ai-quota-card` element is automatically available. Add a **Manual Card** to your dashboard with one of the two modes:

### Mode 1: Backend Mode *(Recommended)*
Reads data directly from your Home Assistant sensors. No extra API calls — loads instantly.

```yaml
type: custom:ai-quota-card
backend: true
provider: claude
auth_index: 0
```

### Mode 2: Standalone Mode
Fetches data independently from your proxy. Useful without the backend integration.

```yaml
type: custom:ai-quota-card
provider: claude
auth_index: 0
proxy_url: https://ai.wolfz.shop/
proxy_token: YOUR_TOKEN_HERE
```

### Card Options

| Name | Type | Required | Description |
|---|---|---|---|
| `type` | string | ✅ | `custom:ai-quota-card` |
| `provider` | string | ✅ | Provider name: `claude`, `codex`, `gemini-cli`, `antigravity`, `copilot`, `kiro` |
| `auth_index` | string/number | ✅ | Account index matching your CLIProxyAPI config |
| `backend` | boolean | ➖ | Set `true` to read from HA sensors instead of fetching from proxy |
| `proxy_url` | string | ➖ | Proxy URL *(Standalone mode only)* |
| `proxy_token` | string | ➖ | Management token *(Standalone mode only)* |

---

## Troubleshooting

### `Custom element not found: ai-quota-card`
The card JS was not loaded by your browser. Try:
1. **Fully restart Home Assistant** (not just reload).
2. **Hard refresh your browser** (`Ctrl+Shift+R` / `Cmd+Shift+R`).
3. If still failing: open browser DevTools (`F12`) → **Application** → **Service Workers** → **Unregister**, then refresh.

### `Config flow could not be loaded: 500 Internal Server Error`
Usually caused by a stale cached integration version. Fix:
1. Fully restart Home Assistant.
2. Hard refresh your browser (`Ctrl+Shift+R`).

### `API Error 429: Rate Limited`
Your proxy is being rate-limited. Home Assistant will automatically retry after a few minutes — no action needed.

### `API Error 401: Unauthorized`
The auth token stored in your proxy has expired. Re-run the corresponding CLI tool locally (e.g., run `codex` or `antigravity` in a terminal) to refresh the token, then wait for the next polling cycle.

### `Failed setup, will retry`
This is completely normal during the first boot or after rate-limiting. Home Assistant retries automatically in the background.
