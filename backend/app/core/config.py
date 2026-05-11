from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default=...)
    SECRET_KEY: str = Field(default="supersecretkey_change_in_production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440) # 24 hours
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()