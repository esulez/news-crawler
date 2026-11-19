"""Dashboard module for displaying news articles."""

from .app import create_app
from .routes import main_routes

__all__ = ["create_app"]
