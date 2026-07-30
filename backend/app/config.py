import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_QUESTION_MODEL: str = "openrouter/auto"
    OPENROUTER_EVAL_MODEL: str = "openrouter/auto"
    OPENROUTER_GRAMMAR_MODEL: str = "anthropic/claude-haiku-4.5"
    OPENROUTER_MATCH_MODEL: str = "anthropic/claude-sonnet-4.5"
    OPENROUTER_FEEDBACK_MODEL: str = "openrouter/auto"
    JWT_SECRET: str = "supersecretjwtkey_ai_interview_coach_2026"
    DATABASE_URL: str = "sqlite:///./interview_coach.db"
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
