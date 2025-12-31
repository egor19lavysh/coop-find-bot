from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_DRIVER: str
    GOOGLE_SHEET_CREDENTIALS_PATH: str
    GOOGLE_SHEET_ID: str
    GOOGLE_SHEET_WORKSHEET_NAME: str
    PRIVATE_PHOTO_GROUP_ID: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    @property
    def db_url(self) -> str:
        return f"postgresql+{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
