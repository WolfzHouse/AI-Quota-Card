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
    CONF_PROVIDER,
    CONF_AUTH_INDEX,
    CONF_API_KEY,
    CONF_ACCOUNT_NAME,
    CONF_DATA_SOURCE,
    DEFAULT_PROXY_URL,
    DATA_SOURCES,
    PROVIDERS
)

_LOGGER = logging.getLogger(__name__)

# Dropdown options for the provider selection
PROVIDER_OPTIONS = [
    selector.SelectOptionDict(value=key, label=name)
    for key, name in PROVIDERS.items()
]


class AIQuotaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AI Web Quota."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._flow_type = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - show menu."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["api_proxy", "trouter"]
        )

    async def async_step_api_proxy(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle API Proxy (CLIProxy/9Router) configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # No validation needed - password is optional for both CLIProxy and 9Router
            
            # Generate a unique_id
            unique_id = f"{user_input[CONF_DATA_SOURCE]}_{user_input[CONF_PROVIDER]}_{user_input[CONF_AUTH_INDEX]}"
            
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            
            # Create the entry title
            data_source_name = DATA_SOURCES.get(user_input[CONF_DATA_SOURCE], user_input[CONF_DATA_SOURCE])
            provider = PROVIDERS.get(user_input[CONF_PROVIDER], user_input[CONF_PROVIDER])
            title = f"{data_source_name} - {provider} (Auth: {user_input[CONF_AUTH_INDEX]})"
            return self.async_create_entry(title=title, data=user_input)

        # Schema for API Proxy sources
        api_proxy_sources = [
            selector.SelectOptionDict(value="cliproxy", label="CLIProxy"),
            selector.SelectOptionDict(value="9router", label="9Router"),
        ]

        schema = vol.Schema(
            {
                vol.Required(CONF_DATA_SOURCE, default="cliproxy"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=api_proxy_sources,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_PROVIDER): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=PROVIDER_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_AUTH_INDEX, default="0"): str,
                vol.Required(CONF_PROXY_URL, default="http://localhost:20128"): str,
                vol.Optional(CONF_API_KEY, default=""): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Optional(CONF_ACCOUNT_NAME, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="api_proxy",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "info": "Configure CLIProxy or 9Router connection"
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
                
                # Generate a unique_id
                unique_id = f"trouter_{user_input[CONF_PROVIDER]}_{user_input[CONF_AUTH_INDEX]}"
                
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                # Create the entry title
                provider = PROVIDERS.get(user_input[CONF_PROVIDER], user_input[CONF_PROVIDER])
                title = f"Trouter - {provider} (Auth: {user_input[CONF_AUTH_INDEX]})"
                return self.async_create_entry(title=title, data=user_input)

        # Schema for Trouter
        schema = vol.Schema(
            {
                vol.Required(CONF_PROVIDER): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=PROVIDER_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_AUTH_INDEX, default="0"): str,
                vol.Required(CONF_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Optional(CONF_ACCOUNT_NAME, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="trouter",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "info": "Configure Trouter.click connection"
            }
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

        data_source = options.get(CONF_DATA_SOURCE, "cliproxy")

        # Build schema based on data source
        if data_source == "trouter":
            schema = vol.Schema(
                {
                    vol.Optional(CONF_API_KEY, default=str(options.get(CONF_API_KEY) or "")): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    ),
                    vol.Optional(CONF_ACCOUNT_NAME, default=str(options.get(CONF_ACCOUNT_NAME) or "")): str,
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
                    vol.Optional(CONF_ACCOUNT_NAME, default=str(options.get(CONF_ACCOUNT_NAME) or "")): str,
                }
            )

        return self.async_show_form(step_id="init", data_schema=schema)
