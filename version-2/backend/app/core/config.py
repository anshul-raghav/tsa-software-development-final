from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "TouchMap API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.1

    database_url: str = "sqlite+aiosqlite:///./touchmap.db"

    upload_dir: str = "./uploads"
    max_image_size_mb: int = 10
    scan_retry_limit: int = 1

    ml_model_path: str = "./app/ml/models/scan_quality_model.pth"
    ml_confidence_threshold: float = 0.7

    ocr_languages: list[str] = ["en"]
    ocr_confidence_threshold: float = 0.3

    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

UPLOAD_PATH = Path(settings.upload_dir)
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
