from flask import Flask, render_template
from flask_login import LoginManager, current_user
import os
from .config import Config
from .extensions import db, login_manager
from .models.user import User
from .routes import auth, emergency, responder, dashboard
from .routes.map import bp as map_bp


from dotenv import load_dotenv
load_dotenv()

def create_app():

    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(app_dir, 'templates'),
                static_folder=os.path.join(app_dir, 'static'),
                static_url_path='/static')
    
    app.config.from_object(Config)
    
    app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(emergency.bp, url_prefix='/emergency')
    app.register_blueprint(responder.bp, url_prefix='/responder')
    app.register_blueprint(dashboard.bp, url_prefix='/dashboard')

    app.register_blueprint(map_bp)

    # Create tables and ensure /tmp exists
    with app.app_context():
        os.makedirs('/tmp', exist_ok=True)
        db.create_all()
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def index():
        return render_template('index.html', user=current_user)
    
    @app.route('/favicon.ico')
    def favicon():
        return '', 204
    
    return app