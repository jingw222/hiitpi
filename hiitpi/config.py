import os
import redis
import secrets


BASE_PATH = os.path.dirname(__file__)


class Config:
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "this is a secret")

    MODEL_DIR = os.path.join(BASE_PATH, "assets", "models")
    MODEL_FILE = os.environ.get("MODEL_FILE")
    MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL")

    SESSION_TYPE = "redis"
    SESSION_REDIS_URL = os.environ.get("SESSION_REDIS_URL")
    SESSION_REDIS = redis.from_url(SESSION_REDIS_URL)

    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
    REDIS_DB = os.environ.get("REDIS_DB")


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    DEVELOPMENT = True
    TEMPLATES_AUTO_RELOAD = True


class TestingConfig(Config):
    ENV = "testing"
    TESTING = True


class ProductionConfig(Config):
    ENV = "production"
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_urlsafe(16))


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": ProductionConfig,
}
