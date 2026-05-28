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
    CONF_API_KEY,
    CONF_DATA_SOURCE,
    CONF_SESSION_TOKEN,
    CONF_ACCOUNT_LABEL,
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

    def _get_dynamic_name(self, default_label: str, fallback: str, jwt_token: str = None, api_name: str = None) -> str:
        """Determine best name to show from token or API if the user didn't provide a custom label."""
        if default_label and default_label not in ("Claude", "Codex", "Antigravity"):
            return default_label
        
        if api_name:
            return api_name
            
        if jwt_token:
            try:
                import json
                import base64
                parts = jwt_token.split(".")
                if len(parts) >= 2:
                    padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
                    data = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
                    email = data.get("email") or data.get("unique_name") or data.get("name")
                    if email:
                        return email
            except Exception:
                pass
                
        return fallback

    def _parse_provider_data(self, provider: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Ported logic from ai-quota-card.js to parse the response payload natively."""
        if not data or not isinstance(data, dict):
            _LOGGER.warning("[AI Quota] %s returned empty or non-dict body: %s", provider, data)
            return []
        items = []

        if provider == "antigravity":
            groups = {}
            models_data = data.get("models", {})
            for key, m_data in models_data.items():
                name = m_data.get("displayName") or m_data.get("display_name") or key
                if not m_data.get("displayName") and not m_data.get("display_name"):
                    if key == 'rev19-uic3-1p': name = 'Gemini 2.5 Computer Use'
                    elif key == 'gemini-3-pro-image': name = 'Gemini 3 Pro Image'
                    elif key == 'gemini-2.5-flash-lite': name = 'Gemini 2.5 Flash Lite'
                    elif key == 'gemini-2.5-flash': name = 'Gemini 2.5 Flash'
                    elif key == 'Gemini-Pro-Agent': name = 'Gemini 3.1 Pro (High)'
                    elif key == 'Gemini-3-Flash-Agent': name = 'Gemini 3.5 Flash (High)'
                    elif key == 'Gemini-3.5-Flash-Low': name = 'Gemini 3.5 Flash (Medium)'
                    elif key == 'Gemini-3.1-Pro-Low': name = 'Gemini 3.1 Pro (Low)'
                    elif key == 'Claude-Opus-4-6-Thinking': name = 'Claude Opus 4.6 (Thinking)'
                    elif key == 'Claude-Sonnet-4-6': name = 'Claude Sonnet 4.6 (Thinking)'
                    elif key == 'Gpt-Oss-120B-Medium': name = 'GPT-OSS 120B (Medium)'
                    elif key == 'Gemini-3-Flash': name = 'Gemini 3 Flash'

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

            def process_win(name: str, win):
                if not win or not isinstance(win, dict):
                    return
                pct = 0
                if win.get("used_percent") is not None:
                    pct = max(0, min(100, round(100 - float(win["used_percent"]))))
                else:
                    remaining = float(win.get("remaining_count") or 0)
                    total = float(win.get("total_count") or 1)
                    pct = max(0, min(100, round((remaining / max(total, 1)) * 100)))

                rt = ""
                reset_at = win.get("reset_at")
                if reset_at and float(reset_at) > 0:
                    target_ms = float(reset_at)
                    # reset_at is Unix seconds, convert to ms
                    if target_ms < 10_000_000_000:
                        target_ms *= 1000
                    rt = self._format_reset_time(target_ms)
                elif win.get("reset_after_seconds") and float(win["reset_after_seconds"]) > 0:
                    import time as _time  # noqa: PLC0415
                    rt = self._format_reset_time((_time.time() + float(win["reset_after_seconds"])) * 1000)

                limits.append({"name": name, "percentage": pct, "resetTime": rt})

            # Use `or {}` so null JSON values don't crash .get() calls
            rl = data.get("rate_limit") or {}
            crl = data.get("code_review_rate_limit") or {}

            plan_type = (data.get("plan_type") or "plus").lower()

            if plan_type == "free":
                process_win("Weekly limit", rl.get("primary_window"))
            else:
                # primary_window = 5-hour (18000s), secondary_window = weekly
                process_win("5-hour limit", rl.get("primary_window"))
                process_win("Weekly limit", rl.get("secondary_window"))

            # Code review windows (null for most accounts)
            process_win("Code review limit", crl.get("primary_window"))

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

        elif provider == "trouter":
            models = []
            
            # Parse quota information
            quota = data.get("quota") or {}
            if quota:
                quota_type = quota.get("type", "duration")
                
                if quota_type == "duration":
                    # Duration-based quota (in seconds)
                    daily_quota = float(quota.get("daily_quota", 0))
                    daily_remaining = float(quota.get("daily_remaining", 0))
                    daily_spent = float(quota.get("daily_spent", 0))
                    
                    if daily_quota > 0:
                        pct = max(0, min(100, round((daily_remaining / daily_quota) * 100)))
                    else:
                        pct = 0
                    
                    # Convert seconds to hours for display
                    spent_hours = daily_spent / 3600
                    total_hours = daily_quota / 3600
                    
                    next_reset = quota.get("next_reset_at", "")
                    if next_reset:
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(next_reset.replace("Z", "+00:00"))
                            reset_str = dt.isoformat()
                        except Exception:
                            reset_str = next_reset
                    else:
                        reset_str = ""
                    
                    models.append({
                        "name": "Daily Duration Quota",
                        "percentage": pct,
                        "resetTime": f"{spent_hours:.2f}h / {total_hours:.2f}h | Reset: {reset_str}"
                    })
                
                elif quota_type == "count":
                    # Count-based quota
                    remaining = float(quota.get("remaining_quota", 0))
                    # We need to calculate total from remaining + used
                    # For now, just show remaining
                    models.append({
                        "name": "Request Quota",
                        "percentage": 100 if remaining > 0 else 0,
                        "resetTime": f"{int(remaining)} remaining"
                    })
            
            # Parse usage statistics
            usage = data.get("usage") or {}
            if usage:
                total_spent = float(usage.get("total_spent", 0))
                daily_spent = float(usage.get("daily_spent", 0))
                request_count = usage.get("request_count", 0)
                daily_request_count = usage.get("daily_request_count", 0)
                
                # Total spend
                models.append({
                    "name": "Lifetime Spend",
                    "percentage": 100,  # Informational only
                    "resetTime": f"${total_spent / 100:.2f}"
                })
                
                # Daily spend
                models.append({
                    "name": "Daily Spend",
                    "percentage": 100,  # Informational only
                    "resetTime": f"${daily_spent / 100:.2f}"
                })
                
                # Request counts
                models.append({
                    "name": "Total Requests",
                    "percentage": 100,  # Informational only
                    "resetTime": f"{request_count} total ({daily_request_count} today)"
                })
                
                # Token usage if available
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                cache_read = usage.get("cache_read_tokens", 0)
                cache_write = usage.get("cache_write_tokens", 0)
                
                if input_tokens or output_tokens:
                    total_tokens = input_tokens + output_tokens + cache_read + cache_write
                    models.append({
                        "name": "Token Usage",
                        "percentage": 100,  # Informational only
                        "resetTime": f"{total_tokens:,} tokens (I:{input_tokens:,} O:{output_tokens:,})"
                    })
            
            # Parse API key status
            status = data.get("status", "unknown")
            timestamps = data.get("timestamps") or {}
            
            if timestamps:
                expires_at = timestamps.get("expires_at", "")
                last_used = timestamps.get("last_used_at", "")
                
                # Calculate if key is active based on expiration
                is_active = status == "active"
                pct = 100 if is_active else 0
                
                expire_info = ""
                if expires_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                        expire_info = f"Expires: {dt.strftime('%Y-%m-%d %H:%M')}"
                    except Exception:
                        expire_info = f"Expires: {expires_at}"
                
                models.append({
                    "name": "API Key Status",
                    "percentage": pct,
                    "resetTime": expire_info
                })
            
            # Service type info
            service_type = data.get("service_type", "")
            sub_service_name = data.get("sub_service_type_name", "")
            if service_type or sub_service_name:
                service_info = f"{service_type.upper()}" if service_type else ""
                if sub_service_name:
                    service_info = f"{service_info} - {sub_service_name}" if service_info else sub_service_name
                
                models.append({
                    "name": "Service Type",
                    "percentage": 100,  # Informational only
                    "resetTime": service_info
                })
            
            if models:
                items.append({"name": "Trouter Quota", "models": models})

        elif provider == "9router":
            models = []
            
            # Parse quotas from 9router response
            quotas = data.get("quotas") or {}
            
            for quota_name, quota_data in quotas.items():
                if not isinstance(quota_data, dict):
                    continue
                
                used = float(quota_data.get("used", 0))
                total = float(quota_data.get("total", 100))
                remaining = float(quota_data.get("remaining", 0))
                remaining_pct = quota_data.get("remainingPercentage")
                reset_at = quota_data.get("resetAt", "")
                unlimited = quota_data.get("unlimited", False)
                
                # Calculate percentage (remaining)
                if remaining_pct is not None:
                    pct = int(remaining_pct)
                elif total > 0:
                    pct = max(0, min(100, round((remaining / total) * 100)))
                else:
                    pct = 0
                    
                # Format reset time and expiration countdown
                reset_str = ""
                expires_in = ""
                if reset_at:
                    try:
                        from datetime import datetime
                        # Parse the reset time (UTC)
                        dt_utc = datetime.fromisoformat(reset_at.replace("Z", "+00:00"))
                        
                        # Convert to Home Assistant timezone
                        dt_local = dt_utc.astimezone()
                        
                        # Format as "yyyy-mm-dd hh:mm:ss"
                        reset_str = dt_local.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Calculate time remaining for "Expires in" display
                        now = datetime.now(dt_local.tzinfo)
                        diff = dt_local - now
                        
                        if diff.total_seconds() > 0:
                            days = diff.days
                            hours = diff.seconds // 3600
                            minutes = (diff.seconds % 3600) // 60
                            
                            if days > 0:
                                expires_in = f"{days}d {hours}h {minutes}m"
                            elif hours > 0:
                                expires_in = f"{hours}h {minutes}m"
                            else:
                                expires_in = f"{minutes}m"
                        else:
                            expires_in = "Expired"
                    except Exception as e:
                        _LOGGER.warning("[AI Quota] Failed to parse reset time for 9router: %s", e)
                        reset_str = reset_at
                        expires_in = ""
                
                # Format display name
                display_name = quota_name.replace("(", "").replace(")", "").title()
                
                # Format usage info - numeric only (no currency symbol)
                # API values are already normalized to plan units.
                usage_info = f"{used:.2f} / {total:.2f}"

                if unlimited:
                    usage_info = f"{used:.2f} used (unlimited)"

                models.append({
                    "name": display_name,
                    "percentage": pct,
                    "resetTime": reset_str,
                    "expiresIn": expires_in,
                    "usage": used,
                    "limit": total,
                    "usageDisplay": usage_info
                })
            
            # Add extra usage info if available (for Claude Code plan)
            extra_usage = data.get("extraUsage")
            if extra_usage and isinstance(extra_usage, dict):
                if extra_usage.get("is_enabled"):
                    used_credits = float(extra_usage.get("used_credits", 0))
                    monthly_limit = float(extra_usage.get("monthly_limit", 0))
                    utilization = float(extra_usage.get("utilization", 0))
                    currency = extra_usage.get("currency", "USD")
                    reset_at_extra = extra_usage.get("resetAt", "")
                    
                    if monthly_limit > 0:
                        pct = max(0, min(100, round(100 - utilization)))
                        
                        # Format reset time for extra usage
                        reset_str_extra = ""
                        expires_in_extra = ""
                        if reset_at_extra:
                            try:
                                from datetime import datetime
                                dt_utc = datetime.fromisoformat(reset_at_extra.replace("Z", "+00:00"))
                                dt_local = dt_utc.astimezone()
                                reset_str_extra = dt_local.strftime("%Y-%m-%d %H:%M:%S")
                                
                                now = datetime.now(dt_local.tzinfo)
                                diff = dt_local - now
                                
                                if diff.total_seconds() > 0:
                                    days = diff.days
                                    hours = diff.seconds // 3600
                                    minutes = (diff.seconds % 3600) // 60
                                    
                                    if days > 0:
                                        expires_in_extra = f"{days}d {hours}h {minutes}m"
                                    elif hours > 0:
                                        expires_in_extra = f"{hours}h {minutes}m"
                                    else:
                                        expires_in_extra = f"{minutes}m"
                                else:
                                    expires_in_extra = "Expired"
                            except Exception:
                                pass
                        
                        used_dollars = used_credits / 100
                        limit_dollars = monthly_limit / 100
                        
                        models.append({
                            "name": "Extra Usage",
                            "percentage": pct,
                            "resetTime": reset_str_extra,
                            "expiresIn": expires_in_extra,
                            "usage": used_dollars,
                            "limit": limit_dollars,
                            "usageDisplay": f"{used_dollars:.2f} / {limit_dollars:.2f}"
                        })
            
            if models:
                plan_name = data.get("plan", "9Router")
                items.append({"name": f"{plan_name} Quota", "models": models})

        return items


    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API for all connections."""
        cfg_data = self.entry.data
        data_source = cfg_data.get("data_source", "9router")
        proxy_url = cfg_data.get("proxy_url", "http://localhost:20128")
        api_key = cfg_data.get("api_key", "")
        
        result_data = {"connections": {}}
        
        if data_source == "trouter":
            # Trouter can have multiple API keys separated by comma or newline
            api_keys = [k.strip() for k in api_key.replace(",", "\n").split("\n") if k.strip()]
            
            if not api_keys:
                return result_data
                
            try:
                async with aiohttp.ClientSession() as session:
                    for idx, key in enumerate(api_keys):
                        try:
                            async with session.get(
                                "https://trouter.click/api/proxy/me?view=dashboard",
                                headers={
                                    "Authorization": f"Bearer {key}",
                                    "Accept": "application/json",
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                },
                                timeout=30
                            ) as response:
                                if not response.ok:
                                    _LOGGER.warning("[AI Quota] Trouter API error for key %d: %s", idx+1, response.status)
                                    continue
                                
                                raw_body = await response.json()
                                parsed_items = self._parse_provider_data("trouter", raw_body)
                                service_name = raw_body.get("plan", "Trouter")
                                key_preview = raw_body.get("key_preview", f"Key {idx+1}")
                                
                                import hashlib
                                key_hash = hashlib.md5(str(key).encode('utf-8')).hexdigest()[:10]
                                conn_id = f"trouter_{key_hash}"
                                result_data["connections"][conn_id] = {
                                    "id": conn_id,
                                    "provider": "trouter",
                                    "name": key_preview,
                                    "email": key_preview,
                                    "plan": service_name,
                                    "isActive": True,
                                    "items": parsed_items,
                                    "api_payload": raw_body
                                }
                        except Exception as e:
                            _LOGGER.warning("[AI Quota] Failed to fetch Trouter key %d: %s", idx+1, e)
            except Exception as err:
                raise UpdateFailed(f"Error communicating with Trouter API: {err}")
                
        elif data_source == "9router":
            base_url = proxy_url if proxy_url and proxy_url != "https://ai.wolfz.shop/v0/management/api-call" else "http://localhost:20128"
            password = api_key
            
            try:
                cookie_jar = aiohttp.CookieJar(unsafe=True)
                async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
                    # 1. Login
                    if password:
                        _LOGGER.debug("[AI Quota] 9Router attempting login")
                        async with session.post(
                            f"{base_url}/api/auth/login",
                            json={"password": password},
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                            },
                            timeout=30
                        ) as login_response:
                            login_text = await login_response.text()
                            if not login_response.ok:
                                raise UpdateFailed(f"9Router login failed {login_response.status}: {login_text[:200]}")
                            try:
                                login_data = json.loads(login_text)
                                if not login_data.get("success"):
                                    raise UpdateFailed(f"9Router login failed: {login_text[:200]}")
                            except json.JSONDecodeError:
                                pass
                                
                    # 2. Get providers/connections
                    async with session.get(
                        f"{base_url}/api/providers/client",
                        headers={"Accept": "application/json"},
                        timeout=30
                    ) as providers_response:
                        if not providers_response.ok:
                            raise UpdateFailed(f"9Router providers failed: {providers_response.status}")
                        providers_data = await providers_response.json()
                        connections = providers_data.get("connections", [])
                        
                    # 3. Fetch usage for each connection
                    for conn in connections:
                        conn_id = conn.get("id")
                        if not conn_id:
                            continue
                            
                        conn_provider = conn.get("provider", "unknown")
                        conn_name = conn.get("name", "Unknown")
                        
                        # Use provider from connection to parse data. Custom providers start with 'anthropic-compatible' etc.
                        parser_provider = conn_provider.lower()
                        if "claude" in parser_provider or "anthropic" in parser_provider:
                            parser_provider = "claude"
                        elif "codex" in parser_provider or "openai" in parser_provider or "chatgpt" in parser_provider:
                            parser_provider = "codex"
                        elif "gemini" in parser_provider:
                            parser_provider = "gemini-cli"
                            
                        try:
                            async with session.get(
                                f"{base_url}/api/usage/{conn_id}",
                                headers={"Accept": "application/json"},
                                timeout=30
                            ) as quota_response:
                                if quota_response.ok:
                                    raw_body = await quota_response.json()
                                    if raw_body.get("message") == "Usage not available for this connection":
                                        continue # Skip
                                        
                                    parsed_items = self._parse_provider_data("9router", raw_body)
                                    plan_name = raw_body.get("plan", "Unknown Plan")
                                    
                                    result_data["connections"][conn_id] = {
                                        "id": conn_id,
                                        "provider": conn_provider,
                                        "name": conn_name,
                                        "email": conn.get("email") or conn_name,
                                        "plan": plan_name,
                                        "isActive": conn.get("isActive", False),
                                        "items": parsed_items,
                                        "api_payload": raw_body
                                    }
                        except Exception as e:
                            _LOGGER.warning("[AI Quota] Failed to fetch usage for %s: %s", conn_name, e)
                            
            except Exception as err:
                raise UpdateFailed(f"Error communicating with 9Router API: {err}")

        elif data_source == "claude_direct":
            session_token = cfg_data.get(CONF_SESSION_TOKEN, "")
            account_label = cfg_data.get(CONF_ACCOUNT_LABEL, "Claude")
            if not session_token:
                raise UpdateFailed("Claude direct: no session token configured")

            headers = {
                "Cookie": f"sessionKey={session_token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Referer": "https://claude.ai/",
            }

            try:
                async with aiohttp.ClientSession() as session:
                    # 1. Resolve organisation ID
                    async with session.get(
                        "https://claude.ai/api/organizations",
                        headers=headers,
                        timeout=30,
                    ) as resp:
                        if resp.status in (401, 403):
                            raise UpdateFailed("Claude direct: session token expired or invalid")
                        if not resp.ok:
                            raise UpdateFailed(f"Claude direct: organisations request failed {resp.status}")
                        orgs = await resp.json()

                    if not orgs or not isinstance(orgs, list):
                        raise UpdateFailed("Claude direct: unexpected organisations response")

                    org_id = orgs[0].get("uuid") or orgs[0].get("id")
                    if not org_id:
                        raise UpdateFailed("Claude direct: could not resolve organisation ID")

                    # 2. Fetch usage
                    async with session.get(
                        f"https://claude.ai/api/organizations/{org_id}/usage",
                        headers=headers,
                        timeout=30,
                    ) as resp:
                        if not resp.ok:
                            raise UpdateFailed(f"Claude direct: usage request failed {resp.status}")
                        raw_body = await resp.json()

                    # 3. Optional: routine run budget
                    routines_data = None
                    try:
                        async with session.get(
                            "https://claude.ai/v1/code/routines/run-budget",
                            headers=headers,
                            timeout=15,
                        ) as resp:
                            if resp.ok:
                                routines_data = await resp.json()
                    except Exception:
                        pass  # routines are optional

                    if routines_data and isinstance(routines_data, dict):
                        raw_body["routines"] = routines_data

                    parsed_items = self._parse_provider_data("claude", raw_body)

                    import hashlib
                    token_hash = hashlib.md5(session_token.encode("utf-8")).hexdigest()[:10]
                    conn_id = f"claude_direct_{token_hash}"

                    org_name = orgs[0].get("name")
                    final_name = self._get_dynamic_name(account_label, "Claude", api_name=org_name)

                    result_data["connections"][conn_id] = {
                        "id": conn_id,
                        "provider": "claude_direct",
                        "name": final_name,
                        "email": org_name or final_name,
                        "plan": orgs[0].get("plan_name", "Claude Subscription"),
                        "isActive": True,
                        "items": parsed_items,
                        "api_payload": raw_body,
                    }
            except UpdateFailed:
                raise
            except Exception as err:
                raise UpdateFailed(f"Error communicating with Claude API: {err}")

        elif data_source == "codex_direct":
            session_token = cfg_data.get(CONF_SESSION_TOKEN, "")
            account_label = cfg_data.get(CONF_ACCOUNT_LABEL, "Codex")
            if not session_token:
                raise UpdateFailed("Codex direct: no session token configured")

            headers = {
                "Authorization": f"Bearer {session_token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://chatgpt.com/backend-api/codex/usage",
                        headers=headers,
                        timeout=30,
                    ) as resp:
                        if resp.status in (401, 403):
                            raise UpdateFailed("Codex direct: session token expired or invalid")
                        if not resp.ok:
                            raise UpdateFailed(f"Codex direct: usage request failed {resp.status}")
                        raw_body = await resp.json()

                parsed_items = self._parse_provider_data("codex", raw_body)

                import hashlib
                token_hash = hashlib.md5(session_token.encode("utf-8")).hexdigest()[:10]
                conn_id = f"codex_direct_{token_hash}"

                final_name = self._get_dynamic_name(account_label, "Codex", jwt_token=session_token)

                result_data["connections"][conn_id] = {
                    "id": conn_id,
                    "provider": "codex_direct",
                    "name": final_name,
                    "email": final_name,
                    "plan": raw_body.get("plan_type", "Codex Subscription"),
                    "isActive": True,
                    "items": parsed_items,
                    "api_payload": raw_body,
                }
            except UpdateFailed:
                raise
            except Exception as err:
                raise UpdateFailed(f"Error communicating with Codex API: {err}")

        elif data_source == "antigravity_direct":
            session_token = cfg_data.get(CONF_SESSION_TOKEN, "")
            account_label = cfg_data.get(CONF_ACCOUNT_LABEL, "Antigravity")
            if not session_token:
                raise UpdateFailed("Antigravity direct: no session token configured")

            headers = {
                "Authorization": f"Bearer {session_token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            }

            # Try primary Antigravity quota endpoint, fall back to CLIProxy-style endpoint
            quota_urls = [
                "https://colab.research.google.com/api/quota",
                "https://labs.google/api/quota",
            ]

            try:
                raw_body = None
                async with aiohttp.ClientSession() as session:
                    for url in quota_urls:
                        try:
                            async with session.get(
                                url,
                                headers=headers,
                                timeout=20,
                            ) as resp:
                                if resp.status in (401, 403):
                                    raise UpdateFailed("Antigravity direct: bearer token expired or invalid")
                                if resp.ok:
                                    raw_body = await resp.json()
                                    _LOGGER.debug("[AI Quota] Antigravity direct: got data from %s", url)
                                    break
                        except UpdateFailed:
                            raise
                        except Exception as e:
                            _LOGGER.debug("[AI Quota] Antigravity direct: %s failed: %s", url, e)
                            continue

                if not raw_body:
                    raise UpdateFailed("Antigravity direct: all quota endpoints failed")

                parsed_items = self._parse_provider_data("antigravity", raw_body)

                import hashlib
                token_hash = hashlib.md5(session_token.encode("utf-8")).hexdigest()[:10]
                conn_id = f"antigravity_direct_{token_hash}"

                api_email = raw_body.get("email") if isinstance(raw_body, dict) else None
                final_name = self._get_dynamic_name(account_label, "Antigravity", jwt_token=session_token, api_name=api_email)

                result_data["connections"][conn_id] = {
                    "id": conn_id,
                    "provider": "antigravity_direct",
                    "name": final_name,
                    "email": final_name,
                    "plan": "Antigravity",
                    "isActive": True,
                    "items": parsed_items,
                    "api_payload": raw_body,
                }
            except UpdateFailed:
                raise
            except Exception as err:
                raise UpdateFailed(f"Error communicating with Antigravity API: {err}")

        return result_data
