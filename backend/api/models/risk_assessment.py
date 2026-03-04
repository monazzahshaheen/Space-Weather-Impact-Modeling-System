"""
Overall Risk Assessment and Recommendations Generator
"""

def calculate_overall_risk(drag, radiation, signal):
    """
    Calculate overall risk score from individual impact components
    
    Args:
        drag (dict): Atmospheric drag impact data
        radiation (dict): Radiation impact data
        signal (dict): Signal degradation data
    
    Returns:
        dict: Overall risk score and level
    """
    risk_score = 0
    
    # Drag risk contribution (0-30 points)
    if drag['decayRate'] > 100:
        risk_score += 30
    elif drag['decayRate'] > 50:
        risk_score += 20
    elif drag['decayRate'] > 10:
        risk_score += 10
    elif drag['decayRate'] > 5:
        risk_score += 5
    
    # Radiation risk contribution (0-40 points)
    if radiation['seuProbability'] > 50:
        risk_score += 40
    elif radiation['seuProbability'] > 30:
        risk_score += 30
    elif radiation['seuProbability'] > 20:
        risk_score += 20
    elif radiation['seuProbability'] > 5:
        risk_score += 10
    
    # Signal risk contribution (0-30 points)
    if signal['signalLoss'] > 40:
        risk_score += 30
    elif signal['signalLoss'] > 20:
        risk_score += 20
    elif signal['signalLoss'] > 10:
        risk_score += 10
    
    # Risk level classification
    if risk_score >= 70:
        risk_level = 'CRITICAL'
    elif risk_score >= 50:
        risk_level = 'HIGH'
    elif risk_score >= 25:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
    
    return {
        'score': risk_score,
        'level': risk_level
    }

def generate_recommendations(impacts):
    """
    Generate actionable recommendations based on impact analysis
    
    Args:
        impacts (dict): Dictionary containing drag, radiation, signal, and overall impacts
    
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    drag = impacts.get('drag', {})
    radiation = impacts.get('radiation', {})
    signal = impacts.get('signal', {})
    overall = impacts.get('overall', {})
    
    # Critical level recommendations
    if overall.get('level') == 'CRITICAL':
        recommendations.append("🚨 CRITICAL: Activate emergency protocols immediately")
        recommendations.append("📡 Switch to backup systems and redundant communication")
        recommendations.append("🛡️ Enable all error correction and protection mechanisms")
    
    # High level recommendations
    if overall.get('level') == 'HIGH':
        recommendations.append("⚠️ HIGH RISK: Increase monitoring frequency to every 5 minutes")
        recommendations.append("📊 Review telemetry for early warning signs")
    
    # Drag-related recommendations
    if drag.get('daysUntilReboost', 999) < 30:
        recommendations.append(f"🚀 Schedule orbit reboost maneuver within {drag.get('daysUntilReboost')} days")
    elif drag.get('decayRate', 0) > 50:
        recommendations.append("📉 Monitor orbit decay closely - increased atmospheric drag detected")
    
    # Radiation-related recommendations
    if radiation.get('seuProbability', 0) > 40:
        recommendations.append("⚡ Enable redundant systems - high SEU probability")
        recommendations.append("💾 Increase memory scrubbing frequency")
    elif radiation.get('seuProbability', 0) > 20:
        recommendations.append("🛡️ Monitor telemetry for bit flips and anomalies")
    
    # Signal-related recommendations
    if signal.get('blackoutDuration', 0) > 0:
        recommendations.append(f"📡 Expect communication blackout: {signal.get('blackoutDuration')} hours")
        recommendations.append("🔄 Switch to backup communication systems")
    elif signal.get('degradation', 0) > 40:
        recommendations.append("📶 Signal degradation detected - use error correction")
    
    # General recommendations
    if overall.get('level') == 'MEDIUM':
        recommendations.append("⚠️ Enhanced monitoring mode recommended")
    
    # If no critical issues, provide normal operations guidance
    if not recommendations:
        recommendations.append("✅ Continue normal operations")
        recommendations.append("📊 Standard telemetry monitoring sufficient")
    else:
        # Always add monitoring recommendation
        recommendations.append("👨‍💻 Ensure ground station coverage")
        recommendations.append("📝 Prepare contingency plans")
    
    return recommendations