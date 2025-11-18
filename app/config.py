from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bind: str = "0.0.0.0"
    port: int = 8080

    jwt_secret: str = "changeme"
    jwt_iss: str = "axon88"
    jwt_aud: str = "control"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    dev_mode: bool = True
    production_mode: bool = False

    cors_origins: str = "*"

    files_root: str = "/home/runner/axon-core"
    default_cwd: str = "/home/runner/axon-core"

    allowed_cmds: str = "/usr/bin/ls,/usr/bin/cat,/usr/bin/tail,/usr/bin/df"

    n8n_base_url: str = ""
    n8n_api_key: str = ""

    openai_api_key: str = ""
    gemini_api_key: str = ""
    deepseek_api_key: str = ""

    ollama_base_url: str = "http://127.0.0.1:11434"
    sdxl_base_url: str = "http://127.0.0.1:7860"

    cf_service_name: str = "cloudflared"
    tailscale_service_name: str = "tailscaled"

    audit_log_path: str = "logs/audit.jsonl"
    log_rotation_size: str = "10MB"
    log_retention_days: int = 30

    @property
    def allowed_commands_list(self) -> List[str]:
        return [cmd.strip() for cmd in self.allowed_cmds.split(",") if cmd.strip()]

    @property
    def cors_origins_list(self) -> List[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
