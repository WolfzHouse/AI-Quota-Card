"""Config flow for AI Web Quota integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_PROXY_URL,
    CONF_API_KEY,
    CONF_DATA_SOURCE,
    CONF_SESSION_TOKEN,
    CONF_ACCOUNT_LABEL,
    DATA_SOURCES,
    DIRECT_PROVIDERS,
)

_LOGGER = logging.getLogger(__name__)


class AIQuotaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AI Web Quota."""

    VERSION = 2  # Bumped to v2 for hub architecture

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - show menu."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["api_proxy", "trouter", "direct_provider"]
        )

    async def async_step_api_proxy(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle API Proxy (CLIProxy/9Router) configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Generate a unique_id based on data source and URL
            base_url = user_input.get(CONF_PROXY_URL, "http://localhost:20128")
            unique_id = f"{user_input[CONF_DATA_SOURCE]}_{base_url}"
            
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            
            # Create the entry title
            data_source_name = DATA_SOURCES.get(user_input[CONF_DATA_SOURCE], user_input[CONF_DATA_SOURCE])
            title = f"{data_source_name} ({base_url})"
            return self.async_create_entry(title=title, data=user_input)

        # Schema for API Proxy sources
        api_proxy_sources = [
            selector.SelectOptionDict(value="cliproxy", label="CLIProxy"),
            selector.SelectOptionDict(value="9router", label="9Router"),
        ]

        schema = vol.Schema(
            {
                vol.Required(CONF_DATA_SOURCE, default="9router"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=api_proxy_sources,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_PROXY_URL, default="http://localhost:20128"): str,
                vol.Optional(CONF_API_KEY, default=""): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
            }
        )

        return self.async_show_form(
            step_id="api_proxy",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "info": "Configure CLIProxy or 9Router hub. All accounts will be auto-discovered."
            }
        )

    async def async_step_trouter(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Trouter configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate API key is provided
            if not user_input.get(CONF_API_KEY):
                errors["base"] = "api_key_required"
            
            if not errors:
                # Add data_source to user_input
                user_input[CONF_DATA_SOURCE] = "trouter"
                
                import hashlib
                api_key = user_input[CONF_API_KEY]
                api_key_hash = hashlib.md5(str(api_key).encode('utf-8')).hexdigest()[:10]
                unique_id = f"trouter_{api_key_hash}"
                
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                # Create the entry title
                title = "Trouter.click"
                return self.async_create_entry(title=title, data=user_input)

        # Schema for Trouter
        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
            }
        )

        return self.async_show_form(
            step_id="trouter",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "info": "Configure Trouter.click hub. You can enter multiple API keys separated by commas."
            }
        )


    # Static login URLs for Claude and Antigravity (no PKCE needed — token extracted from redirect)
    _STATIC_OAUTH_URLS: dict[str, str] = {
        "claude_direct": (
            "**Step 1**: Open this link and log in: [https://claude.ai/login](https://claude.ai/login)\n\n"
            "After logging in, copy the **full URL** from your browser's address bar "
            "(it will contain `sessionKey=...`) and paste it below."
        ),
        "antigravity_direct": (
            "**Step 1**: Open your Antigravity IDE Settings → Accounts → Copy Bearer Token\n\n"
            "(Alternatively, open `%APPDATA%\\antigravity\\auth.json` and copy the `access_token`).\n\n"
            "Paste the raw token in the field below."
        ),
    }

    # Codex CLI OAuth constants (PKCE / authorization-code flow)
    _CODEX_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
    _CODEX_REDIRECT_URI = "http://localhost:1455/auth/callback"
    _CODEX_AUTH_URL = "https://auth.openai.com/oauth/authorize"
    _CODEX_TOKEN_URL = "https://auth.openai.com/oauth/token"

    # ------------------------------------------------------------------ #
    # Step 1 — pick provider
    # ------------------------------------------------------------------ #

    async def async_step_direct_provider(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1 — choose provider and show the login URL."""
        if user_input is not None:
            self._direct_data_source = user_input.get(CONF_DATA_SOURCE, "claude_direct")
            self._direct_account_label = user_input.get(CONF_ACCOUNT_LABEL, "").strip()
            return await self.async_step_direct_oauth()

        provider_options = [
            selector.SelectOptionDict(value="claude_direct", label="Claude (claude.ai)"),
            selector.SelectOptionDict(value="codex_direct", label="Codex (chatgpt.com)"),
            selector.SelectOptionDict(value="antigravity_direct", label="Antigravity"),
        ]

        schema = vol.Schema(
            {
                vol.Required(CONF_DATA_SOURCE, default="claude_direct"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=provider_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_ACCOUNT_LABEL, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="direct_provider",
            data_schema=schema,
            errors={},
        )

    # ------------------------------------------------------------------ #
    # Step 2 — generate OAuth URL, accept pasted redirect, get token
    # ------------------------------------------------------------------ #

    async def async_step_direct_oauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2 — show OAuth login URL, accept pasted redirect URL, extract/exchange token."""
        import hashlib
        import secrets
        import base64
        import aiohttp
        from urllib.parse import urlencode, quote

        data_source = getattr(self, "_direct_data_source", "claude_direct")
        account_label = getattr(self, "_direct_account_label", "")
        provider_label = DIRECT_PROVIDERS.get(data_source, data_source)

        # ---- Build the OAuth URL (first call: no user_input yet) ---- #
        # For Codex: generate PKCE verifier/challenge + state if not already done
        if data_source == "codex_direct" and not hasattr(self, "_codex_verifier"):
            verifier = secrets.token_urlsafe(43)          # 43-char url-safe random string
            challenge = base64.urlsafe_b64encode(
                hashlib.sha256(verifier.encode("ascii")).digest()
            ).rstrip(b"=").decode("ascii")
            state = secrets.token_urlsafe(32)
            self._codex_verifier = verifier
            self._codex_state = state
            params = urlencode({
                "response_type": "code",
                "client_id": self._CODEX_CLIENT_ID,
                "redirect_uri": self._CODEX_REDIRECT_URI,
                "scope": "openid profile email offline_access",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "id_token_add_organizations": "true",
                "codex_cli_simplified_flow": "true",
                "originator": "codex_cli_rs",
                "state": state,
            })
            oauth_url = f"{self._CODEX_AUTH_URL}?{params}"
            instructions = (
                f"**Step 1**: Open this link and log in: [Login to Codex]({oauth_url})\n\n"
                "After signing in, your browser will redirect to `localhost:1455` (which is not running, "
                "so you’ll get a ‘connection refused’ error — that’s expected). "
                "Copy the **full URL** from the address bar anyway and paste it below."
            )
        elif data_source == "codex_direct":
            # Re-render the form with the same URL (e.g., on validation error)
            verifier = self._codex_verifier
            challenge = base64.urlsafe_b64encode(
                hashlib.sha256(verifier.encode("ascii")).digest()
            ).rstrip(b"=").decode("ascii")
            params = urlencode({
                "response_type": "code",
                "client_id": self._CODEX_CLIENT_ID,
                "redirect_uri": self._CODEX_REDIRECT_URI,
                "scope": "openid profile email offline_access",
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "id_token_add_organizations": "true",
                "codex_cli_simplified_flow": "true",
                "originator": "codex_cli_rs",
                "state": self._codex_state,
            })
            oauth_url = f"{self._CODEX_AUTH_URL}?{params}"
            instructions = (
                f"**Step 1**: Open this link and log in: [Login to Codex]({oauth_url})\n\n"
                "After signing in your browser will redirect to `localhost:1455` (which is not running — "
                "that’s normal). Copy the **full URL** from the address bar and paste it below."
            )
        else:
            instructions = self._STATIC_OAUTH_URLS.get(
                data_source,
                "Paste your token below."
            )
            oauth_url = ""

        errors: dict[str, str] = {}

        if user_input is not None:
            redirect_url = (user_input.get("redirect_url") or "").strip()
            if not redirect_url:
                errors["base"] = "session_token_required"
            else:
                session_token: str | None = None

                # ---- Codex: PKCE code exchange ---- #
                if data_source == "codex_direct":
                    from urllib.parse import urlparse, parse_qs
                    auth_code = self._extract_codex_code(redirect_url)
                    if not auth_code:
                        errors["base"] = "invalid_session"
                    else:
                        # Verify state if present
                        parsed = urlparse(redirect_url)
                        qs_params = parse_qs(parsed.query)
                        returned_state = (qs_params.get("state") or [""])[0]
                        if returned_state and returned_state != getattr(self, "_codex_state", ""):
                            errors["base"] = "invalid_session"
                        else:
                            try:
                                async with aiohttp.ClientSession() as http:
                                    async with http.post(
                                        self._CODEX_TOKEN_URL,
                                        json={
                                            "grant_type": "authorization_code",
                                            "code": auth_code,
                                            "redirect_uri": self._CODEX_REDIRECT_URI,
                                            "client_id": self._CODEX_CLIENT_ID,
                                            "code_verifier": self._codex_verifier,
                                        },
                                        headers={"Content-Type": "application/json"},
                                        timeout=20,
                                    ) as resp:
                                        if not resp.ok:
                                            _LOGGER.debug(
                                                "[AI Quota] Codex token exchange failed: %s %s",
                                                resp.status, await resp.text()
                                            )
                                            errors["base"] = "invalid_session"
                                        else:
                                            token_data = await resp.json()
                                            session_token = (
                                                token_data.get("access_token")
                                                or token_data.get("id_token")
                                            )
                                            if not session_token:
                                                errors["base"] = "invalid_session"
                            except aiohttp.ClientError:
                                errors["base"] = "cannot_connect"
                            except Exception:  # noqa: BLE001
                                errors["base"] = "unknown"

                # ---- Claude / Antigravity: extract token from URL ---- #
                else:
                    session_token = self._extract_token_from_url(data_source, redirect_url)
                    if not session_token:
                        errors["base"] = "invalid_session"

                # ---- Validate extracted/exchanged token ---- #
                if not errors and session_token:
                    try:
                        async with aiohttp.ClientSession() as http:
                            if data_source == "claude_direct":
                                async with http.get(
                                    "https://claude.ai/api/organizations",
                                    headers={
                                        "Cookie": f"sessionKey={session_token}",
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                    },
                                    timeout=15,
                                ) as resp:
                                    if resp.status in (401, 403):
                                        errors["base"] = "invalid_session"
                                    elif not resp.ok:
                                        errors["base"] = "cannot_connect"
                            elif data_source == "codex_direct":
                                async with http.get(
                                    "https://chatgpt.com/backend-api/codex/usage",
                                    headers={
                                        "Authorization": f"Bearer {session_token}",
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                    },
                                    timeout=15,
                                ) as resp:
                                    if resp.status in (401, 403):
                                        errors["base"] = "invalid_session"
                                    elif not resp.ok:
                                        errors["base"] = "cannot_connect"
                            elif data_source == "antigravity_direct":
                                async with http.get(
                                    "https://colab.research.google.com/api/quota",
                                    headers={
                                        "Authorization": f"Bearer {session_token}",
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                    },
                                    timeout=15,
                                ) as resp:
                                    if resp.status in (401, 403):
                                        errors["base"] = "invalid_session"
                                    elif not resp.ok:
                                        errors["base"] = "cannot_connect"
                    except aiohttp.ClientError:
                        errors["base"] = "cannot_connect"
                    except Exception:  # noqa: BLE001
                        errors["base"] = "unknown"

                if not errors and session_token:
                    token_hash = hashlib.md5(session_token.encode("utf-8")).hexdigest()[:10]
                    unique_id = f"{data_source}_{token_hash}"
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    label = account_label or provider_label
                    return self.async_create_entry(
                        title=f"{provider_label} Direct — {label}",
                        data={
                            CONF_DATA_SOURCE: data_source,
                            CONF_SESSION_TOKEN: session_token,
                            CONF_ACCOUNT_LABEL: label,
                        },
                    )

        schema = vol.Schema(
            {
                vol.Required("redirect_url"): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.URL)
                ),
            }
        )

        return self.async_show_form(
            step_id="direct_oauth",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "provider": provider_label,
                "oauth_url": oauth_url,
                "instructions": instructions,
            },
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_codex_code(redirect_url: str) -> str | None:
        """Extract the authorization `code` from the Codex callback URL.

        Expected form: http://localhost:1455/auth/callback?code=XXXX&state=YYYY
        """
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(redirect_url.strip())
        qs = parse_qs(parsed.query)
        codes = qs.get("code")
        return codes[0] if codes else None

    @staticmethod
    def _extract_token_from_url(data_source: str, text: str) -> str | None:
        """Extract a session token from a pasted URL or raw token string.

        Used for Claude and Antigravity (non-PKCE flows).
        - claude_direct:       ?sessionKey=  |  #sessionKey=  |  last path segment
        - antigravity_direct:  ?access_token= | #access_token=
        Falls back to treating the entire input as a raw token.
        """
        from urllib.parse import urlparse, parse_qs, unquote

        stripped = text.strip()
        if not stripped:
            return None

        # Not a URL — treat as raw token
        if not stripped.startswith("http"):
            return stripped

        parsed = urlparse(stripped)
        qs = parse_qs(parsed.query)
        frag = parse_qs(parsed.fragment)

        def _first(d: dict, key: str) -> str | None:
            return unquote(d[key][0]) if key in d and d[key] else None

        if data_source == "claude_direct":
            for src in (qs, frag):
                v = _first(src, "sessionKey")
                if v:
                    return v
            # Last path segment if it looks like a token (>30 chars)
            parts = [p for p in parsed.path.split("/") if p]
            if parts and len(parts[-1]) > 30:
                return parts[-1]

        elif data_source == "antigravity_direct":
            for key in ("access_token", "id_token", "token"):
                for src in (qs, frag):
                    v = _first(src, key)
                    if v:
                        return v

        # Generic fallback — any long query/fragment value
        for src in (qs, frag):
            for vals in src.values():
                if vals and len(vals[0]) > 30:
                    return unquote(vals[0])

        return None


    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return AIQuotaOptionsFlowHandler()


class AIQuotaOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for AI Web Quota."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Merge data and options
        options = dict(self.config_entry.data)
        if hasattr(self.config_entry, "options") and self.config_entry.options:
            options.update(self.config_entry.options)

        data_source = options.get(CONF_DATA_SOURCE, "9router")

        # Build schema based on data source
        if data_source == "trouter":
            schema = vol.Schema(
                {
                    vol.Optional(CONF_API_KEY, default=str(options.get(CONF_API_KEY) or "")): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    ),
                }
            )
        elif data_source in ("claude_direct", "codex_direct", "antigravity_direct"):
            schema = vol.Schema(
                {
                    vol.Optional(CONF_SESSION_TOKEN, default=str(options.get(CONF_SESSION_TOKEN) or "")): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    ),
                    vol.Optional(CONF_ACCOUNT_LABEL, default=str(options.get(CONF_ACCOUNT_LABEL) or "")): str,
                }
            )
        else:
            # CLIProxy or 9Router
            schema = vol.Schema(
                {
                    vol.Optional(CONF_PROXY_URL, default=str(options.get(CONF_PROXY_URL) or "http://localhost:20128")): str,
                    vol.Optional(CONF_API_KEY, default=str(options.get(CONF_API_KEY) or "")): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    ),
                }
            )

        return self.async_show_form(step_id="init", data_schema=schema)
