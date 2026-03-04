"""
ML Prediction Routes
Endpoints for satellite anomaly prediction
"""

from flask import Blueprint, request, jsonify
import sys
import os

#Fix import paths
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

from ml.predict import get_predictor, predict_satellite_anomaly

predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/anomaly', methods=['POST'])
def predict_anomaly():
    """
    Predict satellite anomaly probability
    
    POST /api/predictions/anomaly
    Body: {
        "space_weather": {
            "kpIndex": 5,
            "dst": -50,
            "f107": 150,
            "solarWindSpeed": 500,
            "protonFlux": 500
        },
        "satellite": {
            "name": "ISS",
            "altitude": 408,
            "orbit_type": "LEO",
            "shielding": "medium",
            "age_years": 25
        }
    }
    
    Returns: Prediction with probability and recommendations
    """
    try:
        data = request.json
        space_weather = data.get('space_weather', {})
        satellite = data.get('satellite', {})
        
        # Validate required fields
        if not space_weather or not satellite:
            return jsonify({
                'error': 'Missing required fields',
                'required': ['space_weather', 'satellite']
            }), 400
        
        # Make prediction
        result = predict_satellite_anomaly(space_weather, satellite)
        
        return jsonify({
            'success': True,
            'prediction': result,
            'satellite': satellite.get('name', 'Unknown')
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@predictions_bp.route('/24h-forecast', methods=['POST'])
def predict_24h():
    """
    Predict anomaly probability for next 24 hours
    
    POST /api/predictions/24h-forecast
    Body: {
        "space_weather_forecast": [
            {"kpIndex": 5, "f107": 150, ...},  // Hour 0
            {"kpIndex": 6, "f107": 160, ...},  // Hour 1
            ... // 24 entries
        ],
        "satellite": {...}
    }
    
    Returns: Hour-by-hour predictions
    """
    try:
        data = request.json
        forecast = data.get('space_weather_forecast', [])
        satellite = data.get('satellite', {})
        
        if not forecast or not satellite:
            return jsonify({
                'error': 'Missing required fields'
            }), 400
        
        predictor = get_predictor()
        result = predictor.predict_24h_ahead(forecast, satellite)
        
        return jsonify({
            'success': True,
            'forecast': result
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@predictions_bp.route('/batch', methods=['POST'])
def predict_batch():
    """
    Predict anomalies for multiple satellites
    
    POST /api/predictions/batch
    Body: {
        "space_weather": {...},
        "satellites": [
            {"name": "ISS", "altitude": 408, ...},
            {"name": "GPS", "altitude": 20200, ...},
            ...
        ]
    }
    
    Returns: Predictions for all satellites
    """
    try:
        data = request.json
        space_weather = data.get('space_weather', {})
        satellites = data.get('satellites', [])
        
        if not space_weather or not satellites:
            return jsonify({
                'error': 'Missing required fields'
            }), 400
        
        results = []
        for sat in satellites:
            try:
                prediction = predict_satellite_anomaly(space_weather, sat)
                results.append({
                    'satellite': sat.get('name', 'Unknown'),
                    'prediction': prediction
                })
            except Exception as e:
                results.append({
                    'satellite': sat.get('name', 'Unknown'),
                    'error': str(e)
                })
        
        # Sort by risk level
        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        results.sort(key=lambda x: risk_order.get(x.get('prediction', {}).get('risk_level', 'LOW'), 4))
        
        return jsonify({
            'success': True,
            'predictions': results,
            'total': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@predictions_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """
    Get information about loaded ML models
    
    GET /api/predictions/model-info
    
    Returns: Model metadata and performance metrics
    """
    try:
        predictor = get_predictor()
        
        return jsonify({
            'success': True,
            'model_info': predictor.metadata,
            'models_loaded': {
                'random_forest': predictor.rf_model is not None,
                'gradient_boosting': predictor.gb_model is not None,
                'scaler': predictor.scaler is not None
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500