from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    URL: str
    JWT_KEY: str
    ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: str
    GMAIL_APP_PASSWORD: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URL: str
    GEMINI_API_KEY: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()