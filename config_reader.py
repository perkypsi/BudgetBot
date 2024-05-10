from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, StrictInt


class Settings(BaseSettings):
    bot_token: SecretStr
    chat_ids: list
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()