import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量 - 从项目根目录加载.env文件
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'case-creator-secret-key-2024'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///case_creator.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('BACKEND_PORT', 8865))
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # JWT配置
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # OpenRouter API配置
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
    DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'gpt-4o-mini')
    
    # 用户配置
    DEFAULT_USER_UUID = os.environ.get('DEFAULT_USER_UUID')
    DEFAULT_USER_NICKNAME = os.environ.get('DEFAULT_USER_NICKNAME', '案例改编用户')
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    # 缓存配置
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 安全配置
    FRONTEND_PORT = int(os.environ.get('FRONTEND_PORT', 8866))
    CORS_ORIGINS = [
        f"http://localhost:{FRONTEND_PORT}", 
        f"http://127.0.0.1:{FRONTEND_PORT}",
        "http://localhost:8868",  # 前端运行端口
        "http://127.0.0.1:8868",  # 前端运行端口
        "http://localhost:8869",  # 当前前端运行端口
        "http://127.0.0.1:8869"   # 当前前端运行端口
    ]
    
    # 系统配置
    MAX_DAILY_REQUESTS = int(os.environ.get('MAX_DAILY_REQUESTS', 100))
    ENABLE_REGISTRATION = os.environ.get('ENABLE_REGISTRATION', 'true').lower() == 'true'
    MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE', 'false').lower() == 'true'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_case_creator.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 