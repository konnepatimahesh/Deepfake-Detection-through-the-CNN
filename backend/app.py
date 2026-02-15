from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models.user import db, bcrypt
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('database', exist_ok=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.detection import detection_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(detection_bp, url_prefix='/api/detection')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    # Welcome route
    @app.route('/')
    def index():
        return {
            'message': 'Deepfake Detection API',
            'version': '1.0',
            'endpoints': {
                'auth': '/api/auth',
                'detection': '/api/detection',
                'admin': '/api/admin'
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)