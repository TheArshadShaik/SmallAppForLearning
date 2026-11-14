import os
from flask import Flask, render_template, jsonify
from app.config import config_by_name, Config


def create_app(config_name=None):
    """
    Application factory for the modular Python server.
    Features can be dynamically enabled/disabled or decoupled into standalone servers.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "production")
    
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, Config))
    
    # Register Core / Home Page Blueprint
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Dynamically register Feature 1 Blueprint (if enabled)
    if app.config.get("ENABLE_FEATURE_1", True):
        try:
            from app.features.feature1.routes import feature1_bp
            app.register_blueprint(feature1_bp, url_prefix="/feature1")
            app.logger.info("Feature 1 registered successfully at /feature1")
        except ImportError:
            app.logger.warning("Feature 1 module not found or not yet implemented on this branch.")
    
    # Dynamically register Feature 2 Blueprint (if enabled)
    if app.config.get("ENABLE_FEATURE_2", True):
        try:
            from app.features.feature2.routes import feature2_bp
            app.register_blueprint(feature2_bp, url_prefix="/feature2")
            app.logger.info("Feature 2 registered successfully at /feature2")
        except ImportError:
            app.logger.warning("Feature 2 module not found or not yet implemented on this branch.")
            
    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html"), 500

    return app
