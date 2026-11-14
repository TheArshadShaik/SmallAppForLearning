import socket
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, jsonify, current_app

feature1_bp = Blueprint("feature1", __name__, template_folder="templates")


@feature1_bp.route("/")
def index():
    """Feature 1 single page view: Cloud Capacity & Analytics Calculator."""
    meta = {
        "feature_name": "Feature 1 - Cloud Capacity & Cost Estimator",
        "version": "1.0.0",
        "hostname": socket.gethostname(),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "standalone_mode": current_app.config.get("STANDALONE_FEATURE", False),
    }
    return render_template("feature1/feature1.html", meta=meta)


@feature1_bp.route("/api/calculate", methods=["POST"])
def calculate():
    """
    API endpoint for calculating cloud server sizing and costs.
    Accepts JSON: { instances: int, hours: int, rate: float }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    try:
        instances = int(data.get("instances", 1))
        hours = int(data.get("hours", 24))
        rate_per_hour = float(data.get("rate", 0.05))

        if instances <= 0 or hours <= 0 or rate_per_hour < 0:
            return jsonify({"error": "Values must be greater than zero"}), 422

        total_cost = round(instances * hours * rate_per_hour, 2)
        total_compute_hours = instances * hours

        return jsonify({
            "status": "success",
            "calculation": {
                "instances": instances,
                "hours": hours,
                "rate_per_hour": rate_per_hour,
                "total_compute_hours": total_compute_hours,
                "total_cost_usd": total_cost,
                "monthly_projection_usd": round(total_cost * (720 / max(hours, 1)), 2),
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200

    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"Invalid parameter type: {str(exc)}"}), 400


@feature1_bp.route("/api/health")
def health():
    """Health endpoint for Feature 1 when running as an isolated service."""
    return jsonify({
        "service": "feature1",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200
