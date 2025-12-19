import os
from typing import List


def _bool_env(key: str, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in {"1", "true", "t", "yes", "on"}


def _list_env(key: str, default: List[str]) -> List[str]:
    value = os.environ.get(key)
    if not value:
        return default
    return [item.strip() for item in value.split(',') if item.strip()]


DEFAULT_DB_URL = os.environ.get('DATABASE_URL') or 'postgresql+psycopg2://postgres:postgres@localhost:5432/aurea'
DEFAULT_CORS = ["http://localhost:4200", "http://127.0.0.1:4200", "http://localhost:5001", "http://127.0.0.1:5001"]


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-me-in-prod'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret-jwt-key'
    JWT_ACCESS_TOKEN_EXPIRES = 3600 # 1 hour
    SQLALCHEMY_DATABASE_URI = DEFAULT_DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask-WTF CSRF disabled in favor of custom double-submit token in app/__init__.py
    WTF_CSRF_ENABLED = _bool_env('WTF_CSRF_ENABLED', False)
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    # Security / cookies
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = _bool_env('SESSION_COOKIE_SECURE', False)
    SESSION_COOKIE_HTTPONLY = _bool_env('SESSION_COOKIE_HTTPONLY', True)
    REMEMBER_COOKIE_SAMESITE = os.environ.get('REMEMBER_COOKIE_SAMESITE', 'Lax')
    REMEMBER_COOKIE_SECURE = _bool_env('REMEMBER_COOKIE_SECURE', False)
    REMEMBER_COOKIE_HTTPONLY = _bool_env('REMEMBER_COOKIE_HTTPONLY', True)

    # Content limits and upload policy
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 2 * 1024 * 1024))  # 2MB default

    # CORS
    CORS_ALLOWED_ORIGINS = _list_env('CORS_ALLOWED_ORIGINS', DEFAULT_CORS)

    # Rate limiting storage (Redis recomendado para prod)
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'redis://localhost:6379/0')

    # Security headers
    CSP_POLICY = os.environ.get(
        'CSP_POLICY',
        "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; font-src 'self' data:"
    )
    ENABLE_HSTS = _bool_env('ENABLE_HSTS', False)
    OTEL_EXPORTER_OTLP_ENDPOINT = os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')
    ENABLE_OTEL = _bool_env('ENABLE_OTEL', False)


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    RATELIMIT_STORAGE_URI = 'memory://'


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
