import os
from datetime import timedelta

# Get the base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for JWT
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Database - Use absolute path
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "database", "deepfake.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # File uploads - Use absolute path
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
    
    # Model path
    MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), 'trained_models', 'deepfake_detector.h5')