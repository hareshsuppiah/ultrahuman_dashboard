import requests
from flask import Blueprint, jsonify, request
from src.models.user import User, db

metrics_bp = Blueprint("metrics", __name__)

ULTRAHUMAN_API_URL = "https://partner.ultrahuman.com/api/v1/metrics"

@metrics_bp.route("/metrics/<int:user_id>", methods=["GET"])
def get_metrics(user_id):
    """Fetches metrics for a given user and date from the Ultrahuman API."""
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "Date parameter (YYYY-MM-DD) is required"}), 400

    # Validate date format (basic check)
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    headers = {
        "Authorization": user.api_key
    }
    params = {
        "email": user.email,
        "date": date_str
    }

    try:
        response = requests.get(ULTRAHUMAN_API_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        # Check if the response content type is JSON before parsing
        if "application/json" in response.headers.get("Content-Type", ""):
            return jsonify(response.json())
        else:
            # Handle non-JSON responses (e.g., HTML error pages from API)
            return jsonify({"error": "Received non-JSON response from Ultrahuman API", "status_code": response.status_code, "content": response.text}), 502

    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        return jsonify({"error": f"Error connecting to Ultrahuman API: {e}"}), 503
    except Exception as e:
        # Catch other potential errors during the process
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

