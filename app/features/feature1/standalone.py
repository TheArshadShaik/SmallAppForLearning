"""
Feature 1 Standalone Server Runner.
Run this script to deploy Feature 1 as an independent microservice on a new server!
Example:
    python -m app.features.feature1.standalone --port 5001
"""
import os
import argparse
from flask import Flask, redirect
from app.features.feature1.routes import feature1_bp


def create_standalone_app():
    """Constructs a minimal Flask app serving only Feature 1."""
    app = Flask(__name__, template_folder="../../templates", static_folder="../../static")
    app.config["STANDALONE_FEATURE"] = True
    app.config["APP_NAME"] = "Feature 1 Standalone Microservice"
    
    # Mount feature1 at root and /feature1 for seamless routing
    app.register_blueprint(feature1_bp, url_prefix="/feature1")
    
    @app.route("/")
    def root_redirect():
        return redirect("/feature1")
        
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature 1 Microserver Runner")
    parser.add_argument("--host", default="0.0.0.0", help="Binding host")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 5001)), help="Binding port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    app = create_standalone_app()
    print("=" * 60)
    print(f" Starting [Feature 1] Standalone Server on http://{args.host}:{args.port}")
    print(f" Independent Microservice ready for new server deployment.")
    print("=" * 60)
    app.run(host=args.host, port=args.port, debug=args.debug)
