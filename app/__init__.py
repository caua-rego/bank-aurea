from flask import Flask
from config import config
from app.extensions import db, login_manager, bcrypt, csrf, migrate, limiter

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    
    # CORS
    from flask_cors import CORS
    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": ["http://localhost:4200", "http://127.0.0.1:4200", "http://localhost:5001", "http://127.0.0.1:5001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })

    # Login Manager setup
    login_manager.login_view = None # Disable redirect
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return {"error": "Unauthorized"}, 401
    
    # Register Blueprints
    from .controllers.main_controller import main_bp
    app.register_blueprint(main_bp)

    # Register Auth Blueprint
    from .controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register Errors Blueprint
    from .controllers.errors_controller import errors_bp
    app.register_blueprint(errors_bp)

    # Register Admin Blueprint
    from .controllers.admin_controller import admin_bp
    app.register_blueprint(admin_bp)

    # Register User Blueprint
    # Register User Blueprint
    from .controllers.user_controller import user_bp
    app.register_blueprint(user_bp, url_prefix='/users')
    
    # Register Card Blueprint
    from .controllers.card_controller import card_bp
    app.register_blueprint(card_bp, url_prefix='/cards')

    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/aurea.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Aurea Startup')
    
    return app
