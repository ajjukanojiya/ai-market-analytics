from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    PROJECT_NAME: str = "AI Market Analytics Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "rootpassword"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "market_data"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        import os
        # Render provides DATABASE_URL for Postgres instances
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            # SQLAlchemy 1.4+ requires 'postgresql://' to be updated to 'postgresql+psycopg://' or similar
            # but usually psycopg2 is default if we just use postgresql://
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            return db_url
            
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # Dhan API
    DHAN_CLIENT_ID: str = ""
    DHAN_ACCESS_TOKEN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore" # Ignores extra fields in .env

settings = Settings()
