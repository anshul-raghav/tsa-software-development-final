"""
Application settings loaded from environment and .env.

Drives API prefix, OpenAI/OCR options, upload paths, and log level.
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "TouchMap API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # OpenAI: used for panelmap extraction, intent parsing, live guidance
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.1

    database_url: str = "sqlite+aiosqlite:///./touchmap.db"

    # Scan pipeline: where to store preprocessed images and retry behavior
    upload_dir: str = "./uploads"
    max_image_size_mb: int = 10
    scan_retry_limit: int = 1

    # OCR: languages and minimum confidence to keep a token
    ocr_languages: list[str] = ["en"]
    ocr_confidence_threshold: float = 0.3

    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

UPLOAD_PATH = Path(settings.upload_dir)
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
