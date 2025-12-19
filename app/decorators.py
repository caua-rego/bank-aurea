from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if role == 'admin' and not claims.get("is_admin"):
                return jsonify(msg="Admins only!"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
