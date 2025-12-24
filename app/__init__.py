from flask import Flask, render_template
from flask_login import LoginManager, current_user
import os
from .config import Config
from .extensions import db, login_manager
from .models.user import User
from .routes import auth, emergency, responder, dashboard
from flask import send_from_directory
import logging
logging.basicConfig(level=logging.DEBUG)

def create_app():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(app_dir, 'templates'),
                static_folder=os.path.join(app_dir, 'static'),
                static_url_path='/static')
    
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(emergency.bp, url_prefix='/emergency')
    app.register_blueprint(responder.bp, url_prefix='/responder')
    app.register_blueprint(dashboard.bp, url_prefix='/dashboard')
    
    # Create tables and ensure directory exists
    with app.app_context():
        # Ensure /tmp exists for Vercel
        if os.environ.get('VERCEL'):
            os.makedirs('/tmp', exist_ok=True)
        db.create_all()
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def index():
        return render_template('index.html', user=current_user)
    

@app.route('/test')
def test():
    import os
    import traceback
    try:
        return f"""
        <h1>✅ App is working!</h1>
        <p>SECRET_KEY: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}</p>
        <p>VERCEL: {os.environ.get('VERCEL', 'NOT SET')}</p>
        <p>Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}</p>
        """
    except Exception as e:
        return f"<h3>❌ Error:</h3><pre>{traceback.format_exc()}</pre>"
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.static_folder, 'images'), 
                               'favicon.ico', 
                               mimetype='image/vnd.microsoft.icon')

    
    return app