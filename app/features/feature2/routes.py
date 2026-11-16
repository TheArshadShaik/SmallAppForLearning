import os
import sys
import socket
import platform
import threading
import time
from datetime import datetime, timezone
from flask import Blueprint, render_template, jsonify, current_app

feature2_bp = Blueprint("feature2", __name__, template_folder="templates")
SERVER_START_TIME = time.time()


def get_system_telemetry():
    """Gathers server diagnostics and runtime telemetry."""
    uptime_seconds = int(time.time() - SERVER_START_TIME)
    
    # Process information
    process_info = {
        "pid": os.getpid(),
        "active_threads": threading.active_count(),
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s",
        "python_implementation": platform.python_implementation(),
        "python_version": sys.version.split()[0],
    }
    
    # System host metrics
    host_metrics = {
        "hostname": socket.gethostname(),
        "os_system": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count() or 1,
    }
    
    return process_info, host_metrics


@feature2_bp.route("/")
def index():
    """Feature 2 view: Live System Diagnostics & Performance Monitor."""
    process_info, host_metrics = get_system_telemetry()
    return render_template(
        "feature2/feature2.html",
        process=process_info,
        host=host_metrics,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        standalone_mode=current_app.config.get("STANDALONE_FEATURE", False)
    )


@feature2_bp.route("/api/diagnostics")
def diagnostics():
    """JSON API returning full health metrics for monitoring tools / Grafana / Datadog."""
    process_info, host_metrics = get_system_telemetry()
    return jsonify({
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "process": process_info,
        "host": host_metrics,
        "service": "feature2-diagnostics"
    }), 200


@feature2_bp.route("/api/health")
def health():
    """Health check endpoint for Feature 2 when running as an isolated service."""
    return jsonify({
        "service": "feature2",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200
