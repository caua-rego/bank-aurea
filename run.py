import os
from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
