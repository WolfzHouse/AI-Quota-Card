"""Constants for the AI Web Quota integration."""

DOMAIN = "ai_quota"

CONF_PROXY_URL = "proxy_url"
CONF_PROVIDER = "provider"
CONF_AUTH_INDEX = "auth_index"
CONF_PROXY_TOKEN = "proxy_token"
CONF_GEMINI_PROJECT_ID = "gemini_project_id"
CONF_CUSTOM_PLAN_NAME = "custom_plan_name"

DEFAULT_PROXY_URL = "https://ai.wolfz.shop/v0/management/api-call"
DEFAULT_SCAN_INTERVAL_MINUTES = 15

PROVIDERS = {
    "antigravity": "Antigravity",
    "claude": "Claude (Anthropic)",
    "codex": "Codex (OpenAI)",
    "gemini-cli": "Gemini CLI",
    "kiro": "Kiro (CodeWhisperer)",
    "copilot": "GitHub Copilot"
}
