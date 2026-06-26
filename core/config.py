from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str 
    MONGO_DB: str = "alimentacion_db"
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"
    FIREBASE_PROJECT_ID: str = "alimentacion-app-6dbad"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()
