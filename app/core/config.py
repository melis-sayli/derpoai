from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "DERPOAI"
    API_V1: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./derpoai.db"



    # Güvenlik — Ders 3'te kullanacağız



    JWT_SECRET: str = "degistir-bunu-uretimde"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60



    # Çevresel eşikler — Ders 5'te kullanacağız


    
    TEMP_MIN: float = 2.0
    TEMP_MAX: float = 26.0
    HUMIDITY_MAX: float = 70.0

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()