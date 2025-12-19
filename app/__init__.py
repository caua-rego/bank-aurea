import logging
from time import perf_counter
from flask import Flask, request
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
    limiter.init_app(app, storage_uri=app.config.get('RATELIMIT_STORAGE_URI'))
    
    # CORS
    from flask_cors import CORS
    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": app.config.get('CORS_ALLOWED_ORIGINS', []),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })

    # Login Manager setup
    login_manager.login_view = None # Disable redirect
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return {"error": "Unauthorized"}, 401

    # Basic request logging with latency
    @app.before_request
    def start_timer():
        request._start_time = perf_counter()

    @app.after_request
    def log_request(response):
        try:
            duration_ms = None
            if hasattr(request, '_start_time'):
                duration_ms = round((perf_counter() - request._start_time) * 1000, 2)
            app.logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                    "remote_addr": request.remote_addr,
                },
            )
        except Exception:
            pass
        return response
    
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

    # Logging configuration
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        if not app.logger.handlers:
            app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Aurea Startup')
    
    return app
