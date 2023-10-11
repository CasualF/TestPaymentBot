from pydantic import EmailStr
from pydantic_settings import BaseSettings
from typing import Optional, Literal
import os


class Settings(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

    BOT_TOKEN: str
    ACCESS_TOKEN: str

    CREATE_ORDER_URL: str

    class Config:
        env_file = '.env'


settings = Settings()