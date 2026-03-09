import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # path
    BASE_PATH: str = os.path.join(
        os.path.dirname(__file__),            # api/app/core/
        "..", "..",
    )

    # Application
    APP_NAME: str = "FastAPI App"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Anthropic
    ANTHROPIC_API_KEY: str = ""


settings = Settings()
