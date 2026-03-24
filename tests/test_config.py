"""Tests for the config module."""

from ceramicraft_log_mservice.config import Settings, get_settings


def test_settings_defaults():
    """Settings should load with expected defaults."""
    settings = Settings()
    assert settings.POSTGRES_USER == "user"
    assert settings.POSTGRES_PASSWORD == "password"
    assert settings.POSTGRES_HOST == "localhost"
    assert settings.POSTGRES_PORT == 5432
    assert settings.LOG_DB_NAME == "log_db"
    assert settings.LOG_MSERVICE_HTTP_PORT == 8080
    assert settings.LOG_MSERVICE_GRPC_HOST == "[::]"
    assert settings.LOG_MSERVICE_GRPC_PORT == 50051


def test_database_url_format():
    """DATABASE_URL should be correctly assembled from components."""
    settings = Settings(
        POSTGRES_USER="myuser",
        POSTGRES_PASSWORD="mypass",
        POSTGRES_HOST="db-host",
        POSTGRES_PORT=5433,
    )
    assert settings.DATABASE_URL == (
        "postgresql+psycopg://myuser:mypass@db-host:5433/log_db"
    )


def test_get_settings_returns_settings_instance():
    """get_settings() should return a Settings instance."""
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_get_settings_is_cached():
    """get_settings() should return the same object on repeated calls."""
    assert get_settings() is get_settings()
