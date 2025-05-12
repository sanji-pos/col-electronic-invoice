from pydantic_settings import BaseSettings


class Config(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        secrets_dir = None # Desactiva cualquier caché de secretos
