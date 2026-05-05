from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default=...)
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()