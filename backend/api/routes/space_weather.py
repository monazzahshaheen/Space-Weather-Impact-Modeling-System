"""
Space Weather Routes
Endpoints for fetching real-time and historical space weather data
"""

from flask import Blueprint, request, jsonify
import requests
import json
import os
from datetime import datetime, timedelta

space_weather_bp = Blueprint('space_weather', __name__)

@space_weather_bp.route('/current', methods=['GET'])
def get_current():
    """
    Get current space weather conditions from NOAA
    
    GET /api/space-weather/current
    
    Returns: Current Kp, F10.7, solar wind, etc.
    """
    try:
        # Fetch from NOAA APIs
        kp = fetch_kp_index()
        f107 = fetch_f107()
        solar_wind = fetch_solar_wind()
        proton_flux = fetch_proton_flux()
        
        return jsonify({
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'kpIndex': kp,
                'f107': f107,
                'solarWindSpeed': solar_wind.get('speed', 400),
                'solarWindDensity': solar_wind.get('density', 5),
                'protonFlux': proton_flux
            }
        })
    except Exception as e:
        # Return default values if API fails
        return jsonify({
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'kpIndex': 3,
                'f107': 120,
                'solarWindSpeed': 400,
                'solarWindDensity': 5,
                'protonFlux': 10
            },
            'note': 'Using default values - API unavailable'
        })

@space_weather_bp.route('/historical', methods=['GET'])
def get_historical():
    """
    Get historical space weather events
    
    GET /api/space-weather/historical
    
    Returns: List of major historical events
    """
    try:
        events_path = 'data/historical_events.json'
        if os.path.exists(events_path):
            with open(events_path, 'r') as f:
                data = json.load(f)
                return jsonify({
                    'success': True,
                    'events': data.get('events', []),
                    'total': len(data.get('events', []))
                })
        else:
            return jsonify({
                'error': 'Historical events file not found',
                'success': False
            }), 404
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@space_weather_bp.route('/historical/<event_id>', methods=['GET'])
def get_historical_event(event_id):
    """
    Get details of a specific historical event
    
    GET /api/space-weather/historical/halloween_2003
    
    Returns: Event details with space weather data and impacts
    """
    try:
        events_path = 'data/historical_events.json'
        if os.path.exists(events_path):
            with open(events_path, 'r') as f:
                data = json.load(f)
                events = data.get('events', [])
                
                # Find event by ID
                event = next((e for e in events if e.get('id') == event_id), None)
                
                if not event:
                    return jsonify({
                        'error': 'Event not found',
                        'success': False
                    }), 404
                
                return jsonify({
                    'success': True,
                    'event': event
                })
        else:
            return jsonify({
                'error': 'Historical events file not found',
                'success': False
            }), 404
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@space_weather_bp.route('/forecast', methods=['GET'])
def get_forecast():
    """
    Get 3-day space weather forecast
    
    GET /api/space-weather/forecast
    
    Returns: 72-hour forecast
    """
    try:
        # Try to fetch from NOAA
        url = "https://services.swpc.noaa.gov/json/3-day-forecast.json"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'forecast': data
            })
        else:
            # Return simulated forecast
            forecast = []
            for i in range(72):
                forecast.append({
                    'hour': i,
                    'kpIndex': 3 + (i % 3),
                    'f107': 120 + (i % 20),
                    'solarWindSpeed': 400 + (i % 100)
                })
            
            return jsonify({
                'success': True,
                'forecast': forecast,
                'note': 'Simulated data - API unavailable'
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

# Helper functions to fetch real data
def fetch_kp_index():
    """Fetch current Kp index from NOAA"""
    try:
        url = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data[-1].get('kp_index', 3))
    except:
        pass
    return 3.0

def fetch_f107():
    """Fetch F10.7 solar flux from NOAA"""
    try:
        url = "https://services.swpc.noaa.gov/json/f10_7_cm_flux.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data[-1].get('flux', 120))
    except:
        pass
    return 120.0

def fetch_solar_wind():
    """Fetch solar wind data from NOAA"""
    try:
        url = "https://services.swpc.noaa.gov/json/plasma-7-day.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest = data[-1]
            return {
                'speed': float(latest.get('speed', 400)),
                'density': float(latest.get('density', 5))
            }
    except:
        pass
    return {'speed': 400, 'density': 5}

def fetch_proton_flux():
    """Fetch proton flux from NOAA"""
    try:
        url = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-plot-6-hour.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data[-1].get('flux', 10))
    except:
        pass
    return 10.0