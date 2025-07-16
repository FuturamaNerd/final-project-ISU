"""
Configuration file for the news application.
Store sensitive data like API keys here.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# NewsAPI Configuration
NEWS_API_KEY = "fc3239757d57462faa7182b71dc62c8b"

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/news_world_database"

# Flask Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MONGO_URI = MONGO_URI

# Development Configuration
class DevelopmentConfig(Config):
    DEBUG = True

# Production Configuration
class ProductionConfig(Config):
    DEBUG = False
    # In production, use environment variables:
    # NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
    # MONGO_URI = os.environ.get('MONGO_URI') 