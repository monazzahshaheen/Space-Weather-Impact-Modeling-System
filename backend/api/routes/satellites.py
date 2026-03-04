"""
Satellite Routes
Endpoints for satellite data and TLE information
"""

from flask import Blueprint, request, jsonify
import json
import os

satellites_bp = Blueprint('satellites', __name__)

# Load satellite catalog
def load_satellite_catalog():
    """Load satellite catalog from JSON file"""
    catalog_path = 'data/satellite_catalog.json'
    if os.path.exists(catalog_path):
        with open(catalog_path, 'r') as f:
            return json.load(f)
    return {"satellites": []}

@satellites_bp.route('/list', methods=['GET'])
def list_satellites():
    """
    Get list of all satellites in catalog
    
    GET /api/satellites/list
    
    Returns: List of satellites with basic info
    """
    try:
        catalog = load_satellite_catalog()
        return jsonify({
            'success': True,
            'satellites': catalog.get('satellites', []),
            'total': len(catalog.get('satellites', []))
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@satellites_bp.route('/<satellite_id>', methods=['GET'])
def get_satellite(satellite_id):
    """
    Get detailed information about a specific satellite
    
    GET /api/satellites/<satellite_id>
    
    Returns: Satellite details
    """
    try:
        catalog = load_satellite_catalog()
        satellites = catalog.get('satellites', [])
        
        # Find satellite by ID or name
        satellite = next((s for s in satellites if s.get('id') == satellite_id or s.get('name') == satellite_id), None)
        
        if not satellite:
            return jsonify({
                'error': 'Satellite not found',
                'success': False
            }), 404
        
        return jsonify({
            'success': True,
            'satellite': satellite
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@satellites_bp.route('/by-altitude', methods=['GET'])
def get_by_altitude():
    """
    Get satellites filtered by altitude range
    
    GET /api/satellites/by-altitude?min=400&max=1000
    
    Returns: Filtered list of satellites
    """
    try:
        min_alt = float(request.args.get('min', 0))
        max_alt = float(request.args.get('max', 100000))
        
        catalog = load_satellite_catalog()
        satellites = catalog.get('satellites', [])
        
        filtered = [s for s in satellites if min_alt <= s.get('altitude', 0) <= max_alt]
        
        return jsonify({
            'success': True,
            'satellites': filtered,
            'total': len(filtered),
            'filter': {
                'min_altitude': min_alt,
                'max_altitude': max_alt
            }
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@satellites_bp.route('/by-orbit', methods=['GET'])
def get_by_orbit():
    """
    Get satellites by orbit type (LEO, MEO, GEO)
    
    GET /api/satellites/by-orbit?type=LEO
    
    Returns: Filtered list of satellites
    """
    try:
        orbit_type = request.args.get('type', 'LEO').upper()
        
        catalog = load_satellite_catalog()
        satellites = catalog.get('satellites', [])
        
        filtered = [s for s in satellites if s.get('orbit_type', '').upper() == orbit_type]
        
        return jsonify({
            'success': True,
            'satellites': filtered,
            'total': len(filtered),
            'orbit_type': orbit_type
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500