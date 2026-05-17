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
    CONF_API_KEY,
    CONF_ACCOUNT_NAME,
    CONF_DATA_SOURCE,
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
                remaining_pct = int(quota_data.get("remainingPercentage", 0))
                reset_at = quota_data.get("resetAt", "")
                unlimited = quota_data.get("unlimited", False)
                
                # Calculate percentage (remaining)
                pct = remaining_pct if remaining_pct is not None else 0
                
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
                
                # Format usage info - show actual dollar values
                # The API returns values in dollars already (e.g., 0.21 used, 100 total)
                usage_info = f"${used:.2f} / ${total:.2f}"
                
                if unlimited:
                    usage_info = f"${used:.2f} used (unlimited)"
                
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
                            "usageDisplay": f"${used_dollars:.2f} / ${limit_dollars:.2f}"
                        })
            
            if models:
                plan_name = data.get("plan", "9Router")
                items.append({"name": f"{plan_name} Quota", "models": models})

        return items


    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the proxy endpoint."""
        
        # Merge options over data so that user edits take effect immediately
        cfg_data = dict(self.entry.data)
        cfg_data.update(self.entry.options)
        
        provider = cfg_data[CONF_PROVIDER]
        auth_index = cfg_data.get(CONF_AUTH_INDEX, "0")
        api_key = cfg_data.get(CONF_API_KEY, "")
        proxy_url = cfg_data.get(CONF_PROXY_URL, DEFAULT_PROXY_URL)
        data_source = cfg_data.get(CONF_DATA_SOURCE, "cliproxy")

        # Handle Trouter.click data source - direct API call
        if data_source == "trouter":
            if not api_key:
                raise UpdateFailed("API key is required for Trouter.click data source")
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://trouter.click/api/proxy/me?view=dashboard",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Accept": "*/*",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        },
                        timeout=30
                    ) as response:
                        if not response.ok:
                            text = await response.text()
                            raise UpdateFailed(f"Trouter API error {response.status}: {text[:200]}")
                        
                        raw_body = await response.json()
                        
                        _LOGGER.warning("[AI Quota DEBUG] Trouter.click | Keys: %s | Body: %s",
                                        list(raw_body.keys()), json.dumps(raw_body)[:800])
                        
                        parsed_items = self._parse_provider_data(provider, raw_body)
                        
                        # Extract account info
                        service_name = raw_body.get("sub_service_type_name", "Unknown")
                        key_preview = raw_body.get("key_preview", "Unknown")
                        
                        configured_account = cfg_data.get(CONF_ACCOUNT_NAME)
                        return {
                            "plan": service_name,
                            "email": configured_account or key_preview,
                            "items": parsed_items,
                            "api_payload": raw_body
                        }
            except UpdateFailed:
                raise
            except Exception as err:
                import traceback  # noqa: PLC0415
                _LOGGER.error("[AI Quota CRASH] Trouter.click\n%s", traceback.format_exc())
                raise UpdateFailed(f"Error communicating with Trouter API: {err}")

        # Handle 9Router data source - direct API call (try without auth first, like CLIProxy)
        elif data_source == "9router":
            # For 9router, api_key is the password (optional - try without auth first)
            password = api_key
            
            # Get base URL from proxy_url field (default to localhost)
            base_url = proxy_url if proxy_url and proxy_url != DEFAULT_PROXY_URL else "http://localhost:20128"
            
            try:
                # Create session with explicit cookie jar (unsafe=True to accept cookies from IP addresses)
                cookie_jar = aiohttp.CookieJar(unsafe=True)
                async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
                    # Try to access without authentication first (like CLIProxy on localhost)
                    _LOGGER.debug("[AI Quota] 9Router attempting unauthenticated access to %s", base_url)
                    
                    needs_auth = False
                    
                    # Step 1: Try to get providers list without authentication
                    async with session.get(
                        f"{base_url}/api/providers/client",
                        headers={
                            "Accept": "application/json",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        },
                        timeout=30
                    ) as test_response:
                        if test_response.status == 401:
                            _LOGGER.debug("[AI Quota] 9Router requires authentication")
                            needs_auth = True
                        elif not test_response.ok:
                            text = await test_response.text()
                            raise UpdateFailed(f"9Router API error {test_response.status}: {text[:200]}")
                        else:
                            # Success without auth!
                            _LOGGER.debug("[AI Quota] 9Router access successful without authentication")
                            providers_data = await test_response.json()
                            connections = providers_data.get("connections", [])
                            _LOGGER.debug("[AI Quota DEBUG] 9Router | Found %d connections", len(connections))
                    
                    # Step 2: If authentication is needed, login first
                    if needs_auth:
                        if not password:
                            raise UpdateFailed("9Router requires password for authentication")
                        
                        _LOGGER.debug("[AI Quota] 9Router attempting login with password")
                        
                        async with session.post(
                            f"{base_url}/api/auth/login",
                            json={"password": password},
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                            },
                            timeout=30
                        ) as login_response:
                            login_text = await login_response.text()
                            _LOGGER.debug("[AI Quota] 9Router login response status: %d", login_response.status)
                            _LOGGER.debug("[AI Quota] 9Router login response body: %s", login_text[:500])
                            _LOGGER.debug("[AI Quota] 9Router login response headers: %s", dict(login_response.headers))
                            
                            if not login_response.ok:
                                raise UpdateFailed(f"9Router login failed {login_response.status}: {login_text[:200]}")
                            
                            # Verify login was successful
                            try:
                                login_data = json.loads(login_text)
                                if not login_data.get("success"):
                                    raise UpdateFailed(f"9Router login failed: {login_text[:200]}")
                            except json.JSONDecodeError:
                                _LOGGER.warning("[AI Quota] 9Router login response is not JSON: %s", login_text[:200])
                            
                            _LOGGER.debug("[AI Quota] 9Router login successful, cookies: %s", session.cookie_jar)
                            
                            # Log all cookies for debugging
                            for cookie in session.cookie_jar:
                                _LOGGER.debug("[AI Quota] 9Router cookie: %s=%s (domain=%s, path=%s)", 
                                            cookie.key, cookie.value[:20] if len(cookie.value) > 20 else cookie.value,
                                            cookie.get('domain', 'N/A'), cookie.get('path', 'N/A'))
                        
                        # Now get providers list with authentication
                        async with session.get(
                            f"{base_url}/api/providers/client",
                            headers={
                                "Accept": "application/json",
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                            },
                            timeout=30
                        ) as providers_response:
                            if not providers_response.ok:
                                text = await providers_response.text()
                                raise UpdateFailed(f"9Router providers API error {providers_response.status}: {text[:200]}")
                            
                            providers_data = await providers_response.json()
                            connections = providers_data.get("connections", [])
                            _LOGGER.debug("[AI Quota DEBUG] 9Router | Found %d connections", len(connections))
                    
                    # Step 3: Fetch quota for the specific provider using auth_index
                    target_connection = None
                    
                    # Filter connections by provider name (exact match)
                    # Include both active and inactive accounts
                    matching_connections = []
                    for conn in connections:
                        conn_provider = conn.get("provider", "").lower()
                        config_provider = provider.lower()
                        
                        # Exact match or check if config provider is in the connection provider
                        # e.g., "claude" matches "claude" or "anthropic-compatible-..."
                        if conn_provider == config_provider or config_provider in conn_provider:
                            matching_connections.append(conn)
                            _LOGGER.debug("[AI Quota DEBUG] 9Router | Matched connection: provider='%s', name='%s', active=%s", 
                                          conn_provider, conn.get("name"), conn.get("isActive"))
                    
                    _LOGGER.debug("[AI Quota DEBUG] 9Router | Found %d matching connections for provider '%s'", 
                                  len(matching_connections), provider)
                    
                    # Use auth_index to select which account (0 = first, 1 = second, etc.)
                    auth_idx = int(auth_index) if auth_index else 0
                    if auth_idx < len(matching_connections):
                        target_connection = matching_connections[auth_idx]
                        _LOGGER.debug("[AI Quota DEBUG] 9Router | Selected connection at index %d: %s", 
                                      auth_idx, target_connection.get("name"))
                    elif matching_connections:
                        # If auth_index is out of range, use the first one
                        target_connection = matching_connections[0]
                        _LOGGER.warning("[AI Quota] 9Router | Auth index %d out of range, using first connection", auth_idx)
                    
                    # If no match found, use the first active connection
                    if not target_connection:
                        for conn in connections:
                            if conn.get("isActive", False):
                                target_connection = conn
                                _LOGGER.warning("[AI Quota] 9Router | No matching provider found, using first active connection")
                                break
                    
                    if not target_connection:
                        raise UpdateFailed("No active 9Router connections found")
                    
                    connection_id = target_connection.get("id")
                    connection_name = target_connection.get("name", "Unknown")
                    connection_email = target_connection.get("email") or connection_name
                    
                    _LOGGER.debug("[AI Quota DEBUG] 9Router | Using connection: %s (%s)", connection_name, connection_id)
                    
                    # Step 4: Fetch quota for this connection
                    async with session.get(
                        f"{base_url}/api/usage/{connection_id}",
                        headers={
                            "Accept": "application/json",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        },
                        timeout=30
                    ) as quota_response:
                        if not quota_response.ok:
                            text = await quota_response.text()
                            raise UpdateFailed(f"9Router quota API error {quota_response.status}: {text[:200]}")
                        
                        raw_body = await quota_response.json()
                        
                        _LOGGER.warning("[AI Quota DEBUG] 9Router | Connection: %s | Keys: %s | Body: %s",
                                        connection_name, list(raw_body.keys()), json.dumps(raw_body)[:800])
                        
                        # Parse using 9router parser
                        parsed_items = self._parse_provider_data("9router", raw_body)
                        
                        plan_name = raw_body.get("plan", "9Router")
                        
                        return {
                            "plan": plan_name,
                            "email": connection_email,
                            "items": parsed_items,
                            "api_payload": raw_body
                        }
            except UpdateFailed:
                raise
            except Exception as err:
                import traceback  # noqa: PLC0415
                _LOGGER.error("[AI Quota CRASH] 9Router\n%s", traceback.format_exc())
                raise UpdateFailed(f"Error communicating with 9Router API: {err}")

        # Handle CLIProxy data source - proxy-based collection
        # This is the original method for all providers through CLIProxyAPI
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
            },
            "trouter": {
                "method": "GET",
                "url": "https://trouter.click/api/proxy/me?view=dashboard",
                "headers": {
                    "Accept": "*/*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
                }
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
                        "Authorization": f"Bearer {api_key}",
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

        except UpdateFailed:
            raise
        except Exception as err:
            import traceback  # noqa: PLC0415
            _LOGGER.error("[AI Quota CRASH] Provider=%s\n%s", provider, traceback.format_exc())
            raise UpdateFailed(f"Error communicating with CLIProxyAPI: {err}")
