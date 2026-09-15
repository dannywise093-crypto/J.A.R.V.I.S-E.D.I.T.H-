from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "J.A.R.V.I.S.-E.D.I.T.H."
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_token: str = "change-this-in-development"
    llm_provider: str = "mock"
    llm_model: str = "jarvis-local"
    openai_api_key: str = ""
    openai_transcription_model: str = "gpt-4o-transcribe"
    openai_tts_model: str = "gpt-4o-mini-tts"
    database_url: str = "sqlite:///./jarvis.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
