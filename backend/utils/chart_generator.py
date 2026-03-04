"""
Chart Generator for Multi-Satellite Comparison
Creates matplotlib/seaborn visualizations
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import io
import base64

# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

class SatelliteChartGenerator:
    def __init__(self):
        self.colors = {
            'CRITICAL': '#ef4444',
            'HIGH': '#f97316',
            'MEDIUM': '#f59e0b',
            'LOW': '#10b981'
        }
    
    def create_risk_comparison_chart(self, satellites_data, output_path='risk_comparison.png'):
        """
        Create bar chart comparing risk levels across satellites
        
        Args:
            satellites_data (list): List of dicts with satellite impact data
            output_path (str): Output file path
        
        Returns:
            str: Path to saved chart
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        names = [sat['name'][:20] for sat in satellites_data]
        scores = [sat['overall_risk_score'] for sat in satellites_data]
        risk_levels = [sat['risk_level'] for sat in satellites_data]
        
        # Create bars with colors based on risk level
        bars = ax.barh(names, scores)
        
        # Color bars based on risk level
        for bar, level in zip(bars, risk_levels):
            bar.set_color(self.colors.get(level, '#6b7280'))
        
        ax.set_xlabel('Risk Score (0-100)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Satellite', fontsize=12, fontweight='bold')
        ax.set_title('Multi-Satellite Risk Comparison', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 100)
        
        # Add risk level labels
        for i, (score, level) in enumerate(zip(scores, risk_levels)):
            ax.text(score + 2, i, f'{score:.0f} - {level}', 
                   va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved: {output_path}")
        return output_path
    
    def create_impact_breakdown_chart(self, satellites_data, output_path='impact_breakdown.png'):
        """
        Create stacked bar chart showing breakdown of different impact types
        
        Args:
            satellites_data (list): List of satellite data
            output_path (str): Output file path
        
        Returns:
            str: Path to saved chart
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        
        names = [sat['name'][:15] for sat in satellites_data]
        drag_scores = [sat.get('drag_score', 0) for sat in satellites_data]
        rad_scores = [sat.get('radiation_score', 0) for sat in satellites_data]
        signal_scores = [sat.get('signal_score', 0) for sat in satellites_data]
        
        x = np.arange(len(names))
        width = 0.6
        
        # Create stacked bars
        p1 = ax.bar(x, drag_scores, width, label='Atmospheric Drag', color='#3b82f6')
        p2 = ax.bar(x, rad_scores, width, bottom=drag_scores, label='Radiation', color='#f59e0b')
        p3 = ax.bar(x, signal_scores, width, 
                   bottom=np.array(drag_scores) + np.array(rad_scores),
                   label='Signal Degradation', color='#10b981')
        
        ax.set_xlabel('Satellite', fontsize=12, fontweight='bold')
        ax.set_ylabel('Impact Score', fontsize=12, fontweight='bold')
        ax.set_title('Impact Type Breakdown by Satellite', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.legend(loc='upper right', frameon=True, shadow=True)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved: {output_path}")
        return output_path
    
    def create_altitude_vs_risk_chart(self, satellites_data, output_path='altitude_risk.png'):
        """
        Create scatter plot of altitude vs risk score
        
        Args:
            satellites_data (list): List of satellite data
            output_path (str): Output file path
        
        Returns:
            str: Path to saved chart
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        altitudes = [sat['altitude'] for sat in satellites_data]
        risk_scores = [sat['overall_risk_score'] for sat in satellites_data]
        risk_levels = [sat['risk_level'] for sat in satellites_data]
        names = [sat['name'][:15] for sat in satellites_data]
        
        # Create scatter plot with colors by risk level
        for level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            mask = [l == level for l in risk_levels]
            alts = [a for a, m in zip(altitudes, mask) if m]
            scores = [s for s, m in zip(risk_scores, mask) if m]
            
            ax.scatter(alts, scores, c=self.colors[level], 
                      label=level, s=200, alpha=0.7, edgecolors='black', linewidth=1.5)
        
        # Add satellite labels
        for alt, score, name in zip(altitudes, risk_scores, names):
            ax.annotate(name, (alt, score), xytext=(5, 5), 
                       textcoords='offset points', fontsize=8, alpha=0.8)
        
        # Add Van Allen belt regions
        ax.axvspan(3000, 10000, alpha=0.1, color='red', label='Inner Van Allen Belt')
        ax.axvspan(15000, 25000, alpha=0.1, color='orange', label='Outer Van Allen Belt')
        
        ax.set_xlabel('Altitude (km)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Risk Score', fontsize=12, fontweight='bold')
        ax.set_title('Satellite Altitude vs Risk Score', fontsize=14, fontweight='bold', pad=20)
        ax.set_xscale('log')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', frameon=True, shadow=True)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved: {output_path}")
        return output_path
    
    def create_time_series_chart(self, satellite_name, hourly_predictions, output_path='time_series.png'):
        """
        Create time series chart of predicted risk over 24 hours
        
        Args:
            satellite_name (str): Name of satellite
            hourly_predictions (list): List of hourly prediction dicts
            output_path (str): Output file path
        
        Returns:
            str: Path to saved chart
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        hours = [p['hour'] for p in hourly_predictions]
        probabilities = [p['anomaly_probability'] * 100 for p in hourly_predictions]
        kp_values = [p.get('kp', 3) for p in hourly_predictions]
        
        # Anomaly probability over time
        ax1.plot(hours, probabilities, linewidth=2.5, color='#ef4444', marker='o', markersize=6)
        ax1.fill_between(hours, probabilities, alpha=0.3, color='#ef4444')
        ax1.axhline(y=70, color='red', linestyle='--', label='Critical Threshold', linewidth=2)
        ax1.axhline(y=50, color='orange', linestyle='--', label='High Threshold', linewidth=2)
        ax1.axhline(y=30, color='yellow', linestyle='--', label='Medium Threshold', linewidth=2)
        
        ax1.set_ylabel('Anomaly Probability (%)', fontsize=12, fontweight='bold')
        ax1.set_title(f'24-Hour Anomaly Prediction - {satellite_name}', 
                     fontsize=14, fontweight='bold', pad=20)
        ax1.legend(loc='upper right', frameon=True, shadow=True)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # Kp index over time
        ax2.plot(hours, kp_values, linewidth=2.5, color='#3b82f6', marker='s', markersize=6)
        ax2.fill_between(hours, kp_values, alpha=0.3, color='#3b82f6')
        ax2.axhline(y=5, color='orange', linestyle='--', label='Storm Threshold', linewidth=2)
        
        ax2.set_xlabel('Hour', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Kp Index', fontsize=12, fontweight='bold')
        ax2.set_title('Space Weather Conditions (Kp Index)', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right', frameon=True, shadow=True)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 9)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved: {output_path}")
        return output_path
    
    def create_heatmap_chart(self, satellites_data, kp_range, output_path='risk_heatmap.png'):
        """
        Create heatmap showing risk across satellites and Kp values
        
        Args:
            satellites_data (list): List of satellites
            kp_range (list): Range of Kp values to test
            output_path (str): Output file path
        
        Returns:
            str: Path to saved chart
        """
        from api.models.atmospheric_drag import calculate_drag_impact
        from api.models.radiation_dose import calculate_radiation_impact
        from api.models.signal_degradation import calculate_signal_impact
        
        # Create risk matrix
        sat_names = [sat['name'][:12] for sat in satellites_data]
        risk_matrix = []
        
        for sat in satellites_data:
            sat_risks = []
            for kp in kp_range:
                # Simplified risk calculation
                drag = calculate_drag_impact(sat['altitude'], kp, 150)
                rad = calculate_radiation_impact(sat['altitude'], kp, 100)
                sig = calculate_signal_impact(sat['altitude'], kp, sat.get('inclination', 45))
                
                # Combine scores (simplified)
                risk_score = (drag.get('increase', 0) * 0.3 + 
                            rad.get('seuProbability', 0) * 0.4 +
                            sig.get('degradation', 0) * 0.3)
                sat_risks.append(min(risk_score, 100))
            
            risk_matrix.append(sat_risks)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 8))
        
        im = ax.imshow(risk_matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)
        
        # Set ticks
        ax.set_xticks(np.arange(len(kp_range)))
        ax.set_yticks(np.arange(len(sat_names)))
        ax.set_xticklabels(kp_range)
        ax.set_yticklabels(sat_names)
        
        # Labels
        ax.set_xlabel('Kp Index', fontsize=12, fontweight='bold')
        ax.set_ylabel('Satellite', fontsize=12, fontweight='bold')
        ax.set_title('Risk Heatmap: Satellites vs Kp Index', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Risk Score', rotation=270, labelpad=20, fontweight='bold')
        
        # Add text annotations
        for i in range(len(sat_names)):
            for j in range(len(kp_range)):
                text = ax.text(j, i, f'{risk_matrix[i][j]:.0f}',
                             ha="center", va="center", color="white" if risk_matrix[i][j] > 50 else "black",
                             fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved: {output_path}")
        return output_path
    
    def to_base64(self, image_path):
        """Convert image to base64 for embedding in JSON/HTML"""
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')

# Convenience functions
def generate_all_comparison_charts(satellites_data, output_dir='charts'):
    """Generate all comparison charts"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    generator = SatelliteChartGenerator()
    
    charts = {
        'risk_comparison': generator.create_risk_comparison_chart(
            satellites_data, 
            f'{output_dir}/risk_comparison.png'
        ),
        'impact_breakdown': generator.create_impact_breakdown_chart(
            satellites_data,
            f'{output_dir}/impact_breakdown.png'
        ),
        'altitude_risk': generator.create_altitude_vs_risk_chart(
            satellites_data,
            f'{output_dir}/altitude_risk.png'
        ),
        'risk_heatmap': generator.create_heatmap_chart(
            satellites_data,
            list(range(0, 10)),
            f'{output_dir}/risk_heatmap.png'
        )
    }
    
    return charts