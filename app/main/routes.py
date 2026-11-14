import os
import platform
import socket
from datetime import datetime, timezone
from flask import Blueprint, render_template, jsonify, current_app

main_bp = Blueprint("main", __name__, template_folder="../templates")


@main_bp.route("/")
def index():
    """Home page - Primary landing page and main feature."""
    active_features = []
    
    # Check registered blueprints
    for name, bp in current_app.blueprints.items():
        if name == "feature1":
            active_features.append({"name": "Feature 1 - Analytics Calculator", "url": "/feature1", "badge": "Active"})
        elif name == "feature2":
            active_features.append({"name": "Feature 2 - Diagnostics & Metrics", "url": "/feature2", "badge": "Active"})

    server_info = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "app_version": current_app.config.get("APP_VERSION", "1.0.0"),
        "environment": current_app.config.get("ENV", "production"),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "active_features": active_features,
    }
    return render_template("index.html", info=server_info)


@main_bp.route("/health")
def health():
    """Health check endpoint used by Docker, AWS ELB/ALB, and Azure DevOps."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": current_app.config.get("APP_VERSION", "1.0.0"),
        "hostname": socket.gethostname(),
        "features": {
            "feature1": "feature1" in current_app.blueprints,
            "feature2": "feature2" in current_app.blueprints,
        }
    }), 200


@main_bp.route("/api/info")
def info():
    """Returns application status and environment info in JSON."""
    return jsonify({
        "app_name": current_app.config.get("APP_NAME"),
        "version": current_app.config.get("APP_VERSION"),
        "environment": current_app.config.get("ENV"),
        "blueprints": list(current_app.blueprints.keys()),
        "hostname": socket.gethostname(),
    }), 200
