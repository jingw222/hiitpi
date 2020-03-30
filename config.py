import os
import redis


BASE_PATH = os.path.dirname(__file__)

REDIS_CONFIG = {
    "REDIS_DEFAULT_TIMEOUT": os.getenv("REDIS_DEFAULT_TIMEOUT", 30),
    "REDIS_HOST": os.getenv("REDIS_HOST", "localhost"),
    "REDIS_PORT": os.getenv("REDIS_PORT", 6379),
    "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD", "redis"),
}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "this is a secret"
    MODEL_DIR = os.path.join(BASE_PATH, "hiitpi", "assets", "models")
    MODEL_FILE = "posenet_mobilenet_v1_075_481_641_quant_decoder_edgetpu.tflite"
    MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = "redis"
    CACHE_DEFAULT_TIMEOUT = REDIS_CONFIG["REDIS_DEFAULT_TIMEOUT"]
    CACHE_REDIS_HOST = REDIS_CONFIG["REDIS_HOST"]
    CACHE_REDIS_PORT = REDIS_CONFIG["REDIS_PORT"]
    CACHE_REDIS_DB = 0
    CACHE_REDIS_PASSWORD = REDIS_CONFIG["REDIS_PASSWORD"]

    SESSION_TYPE = "redis"
    SESSION_REDIS_URL = os.environ.get(
        "SESSION_REDIS_URL",
        f'redis://:{REDIS_CONFIG["REDIS_PASSWORD"]}@{REDIS_CONFIG["REDIS_HOST"]}:{REDIS_CONFIG["REDIS_PORT"]}/1',
    )

    SESSION_REDIS = redis.from_url(SESSION_REDIS_URL)


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    DEVELOPMENT = True

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URI", "sqlite:///" + os.path.join(BASE_PATH, "data-dev.sqlite")
    )


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    DEVELOPMENT = False

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URI", "sqlite:///" + os.path.join(BASE_PATH, "data.sqlite")
    )


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": ProductionConfig,
}
