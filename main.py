from flask import Flask
from app.routes import app_routes

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.register_blueprint(app_routes)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
