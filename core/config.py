# core/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    NEWS_KEY: str = os.getenv("NEWS_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()