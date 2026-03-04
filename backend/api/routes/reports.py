"""
Report Generation Routes
Endpoints for creating PDF reports and comparison charts
"""

from flask import Blueprint, request, jsonify, send_file
import sys
import os

# Fix import paths
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

from utils.pdf_generator import generate_satellite_report
from utils.chart_generator import SatelliteChartGenerator, generate_all_comparison_charts
from ml.predict import predict_satellite_anomaly
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

# Rest of the file stays the same...

@reports_bp.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF report for a satellite
    
    POST /api/reports/generate-pdf
    Body: {
        "satellite_name": "ISS",
        "space_weather": {...},
        "impacts": {...},
        "predictions": {...}
    }
    
    Returns: PDF file
    """
    try:
        data = request.json
        satellite_name = data.get('satellite_name', 'Unknown Satellite')
        space_weather = data.get('space_weather', {})
        impacts = data.get('impacts', {})
        predictions = data.get('predictions', {})
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{satellite_name.replace(' ', '_')}_{timestamp}.pdf"
        output_path = f"reports/{filename}"
        
        # Create reports directory
        os.makedirs('reports', exist_ok=True)
        
        # Generate report
        generate_satellite_report(
            satellite_name,
            space_weather,
            impacts,
            predictions,
            output_path
        )
        
        # Send file
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@reports_bp.route('/comparison-charts', methods=['POST'])
def generate_comparison_charts():
    """
    Generate multi-satellite comparison charts
    
    POST /api/reports/comparison-charts
    Body: {
        "satellites": [
            {
                "name": "ISS",
                "altitude": 408,
                "overall_risk_score": 45,
                "risk_level": "MEDIUM",
                "drag_score": 20,
                "radiation_score": 15,
                "signal_score": 10
            },
            ...
        ]
    }
    
    Returns: Paths to generated chart images
    """
    try:
        data = request.json
        satellites_data = data.get('satellites', [])
        
        if not satellites_data:
            return jsonify({
                'error': 'No satellite data provided'
            }), 400
        
        # Create charts directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f"charts/{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate all charts
        charts = generate_all_comparison_charts(satellites_data, output_dir)
        
        return jsonify({
            'success': True,
            'charts': charts,
            'total': len(charts)
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@reports_bp.route('/risk-comparison', methods=['POST'])
def create_risk_comparison():
    """Generate risk comparison bar chart"""
    try:
        data = request.json
        satellites_data = data.get('satellites', [])
        
        os.makedirs('charts', exist_ok=True)
        generator = SatelliteChartGenerator()
        
        output_path = f"charts/risk_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = generator.create_risk_comparison_chart(satellites_data, output_path)
        
        return send_file(chart_path, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/time-series', methods=['POST'])
def create_time_series():
    """Generate 24-hour prediction time series chart"""
    try:
        data = request.json
        satellite_name = data.get('satellite_name', 'Unknown')
        hourly_predictions = data.get('hourly_predictions', [])
        
        os.makedirs('charts', exist_ok=True)
        generator = SatelliteChartGenerator()
        
        output_path = f"charts/time_series_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = generator.create_time_series_chart(satellite_name, hourly_predictions, output_path)
        
        return send_file(chart_path, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/heatmap', methods=['POST'])
def create_heatmap():
    """Generate risk heatmap"""
    try:
        data = request.json
        satellites_data = data.get('satellites', [])
        kp_range = data.get('kp_range', list(range(0, 10)))
        
        os.makedirs('charts', exist_ok=True)
        generator = SatelliteChartGenerator()
        
        output_path = f"charts/heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = generator.create_heatmap_chart(satellites_data, kp_range, output_path)
        
        return send_file(chart_path, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/full-report', methods=['POST'])
def generate_full_report():
    """
    Generate comprehensive report with PDF and all charts
    
    POST /api/reports/full-report
    Body: {
        "satellite": {...},
        "space_weather": {...},
        "include_charts": true
    }
    
    Returns: ZIP file with PDF and charts
    """
    try:
        import zipfile
        from api.models.atmospheric_drag import calculate_drag_impact
        from api.models.radiation_dose import calculate_radiation_impact
        from api.models.signal_degradation import calculate_signal_impact
        
        data = request.json
        satellite = data.get('satellite', {})
        space_weather = data.get('space_weather', {})
        include_charts = data.get('include_charts', True)
        
        # Calculate impacts
        altitude = satellite.get('altitude', 400)
        kp = space_weather.get('kpIndex', 3)
        
        impacts = {
            'drag': calculate_drag_impact(altitude, kp, space_weather.get('f107', 120)),
            'radiation': calculate_radiation_impact(altitude, kp, space_weather.get('protonFlux', 100)),
            'signal': calculate_signal_impact(altitude, kp, satellite.get('inclination', 45))
        }
        
        # Calculate overall risk
        from api.models.risk_assessment import calculate_overall_risk, generate_recommendations
        impacts['overall'] = calculate_overall_risk(impacts['drag'], impacts['radiation'], impacts['signal'])
        impacts['recommendations'] = generate_recommendations(impacts)
        
        # ML prediction
        predictions = predict_satellite_anomaly(space_weather, satellite)
        
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f"reports/{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF
        pdf_path = generate_satellite_report(
            satellite.get('name', 'Unknown'),
            space_weather,
            impacts,
            predictions,
            f"{output_dir}/report.pdf"
        )
        
        files_to_zip = [pdf_path]
        
        # Generate charts if requested
        if include_charts:
            generator = SatelliteChartGenerator()
            
            # Time series (with forecast)
            hourly_pred = [predictions] * 24  # Simplified
            ts_path = generator.create_time_series_chart(
                satellite.get('name', 'Unknown'),
                hourly_pred,
                f"{output_dir}/time_series.png"
            )
            files_to_zip.append(ts_path)
        
        # Create ZIP
        zip_path = f"{output_dir}/complete_report.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in files_to_zip:
                zipf.write(file, os.path.basename(file))
        
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"report_{satellite.get('name', 'unknown')}_{timestamp}.zip"
        )
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500