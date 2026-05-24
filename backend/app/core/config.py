from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/job_autofiller"
    REDIS_URL: str = "redis://localhost:6379/0"
    GROQ_API_KEY: str = ""
    APIFY_API_TOKEN: str = ""
    APIFY_ACTOR_ID: str = "curious_coder/linkedin-jobs-scraper"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    SCORING_MODEL: str = "llama-3.1-8b-instant"
    CORS_ORIGINS: str = "http://localhost:3000"  # Comma-separated list of allowed origins


settings = Settings()
