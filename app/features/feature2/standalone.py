"""
Feature 2 Standalone Server Runner.
Run this script to deploy Feature 2 as an independent microservice on a new server!
Example:
    python -m app.features.feature2.standalone --port 5002
"""
import os
import argparse
from flask import Flask, redirect
from app.features.feature2.routes import feature2_bp


def create_standalone_app():
    """Constructs a minimal Flask app serving only Feature 2."""
    app = Flask(__name__, template_folder="../../templates", static_folder="../../static")
    app.config["STANDALONE_FEATURE"] = True
    app.config["APP_NAME"] = "Feature 2 Standalone Microservice"
    
    # Mount feature2 at root and /feature2 for seamless routing
    app.register_blueprint(feature2_bp, url_prefix="/feature2")
    
    @app.route("/")
    def root_redirect():
        return redirect("/feature2")
        
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature 2 Microserver Runner")
    parser.add_argument("--host", default="0.0.0.0", help="Binding host")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 5002)), help="Binding port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    app = create_standalone_app()
    print("=" * 60)
    print(f" Starting [Feature 2] Standalone Server on http://{args.host}:{args.port}")
    print(f" Independent Microservice ready for new server deployment.")
    print("=" * 60)
    app.run(host=args.host, port=args.port, debug=args.debug)
