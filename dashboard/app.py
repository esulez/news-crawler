"""Flask application for the news dashboard."""

from flask import Flask, render_template, jsonify, request
from storage.database import Database
from crawler.crawler import NewsCrawler
from utils.deduplicator import Deduplicator
import os
from datetime import datetime


def create_app(config_path: str = None, db_path: str = "data/news.db"):
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DATABASE_PATH'] = db_path
    app.config['CONFIG_PATH'] = config_path
    
    # Initialize components
    database = Database(db_path)
    crawler = NewsCrawler(config_path, db_path)
    deduplicator = Deduplicator(db_path)
    
    # Register blueprints or routes
    from . import routes
    app.register_blueprint(routes.main_routes)
    
    # Make components available to routes
    app.database = database
    app.crawler = crawler
    app.deduplicator = deduplicator
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
