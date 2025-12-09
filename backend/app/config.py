"""Application configuration settings."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "TasteBuds"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url_env: str | None = None  # Render provides DATABASE_URL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "tastesync"
    postgres_user: str = "tastesync_user"
    postgres_password: str = ""
    use_sqlite: bool = True  # Use SQLite for development without PostgreSQL

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "tastesync-embeddings"

    # Yelp API
    yelp_api_key: str = ""

    # OpenAI
    openai_api_key: str = ""

    # JWT
    jwt_secret_key: str = "your-secret-key-min-32-characters-long"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # CORS - Can be overridden with ALLOWED_ORIGINS env var (comma-separated)
    allowed_origins: str = ""  # Empty means use default list

    @property
    def cors_origins(self) -> List[str]:
        """Get CORS allowed origins - supports env override or defaults."""
        # If ALLOWED_ORIGINS is set, use it (comma-separated)
        if self.allowed_origins:
            return [origin.strip() for origin in self.allowed_origins.split(",")]

        # Default origins for development and production
        default_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://192.168.1.81:3000",
            "http://192.168.1.81:3001",
            "https://neon-strudel-0bb18c.netlify.app",
        ]
        return default_origins

    @property
    def database_url(self) -> str:
        """Construct database URL (SQLite for dev, PostgreSQL for prod)."""
        # If DATABASE_URL is provided (e.g., from Render), use it
        if self.database_url_env:
            # Convert postgres:// to postgresql+asyncpg://
            url = self.database_url_env.replace("postgres://", "postgresql+asyncpg://")
            url = url.replace("postgresql://", "postgresql+asyncpg://")
            return url

        if self.use_sqlite:
            return "sqlite+aiosqlite:///./tastesync.db"
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def sync_database_url(self) -> str:
        """Construct sync database URL for Alembic."""
        # If DATABASE_URL is provided, use it
        if self.database_url_env:
            # Ensure it uses postgresql:// (not asyncpg)
            url = self.database_url_env.replace("postgresql+asyncpg://", "postgresql://")
            return url

        if self.use_sqlite:
            return "sqlite:///./tastesync.db"
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        # Map DATABASE_URL to database_url_env
        fields = {
            'database_url_env': {'env': 'DATABASE_URL'}
        }


def get_settings() -> Settings:
    """Get settings instance (cache removed for development)."""
    return Settings()
