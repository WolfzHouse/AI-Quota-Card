"""Constants for the AI Web Quota integration."""

DOMAIN = "ai_quota"

CONF_PROXY_URL = "proxy_url"
CONF_API_KEY = "api_key"
CONF_DATA_SOURCE = "data_source"
CONF_SESSION_TOKEN = "session_token"
CONF_ACCOUNT_LABEL = "account_label"

DEFAULT_PROXY_URL = "https://ai.wolfz.shop/v0/management/api-call"
DEFAULT_SCAN_INTERVAL_MINUTES = 15

DATA_SOURCES = {
    "cliproxy": "CLIProxy",
    "trouter": "Trouter.click",
    "9router": "9Router",
    "claude_direct": "Claude (Direct)",
    "codex_direct": "Codex (Direct)",
    "antigravity_direct": "Antigravity (Direct)",
}

DIRECT_PROVIDERS = {
    "claude_direct": "Claude",
    "codex_direct": "Codex",
    "antigravity_direct": "Antigravity",
}
