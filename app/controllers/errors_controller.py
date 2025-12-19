from flask import Blueprint

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return {"error": "Resource not found"}, 404

@errors_bp.app_errorhandler(403)
def forbidden_error(error):
    return {"error": "Forbidden"}, 403

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return {"error": "Internal Server Error"}, 500

@errors_bp.app_errorhandler(Exception)
def handle_exception(e):
    return {"error": str(e)}, 500
