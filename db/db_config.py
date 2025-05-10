import os.path

from pydantic_settings import BaseSettings


def _get_module_path() -> str:
    return os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_SSL_CA: str

    @property
    def DATABASE_URL(self):
        return (f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?"
                f"ssl_ca={self.DB_SSL_CA}")

    class Config:
        env_file = os.path.join(_get_module_path(), '../.env')  # используй BASEDIR
        env_file_encoding = 'utf-8'


settings = Settings()
