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


    async def async_step_direct_provider(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Direct Provider (Claude / Codex / Antigravity) configuration."""
        import hashlib
        import aiohttp

        errors: dict[str, str] = {}

        if user_input is not None:
            session_token = user_input.get(CONF_SESSION_TOKEN, "").strip()
            data_source = user_input.get(CONF_DATA_SOURCE, "claude_direct")

            if not session_token:
                errors["base"] = "session_token_required"
            else:
                # Quick validation — try a lightweight call to the provider API
                try:
                    async with aiohttp.ClientSession() as session:
                        if data_source == "claude_direct":
                            async with session.get(
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
                            async with session.get(
                                "https://chatgpt.com/backend-api/codex/usage",
                                headers={
                                    "Cookie": f"__Secure-next-auth.session-token={session_token}",
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                    "Referer": "https://chatgpt.com/",
                                },
                                timeout=15,
                            ) as resp:
                                if resp.status in (401, 403):
                                    errors["base"] = "invalid_session"
                                elif not resp.ok:
                                    errors["base"] = "cannot_connect"
                        elif data_source == "antigravity_direct":
                            async with session.get(
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

            if not errors:
                token_hash = hashlib.md5(session_token.encode("utf-8")).hexdigest()[:10]
                unique_id = f"{data_source}_{token_hash}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                provider_label = DIRECT_PROVIDERS.get(data_source, data_source)
                account_label = user_input.get(CONF_ACCOUNT_LABEL, "").strip() or provider_label
                title = f"{provider_label} Direct — {account_label}"

                return self.async_create_entry(title=title, data=user_input)

        # Provider dropdown options
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
                vol.Required(CONF_SESSION_TOKEN): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Optional(CONF_ACCOUNT_LABEL, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="direct_provider",
            data_schema=schema,
            errors=errors,
        )

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
