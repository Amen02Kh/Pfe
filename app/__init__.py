from flask import Flask
from config import Config
from app.extensions import db
from app.models.users import login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Flask extensions here
    db.init_app(app)
    login_manager.init_app(app)
    # Register blueprints here
    from app.login import bp as login_bp
    app.register_blueprint(login_bp)
    
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp,url_prefix='/pentest')
    from app.cve import bp as cve_bp
    app.register_blueprint(cve_bp, url_prefix='/cve')

    from app.history import bp as history_bp
    app.register_blueprint(history_bp, url_prefix='/history')

    from app.panel import bp as panel_bp
    app.register_blueprint(panel_bp, url_prefix='/panel')

    from app.logout import bp as logout_bp
    app.register_blueprint(logout_bp, url_prefix='/logout')

    

    return app
