from flask import Flask, jsonify
from flask_cors import CORS

from .api.analysis import analysis_bp
from .api.reports import reports_bp
from .api.preview import preview_bp
from .api.logs import logs_bp

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # Enable CORS for all domains on all routes.
    # For a production environment, you would want to restrict this
    # to the specific domain of your frontend.
    CORS(app)

    # Register blueprints
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')
    app.register_blueprint(preview_bp, url_prefix='/api/preview')
    app.register_blueprint(logs_bp, url_prefix='/api')

    @app.route("/")
    def health_check():
        """A simple health check endpoint."""
        return jsonify({
            "status": "ok",
            "message": "Grain Size Analysis API is running."
        })

    return app

# This allows running the app directly with `python -m app.main` for development
# For production, Gunicorn will be used, and it will import `app` from this file.
app = create_app()

if __name__ == '__main__':
    # Note: This is for development only.
    # In production, use a WSGI server like Gunicorn.
    app.run(debug=True, host='0.0.0.0', port=8000)
