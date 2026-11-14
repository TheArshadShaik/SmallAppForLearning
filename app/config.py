import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod-789012")
    APP_NAME = os.getenv("APP_NAME", "SmallApp Modular Python Server")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = False
    TESTING = False
    
    # Feature Toggles (allows selectively enabling features per server)
    ENABLE_FEATURE_1 = os.getenv("ENABLE_FEATURE_1", "true").lower() in ("true", "1", "yes")
    ENABLE_FEATURE_2 = os.getenv("ENABLE_FEATURE_2", "true").lower() in ("true", "1", "yes")
    
    # Server configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENABLE_FEATURE_1 = True
    ENABLE_FEATURE_2 = True


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
