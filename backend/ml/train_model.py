"""
Train Machine Learning Model for Satellite Anomaly Prediction
Uses Random Forest and Neural Network ensemble
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import json
from datetime import datetime

def generate_synthetic_training_data(n_samples=10000):
    """
    Generate synthetic training data based on known space weather impacts
    In production, replace with actual historical satellite anomaly data
    """
    np.random.seed(42)
    
    data = []
    
    for _ in range(n_samples):
        # Space weather parameters
        kp = np.random.uniform(0, 9)
        dst = np.random.uniform(-400, 20)
        f107 = np.random.uniform(70, 250)
        solar_wind_speed = np.random.uniform(300, 900)
        proton_flux = np.random.uniform(1, 10000)
        
        # Satellite parameters
        altitude = np.random.choice([400, 550, 800, 1200, 20200, 35786])
        orbit_type = 'LEO' if altitude < 2000 else ('MEO' if altitude < 35786 else 'GEO')
        shielding = np.random.choice(['low', 'medium', 'high'])
        age_years = np.random.uniform(0, 15)
        
        # Calculate risk factors
        drag_risk = (kp / 9) * (f107 / 250) * (1 / (altitude / 400)) if altitude < 2000 else 0
        radiation_risk = 0
        if 3000 < altitude < 25000:  # Van Allen belts
            radiation_risk = (kp / 9) * (proton_flux / 10000) * (1 if shielding == 'low' else 0.5 if shielding == 'medium' else 0.3)
        
        signal_risk = (kp / 9) * (1 if altitude < 2000 else 0.3)
        
        # Determine if anomaly occurred (based on combined risks)
        anomaly_probability = (drag_risk + radiation_risk + signal_risk) / 3
        anomaly_probability *= (1 + age_years / 30)  # Older satellites more vulnerable
        
        # Add some noise
        anomaly_probability += np.random.normal(0, 0.1)
        anomaly_probability = np.clip(anomaly_probability, 0, 1)
        
        # Binary outcome
        anomaly = 1 if anomaly_probability > 0.4 else 0
        
        data.append({
            'kp': kp,
            'dst': dst,
            'f107': f107,
            'solar_wind_speed': solar_wind_speed,
            'proton_flux': proton_flux,
            'altitude': altitude,
            'orbit_type_LEO': 1 if orbit_type == 'LEO' else 0,
            'orbit_type_MEO': 1 if orbit_type == 'MEO' else 0,
            'orbit_type_GEO': 1 if orbit_type == 'GEO' else 0,
            'shielding_low': 1 if shielding == 'low' else 0,
            'shielding_medium': 1 if shielding == 'medium' else 0,
            'shielding_high': 1 if shielding == 'high' else 0,
            'age_years': age_years,
            'anomaly': anomaly
        })
    
    return pd.DataFrame(data)

def train_models():
    """Train and save anomaly prediction models"""
    print("Generating training data...")
    df = generate_synthetic_training_data(n_samples=10000)
    
    # Save training data
    df.to_csv('ml/data/training_data.csv', index=False)
    print(f"Training data saved: {len(df)} samples")
    print(f"Anomaly rate: {df['anomaly'].mean():.2%}")
    
    # Split features and target
    X = df.drop('anomaly', axis=1)
    y = df['anomaly']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("\n" + "="*60)
    print("Training Random Forest Model...")
    print("="*60)
    
    # Train Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_train)
    
    # Evaluate
    rf_pred = rf_model.predict(X_test_scaled)
    rf_proba = rf_model.predict_proba(X_test_scaled)[:, 1]
    
    print("\nRandom Forest Performance:")
    print(classification_report(y_test, rf_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, rf_proba):.4f}")
    
    # Cross-validation
    cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5)
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    print("\n" + "="*60)
    print("Training Gradient Boosting Model...")
    print("="*60)
    
    # Train Gradient Boosting
    gb_model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    gb_model.fit(X_train_scaled, y_train)
    
    # Evaluate
    gb_pred = gb_model.predict(X_test_scaled)
    gb_proba = gb_model.predict_proba(X_test_scaled)[:, 1]
    
    print("\nGradient Boosting Performance:")
    print(classification_report(y_test, gb_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, gb_proba):.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n" + "="*60)
    print("Top 10 Most Important Features:")
    print("="*60)
    print(feature_importance.head(10).to_string(index=False))
    
    # Save models
    print("\n" + "="*60)
    print("Saving models...")
    print("="*60)
    
    joblib.dump(rf_model, 'ml/models/rf_anomaly_detector.pkl')
    joblib.dump(gb_model, 'ml/models/gb_anomaly_detector.pkl')
    joblib.dump(scaler, 'ml/models/scaler.pkl')
    
    # Save feature names
    with open('ml/models/feature_names.json', 'w') as f:
        json.dump(list(X.columns), f)
    
    # Save model metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'n_samples': len(df),
        'anomaly_rate': float(df['anomaly'].mean()),
        'rf_accuracy': float((rf_pred == y_test).mean()),
        'rf_roc_auc': float(roc_auc_score(y_test, rf_proba)),
        'gb_accuracy': float((gb_pred == y_test).mean()),
        'gb_roc_auc': float(roc_auc_score(y_test, gb_proba)),
        'features': list(X.columns),
        'top_features': feature_importance.head(10).to_dict('records')
    }
    
    with open('ml/models/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n✅ Models saved successfully!")
    print(f"   - Random Forest: ml/models/rf_anomaly_detector.pkl")
    print(f"   - Gradient Boosting: ml/models/gb_anomaly_detector.pkl")
    print(f"   - Scaler: ml/models/scaler.pkl")
    print(f"   - Metadata: ml/models/model_metadata.json")
    
    return rf_model, gb_model, scaler, metadata

if __name__ == '__main__':
    import os
    
    # Create directories
    os.makedirs('ml/models', exist_ok=True)
    os.makedirs('ml/data', exist_ok=True)
    
    # Train models
    rf_model, gb_model, scaler, metadata = train_models()
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"Model Accuracy: {metadata['rf_accuracy']:.2%}")
    print(f"ROC-AUC Score: {metadata['rf_roc_auc']:.4f}")
    print("\nThe models are ready to make predictions!")