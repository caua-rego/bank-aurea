import logging
import secrets
from time import perf_counter
from flask import Flask, request, session
from config import config
from app.extensions import db, login_manager, bcrypt, csrf, migrate, limiter
from prometheus_flask_exporter import PrometheusMetrics
from pythonjsonlogger import jsonlogger

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

    # Metrics
    metrics = PrometheusMetrics(app, group_by="endpoint")
    metrics.info("app_info", "Aurea application info", version="1.0.0")
    
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

    # CSRF double-submit token for state-changing requests
    CSRF_HEADER = "X-XSRF-TOKEN"
    CSRF_COOKIE = "XSRF-TOKEN"

    def _ensure_csrf_token():
        token = session.get('csrf_token')
        if not token:
            token = secrets.token_urlsafe(32)
            session['csrf_token'] = token
        return token

    @app.before_request
    def enforce_csrf_for_state_changes():
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            allowlist = ['/metrics', '/healthz', '/auth/login', '/auth/register']
            if request.path in allowlist:
                return
            token = session.get('csrf_token')
            header_token = request.headers.get(CSRF_HEADER)
            if not token or token != header_token:
                # Auto-bypass in testing to keep fixtures lean
                if app.config.get('TESTING'):
                    return
                return {"error": "CSRF token missing or invalid"}, 400

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
            csrf_token = _ensure_csrf_token()
            response.set_cookie(
                CSRF_COOKIE,
                csrf_token,
                samesite=app.config.get('SESSION_COOKIE_SAMESITE', 'Lax'),
                secure=app.config.get('SESSION_COOKIE_SECURE', False),
                httponly=False,
            )

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
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = app.config.get('CSP_POLICY')
        if app.config.get('ENABLE_HSTS'):
            response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
        return response

    @app.route('/healthz')
    def healthz():
        return {"status": "ok"}, 200
    
    # Register Blueprints
    from .controllers.main_controller import main_bp
    app.register_blueprint(main_bp)

    # Register Auth Blueprint
    from .controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register Errors Blueprint
    from .controllers.errors_controller import errors_bp
    app.register_blueprint(errors_bp)

    # API Docs (ReDoc)
    from .controllers.docs_controller import docs_bp
    app.register_blueprint(docs_bp)

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

    # Logging configuration (JSON)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Aurea Startup')

    # Optional OpenTelemetry
    if app.config.get('ENABLE_OTEL') and app.config.get('OTEL_EXPORTER_OTLP_ENDPOINT'):
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            from opentelemetry.instrumentation.flask import FlaskInstrumentor

            provider = TracerProvider()
            otlp_exporter = OTLPSpanExporter(endpoint=app.config['OTEL_EXPORTER_OTLP_ENDPOINT'])
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            trace.set_tracer_provider(provider)
            FlaskInstrumentor().instrument_app(app)
            app.logger.info('OTEL tracing enabled')
        except Exception as exc:
            app.logger.error('Failed to init OTEL', extra={'error': str(exc)})
    
    return app
