"""
Routes package initialization
"""

from .satellites import satellites_bp
from .space_weather import space_weather_bp
from .predictions import predictions_bp
from .reports import reports_bp

__all__ = ['satellites_bp', 'space_weather_bp', 'predictions_bp', 'reports_bp']