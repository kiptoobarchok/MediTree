from flask import Flask, render_template
from config import Config
from application.database import db, init_db
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from application.models import User

bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_db(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from application.auth import auth_bp
    from application.plantcare import plantcare_bp
    from application.marketplace import marketplace_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(plantcare_bp)
    app.register_blueprint(marketplace_bp)
    
    # Main route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))