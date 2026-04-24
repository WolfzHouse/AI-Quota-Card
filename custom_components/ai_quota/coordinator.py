"""DataUpdateCoordinator for AI Quota."""
import json
import logging
import math
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    CONF_PROXY_URL,
    CONF_PROVIDER,
    CONF_AUTH_INDEX,
    CONF_PROXY_TOKEN,
    CONF_ACCOUNT_NAME,
    DEFAULT_PROXY_URL,
    DEFAULT_SCAN_INTERVAL_MINUTES
)

_LOGGER = logging.getLogger(__name__)

class AIQuotaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AI Quota data via CLIProxyAPI."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        
        # Ensure we poll relatively infrequently by default, e.g. 15 mins
        interval = timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=interval,
        )

    def _format_reset_time(self, timestamp_ms: float) -> str:
        """Return the string reset time or empty if invalid."""
        if not timestamp_ms:
            return ""
        from datetime import datetime
        try:
            dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
            return dt.isoformat()
        except Exception:
            return ""

    def _parse_provider_data(self, provider: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Ported logic from ai-quota-card.js to parse the response payload natively."""
        if not data or not isinstance(data, dict):
            _LOGGER.warning("[AI Quota] %s returned empty or non-dict body: %s", provider, data)
            return []
        items = []

        if provider == "antigravity":
            groups = {}
            models_data = data.get("models", {})
            for name, m_data in models_data.items():
                frac = m_data.get("remainingFraction")
                # Fallback rule: if no remainingFraction provided but exists in models, it implies 100% full limit
                parsed_remaining = float(frac) if frac is not None else 1.0
                
                reset_ms = m_data.get("resetTimeMs")
                rt = self._format_reset_time(float(reset_ms)) if reset_ms else ""

                lname = name.lower()
                group_name = "Other"
                if "gemini" in lname and "pro" in lname:
                    group_name = "Gemini Pro"
                elif "gemini" in lname and "flash" in lname:
                    group_name = "Gemini Flash"
                elif "gemini" in lname:
                    group_name = "Gemini"
                elif "gpt-4" in lname:
                    group_name = "GPT-4"
                elif "gpt-3.5" in lname:
                    group_name = "GPT-3.5"
                elif "gpt" in lname or "o1" in lname:
                    group_name = "GPT"
                elif "claude" in lname:
                    group_name = "Claude"
                
                if group_name not in groups:
                    groups[group_name] = []
                groups[group_name].append({
                    "name": name,
                    "percentage": max(0, min(100, round(parsed_remaining * 100))),
                    "resetTime": rt
                })
            
            for g_name, r_items in groups.items():
                if not r_items:
                    continue
                avg = sum(i["percentage"] for i in r_items) / len(r_items)
                rt_str = next((i["resetTime"] for i in r_items if i.get("resetTime")), "")
                items.append({
                    "name": g_name,
                    "models": r_items,
                    "percentage": round(avg),
                    "resetTime": rt_str
                })

        elif provider == "claude":
            models = []
            
            def add_usage(key: str, display_name: str):
                usage = data.get(key)
                if usage and usage.get("utilization") is not None:
                    u = float(usage["utilization"])
                    rt = ""
                    resets_at = usage.get("resets_at")
                    if resets_at:
                        try:
                            from datetime import datetime
                            # Anthropic gives ISO strings
                            dt = datetime.fromisoformat(resets_at.replace("Z", "+00:00"))
                            rt = dt.isoformat()
                        except Exception:
                            pass
                    models.append({
                        "name": display_name,
                        "percentage": max(0, min(100, round(100 - u))),
                        "resetTime": rt
                    })
            
            add_usage("five_hour", "5-hour limit")
            add_usage("seven_day", "7-day limit")
            add_usage("seven_day_sonnet", "7-day-sonnet limit")
            add_usage("seven_day_opus", "7-day-opus limit")

            extra = data.get("extra_usage")
            if extra and isinstance(extra, dict) and extra.get("is_enabled"):
                utilization = 0.0
                if extra.get("utilization") is not None:
                    utilization = float(extra["utilization"])
                elif extra.get("used_credits") is not None and extra.get("monthly_limit") and float(extra["monthly_limit"]) > 0:
                    utilization = (float(extra["used_credits"]) / float(extra["monthly_limit"])) * 100.0

                extra_disp = ""
                if extra.get("used_credits") is not None and extra.get("monthly_limit") is not None:
                    used = float(extra["used_credits"]) / 100.0
                    total = float(extra["monthly_limit"]) / 100.0
                    extra_disp = f"${used:.2f} / ${total:.2f}"
                
                models.append({
                    "name": "Extra Usage",
                    "percentage": max(0, min(100, round(100 - utilization))),
                    "resetTime": extra_disp
                })
            
            items.append({"name": "Claude Quota", "models": models})

        elif provider == "codex":
            limits = []
            def process_win(name: str, win: dict):
                if not win:
                    return
                pct = 0
                if win.get("used_percent") is not None:
                    pct = max(0, min(100, round(100 - float(win["used_percent"]))))
                else:
                    remaining = float(win.get("remaining_count", 0))
                    total = float(win.get("total_count", 1))
                    total = max(total, 1)
                    pct = max(0, min(100, round((remaining / total) * 100)))
                
                rt = ""
                if win.get("reset_at") and float(win["reset_at"]) > 0:
                    target_ms = float(win["reset_at"])
                    if target_ms < 10000000000:
                        target_ms *= 1000
                    rt = self._format_reset_time(target_ms)
                elif win.get("reset_after_seconds") and float(win["reset_after_seconds"]) > 0:
                    import time
                    target_ms = (time.time() + float(win["reset_after_seconds"])) * 1000
                    rt = self._format_reset_time(target_ms)

                limits.append({"name": name, "percentage": pct, "resetTime": rt})

            rl = data.get("rate_limit", {})
            crl = data.get("code_review_rate_limit", {})
            
            plan_type = data.get("plan_type", "plus")
            if isinstance(plan_type, str):
                plan_type = plan_type.lower()
            
            # Process main windows
            if plan_type == "free":
                process_win("Weekly limit", rl.get("primary_window") or data.get("5_hour_window") or data.get("weekly_window"))
            else:
                process_win("5-hour limit", rl.get("primary_window") or data.get("5_hour_window"))
                process_win("Weekly limit", rl.get("secondary_window") or data.get("weekly_window"))
            
            # Process code review windows
            process_win("Code review weekly limit", crl.get("primary_window") or data.get("code_review_window"))

            items.append({"name": "Codex Quota", "models": limits})
            
        elif provider == "gemini-cli":
            buckets = []
            for b in data.get("buckets", []):
                name = b.get("modelId", "unknown model")
                used = float(b.get("used", 0))
                limit = float(b.get("limit", 1))
                if limit <= 0:
                    limit = 1
                
                pct = max(0, min(100, round(100 - (used / limit * 100))))
                
                rt = ""
                resets_at = b.get("resetsAt")
                if resets_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(resets_at.replace("Z", "+00:00"))
                        rt = dt.isoformat()
                    except Exception:
                        pass
                
                buckets.append({"name": name, "percentage": pct, "resetTime": rt})
            items.append({"name": "Gemini Quota", "models": buckets})

        elif provider in ("kiro", "copilot"):
            title = "Kiro" if provider == "kiro" else "Copilot"
            models = []
            for m in data.get("models", []):
                pct = 0
                if m.get("percentage") is not None:
                    pct = float(m["percentage"])
                elif m.get("limit") is not None and m.get("used") is not None and float(m["limit"]) > 0:
                    pct = 100 - ((float(m["used"]) / float(m["limit"])) * 100)
                
                rt = ""
                resets_at = m.get("resetsAt")
                if resets_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(resets_at.replace("Z", "+00:00"))
                        rt = dt.isoformat()
                    except Exception:
                        pass
                
                models.append({
                    "name": m.get("name", "quota"),
                    "percentage": max(0, min(100, round(pct))),
                    "resetTime": rt
                })
            
            items.append({"name": f"{title} Quota", "models": models})

        return items


    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the proxy endpoint."""
        
        # Merge options over data so that user edits take effect immediately
        cfg_data = dict(self.entry.data)
        cfg_data.update(self.entry.options)
        
        provider = cfg_data[CONF_PROVIDER]
        auth_index = cfg_data.get(CONF_AUTH_INDEX, "0")
        proxy_token = cfg_data.get(CONF_PROXY_TOKEN, "")
        proxy_url = cfg_data.get(CONF_PROXY_URL, DEFAULT_PROXY_URL)

        req_config = {
            "antigravity": {
                "method": "POST",
                "url": "https://daily-cloudcode-pa.sandbox.googleapis.com/v1internal:fetchAvailableModels",
                "headers": { "User-Agent": "antigravity/1.11.5 windows/amd64" }
            },
            "claude": {
                "method": "GET",
                "url": "https://api.anthropic.com/api/oauth/usage",
                "headers": {"anthropic-beta": "oauth-2025-04-20", "Accept": "application/json"}
            },
            "codex": {
                "method": "GET",
                "url": "https://chatgpt.com/backend-api/wham/usage",
                "headers": { "User-Agent": "codex_cli_rs/0.76.0 (Debian 13.0.0; x86_64) WindowsTerminal" }
            },
            "gemini-cli": {
                "method": "POST",
                "url": "https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota",
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "kiro": {
                "method": "GET",
                "url": "https://api.github.com/copilot_internal",
            },
            "copilot": {
                "method": "GET",
                "url": "https://api.github.com/copilot_internal/billing",
            }
        }

        cfg = req_config.get(provider)
        if not cfg:
            raise UpdateFailed(f"Unknown provider: {provider}")

        headers = {
            "Authorization": "Bearer $TOKEN$",
            "Content-Type": "application/json"
        }
        headers.update(cfg.get("headers", {}))

        req_body = {
            "authIndex": auth_index,
            "method": cfg["method"],
            "url": cfg["url"],
            "header": headers
        }

        if provider == "gemini-cli":
            req_body["data"] = '{"project": ""}'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    proxy_url,
                    json=req_body,
                    headers={
                        "Authorization": f"Bearer {proxy_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=30
                ) as response:
                    
                    if not response.ok:
                        text = await response.text()
                        raise UpdateFailed(f"HTTP error {response.status}: {text}")

                    result = await response.json()
                    status_code = result.get("statusCode") or result.get("status_code", 200)

                    raw_body = result.get("body") or {}
                    if isinstance(raw_body, str):
                        try:
                            raw_body = json.loads(raw_body)
                        except json.JSONDecodeError:
                            raw_body = {}
                    if not isinstance(raw_body, dict):
                        raw_body = {}

                    if not (200 <= status_code < 300):
                        err_msg = json.dumps(raw_body)[:200]
                        raise UpdateFailed(f"API Error {status_code}: {err_msg}")

                    _LOGGER.warning("[AI Quota DEBUG] Provider: %s | Keys: %s | Body: %s",
                                    provider, list(raw_body.keys()), json.dumps(raw_body)[:800])

                    parsed_items = self._parse_provider_data(provider, raw_body)
                    
                    # Detect Plan
                    detected_plan = "Free"
                    if provider == "codex" and raw_body.get("plan_type"):
                        detected_plan = raw_body["plan_type"]
                    elif provider == "claude":
                        extra = raw_body.get("extra_usage")
                        if isinstance(extra, dict) and (extra.get("is_enabled") or extra.get("monthly_limit") is not None):
                            detected_plan = "Team"
                        elif raw_body.get("organization") and isinstance(raw_body["organization"], dict) and raw_body["organization"].get("type"):
                            val = raw_body["organization"]["type"]
                            detected_plan = val[0].upper() + val[1:] if val else "Free"
                            
                    configured_account = cfg_data.get(CONF_ACCOUNT_NAME)
                    return {
                        "plan": detected_plan,
                        "email": configured_account or raw_body.get("email") or result.get("email") or "Unknown Account",
                        "items": parsed_items,
                        "api_payload": raw_body
                    }

        except Exception as err:
            raise UpdateFailed(f"Error communicating with CLIProxyAPI: {err}")
