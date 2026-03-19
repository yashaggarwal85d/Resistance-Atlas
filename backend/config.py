from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    nvidia_api_key: str
    nvidia_api_url: str = "https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = (".env", "../.env")
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
