"""
ML Prediction Module for Satellite Anomaly Detection
"""

import numpy as np
import joblib
import json
import os
from datetime import datetime, timedelta

class AnomalyPredictor:
    def __init__(self, model_dir='ml/models'):
        """Initialize predictor with trained models"""
        self.model_dir = model_dir
        self.rf_model = None
        self.gb_model = None
        self.scaler = None
        self.feature_names = None
        self.metadata = None
        
        self.load_models()
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            self.rf_model = joblib.load(os.path.join(self.model_dir, 'rf_anomaly_detector.pkl'))
            self.gb_model = joblib.load(os.path.join(self.model_dir, 'gb_anomaly_detector.pkl'))
            self.scaler = joblib.load(os.path.join(self.model_dir, 'scaler.pkl'))
            
            with open(os.path.join(self.model_dir, 'feature_names.json'), 'r') as f:
                self.feature_names = json.load(f)
            
            with open(os.path.join(self.model_dir, 'model_metadata.json'), 'r') as f:
                self.metadata = json.load(f)
            
            print(f"✅ Models loaded successfully (trained: {self.metadata['training_date'][:10]})")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            print("Run train_model.py first to create the models.")
            raise
    
    def prepare_features(self, space_weather, satellite):
        """
        Prepare feature vector from space weather and satellite data
        
        Args:
            space_weather (dict): {kp, dst, f107, solar_wind_speed, proton_flux}
            satellite (dict): {altitude, orbit_type, shielding, age_years}
        
        Returns:
            numpy array: Feature vector
        """
        # Extract orbit type
        orbit_type = satellite.get('orbit_type', 'LEO')
        
        # Extract shielding
        shielding = satellite.get('shielding', 'medium')
        
        features = {
            'kp': space_weather.get('kpIndex', 3),
            'dst': space_weather.get('dst', -30),
            'f107': space_weather.get('f107', 120),
            'solar_wind_speed': space_weather.get('solarWindSpeed', 400),
            'proton_flux': space_weather.get('protonFlux', 100),
            'altitude': satellite.get('altitude', 400),
            'orbit_type_LEO': 1 if orbit_type == 'LEO' else 0,
            'orbit_type_MEO': 1 if orbit_type == 'MEO' else 0,
            'orbit_type_GEO': 1 if orbit_type == 'GEO' else 0,
            'shielding_low': 1 if shielding == 'low' else 0,
            'shielding_medium': 1 if shielding == 'medium' else 0,
            'shielding_high': 1 if shielding == 'high' else 0,
            'age_years': satellite.get('age_years', 5)
        }
        
        # Ensure correct order
        feature_vector = [features[name] for name in self.feature_names]
        
        return np.array([feature_vector])
    
    def predict_anomaly(self, space_weather, satellite, use_ensemble=True):
        """
        Predict probability of satellite anomaly
        
        Args:
            space_weather (dict): Current space weather conditions
            satellite (dict): Satellite parameters
            use_ensemble (bool): Use ensemble of models for prediction
        
        Returns:
            dict: Prediction results
        """
        # Prepare features
        X = self.prepare_features(space_weather, satellite)
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from both models
        rf_proba = self.rf_model.predict_proba(X_scaled)[0, 1]
        gb_proba = self.gb_model.predict_proba(X_scaled)[0, 1]
        
        # Ensemble prediction (average)
        if use_ensemble:
            anomaly_probability = (rf_proba + gb_proba) / 2
        else:
            anomaly_probability = rf_proba
        
        # Determine risk level
        if anomaly_probability > 0.7:
            risk_level = "CRITICAL"
        elif anomaly_probability > 0.5:
            risk_level = "HIGH"
        elif anomaly_probability > 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            anomaly_probability, space_weather, satellite
        )
        
        return {
            'anomaly_probability': float(anomaly_probability),
            'risk_level': risk_level,
            'confidence': float(min(abs(rf_proba - gb_proba), 0.95)),  # Lower diff = higher confidence
            'rf_prediction': float(rf_proba),
            'gb_prediction': float(gb_proba),
            'recommendations': recommendations,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def predict_24h_ahead(self, space_weather_forecast, satellite):
        """
        Predict anomaly probability for next 24 hours
        
        Args:
            space_weather_forecast (list): List of hourly forecasts
            satellite (dict): Satellite parameters
        
        Returns:
            dict: 24-hour prediction timeline
        """
        predictions = []
        
        for i, forecast in enumerate(space_weather_forecast[:24]):
            pred = self.predict_anomaly(forecast, satellite)
            pred['hour'] = i
            predictions.append(pred)
        
        # Calculate peak risk
        peak_risk = max(predictions, key=lambda x: x['anomaly_probability'])
        
        return {
            'hourly_predictions': predictions,
            'peak_risk': {
                'hour': peak_risk['hour'],
                'probability': peak_risk['anomaly_probability'],
                'level': peak_risk['risk_level']
            },
            'average_risk': float(np.mean([p['anomaly_probability'] for p in predictions])),
            'satellite': satellite.get('name', 'Unknown')
        }
    
    def _generate_recommendations(self, probability, space_weather, satellite):
        """Generate actionable recommendations based on prediction"""
        recommendations = []
        
        kp = space_weather.get('kpIndex', 3)
        altitude = satellite.get('altitude', 400)
        
        if probability > 0.7:
            recommendations.append("🚨 CRITICAL: Activate emergency protocols immediately")
            recommendations.append("📡 Switch to backup systems and redundant communication")
            recommendations.append("🛡️ Enable all error correction and protection mechanisms")
        
        if probability > 0.5:
            recommendations.append("⚠️ HIGH RISK: Increase monitoring frequency to every 5 minutes")
            recommendations.append("📊 Review telemetry for early warning signs")
        
        if kp > 6 and altitude < 1000:
            recommendations.append("🚀 Consider orbit reboost maneuver if possible")
            recommendations.append("📉 Expect significant atmospheric drag increase")
        
        if altitude > 3000 and altitude < 25000:
            recommendations.append("☢️ Monitor radiation dose accumulation")
            recommendations.append("💾 Increase memory scrubbing frequency")
        
        if probability > 0.3:
            recommendations.append("👨‍💻 Ensure ground station coverage")
            recommendations.append("📝 Prepare contingency plans")
        
        if not recommendations:
            recommendations.append("✅ Risk level acceptable - continue normal operations")
            recommendations.append("📊 Maintain standard monitoring procedures")
        
        return recommendations

# Global predictor instance
_predictor = None

def get_predictor():
    """Get or create global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = AnomalyPredictor()
    return _predictor

def predict_satellite_anomaly(space_weather, satellite):
    """Convenience function for making predictions"""
    predictor = get_predictor()
    return predictor.predict_anomaly(space_weather, satellite)