"""
Atmospheric Drag Impact Model
Based on NRLMSISE-00 atmospheric model (simplified)
"""

import math

def calculate_drag_impact(altitude, kp_index, f107_index):
    """
    Calculate atmospheric drag impact on satellite orbit
    
    Args:
        altitude (float): Satellite altitude in km
        kp_index (float): Geomagnetic activity index (0-9)
        f107_index (float): Solar flux index (70-250)
    
    Returns:
        dict: Drag impact metrics
    """
    # Baseline atmospheric density (kg/m³)
    # Exponential decay with altitude
    baseline_density = 1.225 * math.exp(-altitude / 8.5)
    
    # Kp effect on density (storms can increase density 2-10x)
    kp_multiplier = 1 + (kp_index - 3) * 0.4
    
    # F10.7 solar flux effect on thermosphere expansion
    solar_multiplier = 1 + (f107_index - 100) / 200
    
    # Current atmospheric density
    atmospheric_density = baseline_density * kp_multiplier * solar_multiplier
    
    # Orbital velocity (km/s) - simplified circular orbit
    mu = 398600.4418  # Earth gravitational parameter
    r = 6371 + altitude
    velocity = math.sqrt(mu / r)
    
    # Satellite parameters (typical values)
    if altitude < 1000:
        drag_coeff = 2.2
        area = 10  # m²
        mass = 500  # kg
    elif altitude < 10000:
        drag_coeff = 2.0
        area = 25
        mass = 2000
    else:
        drag_coeff = 1.8
        area = 50
        mass = 5000
    
    # Drag force: F = 0.5 * ρ * v² * Cd * A
    drag_force = 0.5 * atmospheric_density * math.pow(velocity * 1000, 2) * drag_coeff * area
    
    # Orbit decay rate (meters per day)
    # Simplified: a = F/m, then convert to altitude change
    decay_rate = (drag_force / mass) * 86400 * 0.5
    
    # Normal decay rate for comparison
    if altitude < 500:
        normal_decay = 100
    elif altitude < 1000:
        normal_decay = 20
    elif altitude < 10000:
        normal_decay = 2
    else:
        normal_decay = 0.1
    
    # Percentage increase from normal
    if normal_decay > 0:
        decay_increase = ((decay_rate / normal_decay) - 1) * 100
    else:
        decay_increase = 0
    
    # Days until reboost needed (assuming 1km safety margin)
    if decay_rate > 10:
        days_until_reboost = int(1000 / decay_rate)
    else:
        days_until_reboost = 999  # No immediate reboost needed
    
    return {
        'decayRate': max(0, decay_rate),
        'normalDecay': normal_decay,
        'increase': max(0, decay_increase),
        'daysUntilReboost': days_until_reboost,
        'atmosphericDensity': atmospheric_density,
        'dragForce': drag_force
    }