"""
Signal Degradation Model
Ionospheric scintillation and communication impacts
"""

def calculate_signal_impact(altitude, kp_index, inclination=45):
    """
    Calculate communication and signal degradation
    
    Args:
        altitude (float): Satellite altitude in km
        kp_index (float): Geomagnetic activity index (0-9)
        inclination (float): Orbital inclination in degrees
    
    Returns:
        dict: Signal impact metrics
    """
    # Ionospheric effects are strongest at LEO and high latitudes
    if altitude < 2000:
        ionospheric_factor = 1.0
    else:
        ionospheric_factor = 0.1
    
    # Polar regions experience more scintillation
    if abs(inclination) > 60:
        polar_factor = 1.5
    else:
        polar_factor = 1.0
    
    # Scintillation index based on Kp
    scintillation_index = max(0, (kp_index - 2) * ionospheric_factor * polar_factor)
    
    # Signal loss in dB
    signal_loss = min(80, scintillation_index * 12)
    
    # Signal degradation percentage
    degradation = min(100, signal_loss / 0.8)
    
    # GPS position error (only for MEO satellites ~20,000 km)
    is_gps = 19000 < altitude < 21000
    if is_gps:
        normal_error = 2  # meters
        error_multiplier = 1 + (kp_index - 3) * 0.8
        position_error = normal_error * error_multiplier
    else:
        position_error = 0
    
    # Communication blackout duration (severe storms only)
    if kp_index >= 7:
        blackout_duration = 4 + (kp_index - 7) * 2
    else:
        blackout_duration = 0
    
    # Signal quality assessment
    if signal_loss < 10:
        quality = 'GOOD'
    elif signal_loss < 30:
        quality = 'DEGRADED'
    else:
        quality = 'SEVERE'
    
    return {
        'signalLoss': signal_loss,
        'degradation': degradation,
        'positionError': position_error,
        'blackoutDuration': blackout_duration,
        'quality': quality,
        'scintillationIndex': scintillation_index
    }