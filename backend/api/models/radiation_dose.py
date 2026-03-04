"""
Radiation Dose Impact Model
Based on AP-8 (protons) and AE-8 (electrons) models (simplified)
"""

import math

def calculate_radiation_impact(altitude, kp_index, proton_flux=100):
    """
    Calculate radiation dose and SEU probability
    
    Args:
        altitude (float): Satellite altitude in km
        kp_index (float): Geomagnetic activity index (0-9)
        proton_flux (float): Solar energetic proton flux (pfu)
    
    Returns:
        dict: Radiation impact metrics
    """
    # Van Allen radiation belts
    # Inner belt (protons): ~3,000-10,000 km, peak at 6,000 km
    # Outer belt (electrons): ~15,000-25,000 km, peak at 20,000 km
    
    inner_belt_peak = 6000
    outer_belt_peak = 20000
    
    # Gaussian distribution for belt intensity
    inner_belt_factor = math.exp(-math.pow((altitude - inner_belt_peak) / 4000, 2))
    outer_belt_factor = math.exp(-math.pow((altitude - outer_belt_peak) / 8000, 2))
    
    # Combined belt factor (max of both)
    belt_factor = max(inner_belt_factor, outer_belt_factor)
    
    # Outside belts, radiation is much lower
    if altitude > 25000 or altitude < 1000:
        outside_belts = 0.1
    else:
        outside_belts = 1.0
    
    # Geomagnetic storm effect (pushes belts lower and intensifies)
    storm_multiplier = 1 + (kp_index - 3) * 0.3
    
    # Solar energetic particle contribution
    if altitude < 2000:
        proton_contribution = 0.5  # LEO has some atmospheric shielding
    else:
        proton_contribution = 1.0
    
    proton_dose = (proton_flux / 100) * proton_contribution
    
    # Baseline dose (mrad/day)
    baseline_dose = 10
    current_dose = baseline_dose * belt_factor * outside_belts * storm_multiplier * (1 + proton_dose)
    
    # Single Event Upset (SEU) probability
    # Depends on dose and satellite shielding
    # Simplified: assume medium shielding
    if altitude < 1000:
        shielding_factor = 0.6  # LEO has atmospheric protection
    elif altitude < 10000:
        shielding_factor = 0.8
    else:
        shielding_factor = 1.0
    
    seu_probability = min(95, current_dose * shielding_factor * 0.5)
    
    # Safe mode risk assessment
    if seu_probability > 50:
        safe_mode_risk = 'HIGH'
    elif seu_probability > 20:
        safe_mode_risk = 'MEDIUM'
    else:
        safe_mode_risk = 'LOW'
    
    return {
        'dose': current_dose,
        'seuProbability': seu_probability,
        'safeModeRisk': safe_mode_risk,
        'beltFactor': belt_factor
    }