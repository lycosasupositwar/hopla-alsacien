import os
from flask import Blueprint, jsonify, request

logs_bp = Blueprint('logs', __name__)

LOG_DIR = "/var/log/app"
LOG_FILES = {
    "backend_access": os.path.join(LOG_DIR, "backend_access.log"),
    "backend_error": os.path.join(LOG_DIR, "backend_error.log"),
    "nginx_access": os.path.join(LOG_DIR, "nginx_access.log"),
    "nginx_error": os.path.join(LOG_DIR, "nginx_error.log"),
}

def read_log_file(path: str, max_lines: int = 200) -> str:
    """Reads the last `max_lines` of a file, returning an empty string if not found."""
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            return "".join(lines[-max_lines:])
    except FileNotFoundError:
        return f"Log file not found at {path}"
    except Exception as e:
        return f"Error reading log file at {path}: {str(e)}"

@logs_bp.route('/logs', methods=['GET'])
def get_logs():
    """
    Fetches the latest logs from all configured log files.
    Accepts a `max_lines` query parameter.
    """
    try:
        max_lines = int(request.args.get('max_lines', 200))
    except (ValueError, TypeError):
        max_lines = 200

    all_logs = {
        key: read_log_file(path, max_lines)
        for key, path in LOG_FILES.items()
    }

    return jsonify(all_logs)
