from flask import Flask, request, send_from_directory
from flask_cors import CORS
from datetime import timedelta
from flask_jwt_extended import JWTManager
from config import APP_NAME, DB_URL, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_EXPIRES_DAYS
from db import db
from blueprints.sign_bp import sign_bp
from blueprints.user_bp import user_bp
from blueprints.film_bp import film_bp
from blueprints.post_bp import post_bp
from blueprints.admin_bp import admin_bp
from common.handler import register_exception_handlers
import os 

def create_app():
    """Create Flask App Instance"""
    app = Flask(APP_NAME)

    # Configure CORS with comprehensive settings
    CORS(app,
         origins=['http://localhost:5173'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin'],
         supports_credentials=True,
         max_age=86400)  # Cache preflight for 24 hours

    # JWT configuration (centralized) from config.py
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['JWT_ALGORITHM'] = JWT_ALGORITHM
    # set access token expiry timedelta
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=int(JWT_ACCESS_EXPIRES_DAYS))
    JWTManager(app)

    # database settings
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Static files directory paths
    current_dir = os.path.dirname(os.path.abspath(__file__))  # api/src
    posters_path = os.path.join(current_dir, 'data', 'posters')
    avatars_path = os.path.join(current_dir, 'data', 'avatars')

    def serve_poster(filename):
        try:
            return send_from_directory(posters_path, filename)
        except Exception as e:
            return "File not found", 404
    def serve_avatar(filename):
        try:
            return send_from_directory(avatars_path, filename)
        except Exception as e:
            return "File not found", 404

    app.add_url_rule('/static/posters/<path:filename>', 'serve_poster', serve_poster)
    app.add_url_rule('/static/avatars/<path:filename>', 'serve_avatar', serve_avatar)

    # register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(sign_bp)
    app.register_blueprint(film_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(admin_bp)

    # register global exception handlers
    register_exception_handlers(app)

    # Handle OPTIONS requests globally
    @app.before_request
    def handle_options():
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response

    @app.route('/')
    def index():
        return {
            'message': 'filmhub',
            'version': '1.0.0',
        }

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
