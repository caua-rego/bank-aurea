import os
import uuid
import json
from flask import Blueprint, request, jsonify, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db, csrf

user_bp = Blueprint('user', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/profile', methods=['PUT'])
@csrf.exempt
@login_required
def update_profile():
    # Handle multipart/form-data or JSON
    # When uploading file, it comes as form-data
    
    # Update preferences/text fields
    if request.form.get('preferences'):
        prefs = request.form.get('preferences')
        if isinstance(prefs, str):
             # If it came as a stringified JSON from FormData
            try:
                # Validate JSON
                json.loads(prefs) 
                current_user.preferences = prefs
            except:
                pass 
    
    # Handle JSON body (legacy support if needed, or if frontend sends JSON)
    elif request.is_json:
        data = request.get_json()
        if 'profile_image' in data:
            current_user.profile_image = data['profile_image']
        if 'preferences' in data:
            prefs = data['preferences']
            if isinstance(prefs, dict):
                current_user.preferences = json.dumps(prefs)
            else:
                current_user.preferences = prefs
                
    # Handle File Upload
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = str(uuid.uuid4()) + '.' + extension
            
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            file.save(os.path.join(upload_folder, unique_filename))
            
            current_user.profile_image = url_for('static', filename=f'uploads/{unique_filename}', _external=True)

    try:
        db.session.commit()
        
        # Prepare response user object
        user_data = {
            "username": current_user.username,
            "profile_image": current_user.profile_image,
            "preferences": {}
        }
        
        if current_user.preferences:
            try:
                user_data["preferences"] = json.loads(current_user.preferences)
            except:
                pass

        # Ensure profile_image returned as absolute URL when available
        if current_user.profile_image and not str(current_user.profile_image).startswith('http'):
            user_data["profile_image"] = url_for('static', filename=current_user.profile_image.lstrip('/static/'), _external=True)

        return jsonify({
            "success": True, 
            "message": "Profile updated",
            "user": user_data
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
