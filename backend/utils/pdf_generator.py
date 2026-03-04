"""
PDF Report Generator for Space Weather Impact Analysis
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import io

class SpaceWeatherReport:
    def __init__(self, output_path='report.pdf'):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#16213e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=10
        )
    
    def add_title_page(self, satellite_name, date_range):
        """Add report title page"""
        # Title
        title = Paragraph(
            "Space Weather Impact Analysis Report",
            self.title_style
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Satellite name
        sat_name = Paragraph(
            f"<b>Satellite:</b> {satellite_name}",
            self.heading_style
        )
        self.story.append(sat_name)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Date range
        date_text = Paragraph(
            f"<b>Analysis Period:</b> {date_range}",
            self.normal_style
        )
        self.story.append(date_text)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Generation date
        gen_date = Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
            self.normal_style
        )
        self.story.append(gen_date)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Disclaimer
        disclaimer = Paragraph(
            "<i>This report provides an assessment of space weather impacts on satellite "
            "operations based on current models and historical data. Predictions are "
            "probabilistic and should be used in conjunction with other data sources.</i>",
            self.normal_style
        )
        self.story.append(disclaimer)
        
        self.story.append(PageBreak())
    
    def add_executive_summary(self, summary_data):
        """Add executive summary section"""
        self.story.append(Paragraph("Executive Summary", self.heading_style))
        
        # Overall risk
        risk_color = self._get_risk_color(summary_data['overall_risk'])
        risk_text = f"""
        <para alignment="center" backColor="{risk_color}" textColor="white" fontSize="14" spaceAfter="10">
        <b>OVERALL RISK LEVEL: {summary_data['overall_risk']}</b>
        </para>
        """
        self.story.append(Paragraph(risk_text, self.normal_style))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Key findings
        self.story.append(Paragraph("<b>Key Findings:</b>", self.normal_style))
        for finding in summary_data.get('key_findings', []):
            bullet = Paragraph(f"• {finding}", self.normal_style)
            self.story.append(bullet)
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_space_weather_conditions(self, conditions):
        """Add current space weather conditions"""
        self.story.append(Paragraph("Current Space Weather Conditions", self.heading_style))
        
        # Create table
        data = [
            ['Parameter', 'Current Value', 'Status'],
            ['Kp Index', f"{conditions['kpIndex']}", self._get_kp_status(conditions['kpIndex'])],
            ['F10.7 Solar Flux', f"{conditions['f107']}", 'Normal' if conditions['f107'] < 150 else 'Elevated'],
            ['Solar Wind Speed', f"{conditions['solarWindSpeed']} km/s", 'Normal' if conditions['solarWindSpeed'] < 500 else 'High'],
            ['Proton Flux', f"{conditions['protonFlux']} pfu", 'Quiet' if conditions['protonFlux'] < 100 else 'Active']
        ]
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_impact_analysis(self, impacts):
        """Add detailed impact analysis"""
        self.story.append(Paragraph("Impact Analysis", self.heading_style))
        
        # Atmospheric Drag
        self.story.append(Paragraph("<b>1. Atmospheric Drag Impact</b>", self.normal_style))
        drag_data = [
            ['Metric', 'Value'],
            ['Orbit Decay Rate', f"{impacts['drag']['decayRate']:.2f} m/day"],
            ['Normal Decay Rate', f"{impacts['drag']['normalDecay']:.2f} m/day"],
            ['Increase', f"+{impacts['drag']['increase']:.0f}%"],
        ]
        
        if impacts['drag']['daysUntilReboost'] < 100:
            drag_data.append(['⚠️ Reboost Required', f"Within {impacts['drag']['daysUntilReboost']} days"])
        
        table = self._create_simple_table(drag_data)
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Radiation Impact
        self.story.append(Paragraph("<b>2. Radiation Effects</b>", self.normal_style))
        rad_data = [
            ['Metric', 'Value'],
            ['Radiation Dose', f"{impacts['radiation']['dose']:.1f} mrad/day"],
            ['SEU Probability', f"{impacts['radiation']['seuProbability']:.1f}%"],
            ['Safe Mode Risk', impacts['radiation']['safeModeRisk']]
        ]
        
        table = self._create_simple_table(rad_data)
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Communication Impact
        self.story.append(Paragraph("<b>3. Communication/Signal Quality</b>", self.normal_style))
        comm_data = [
            ['Metric', 'Value'],
            ['Signal Quality', impacts['signal']['quality']],
            ['Signal Loss', f"{impacts['signal']['signalLoss']:.1f} dB"],
            ['Degradation', f"{impacts['signal']['degradation']:.0f}%"]
        ]
        
        if impacts['signal']['blackoutDuration'] > 0:
            comm_data.append(['Expected Blackout', f"{impacts['signal']['blackoutDuration']} hours"])
        
        table = self._create_simple_table(comm_data)
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_recommendations(self, recommendations):
        """Add recommendations section"""
        self.story.append(Paragraph("Recommended Actions", self.heading_style))
        
        for i, rec in enumerate(recommendations, 1):
            bullet = Paragraph(f"{i}. {rec}", self.normal_style)
            self.story.append(bullet)
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_ml_predictions(self, predictions):
        """Add ML prediction section"""
        self.story.append(Paragraph("Machine Learning Predictions", self.heading_style))
        
        pred_text = f"""
        <b>Anomaly Probability:</b> {predictions['anomaly_probability']*100:.1f}%<br/>
        <b>Risk Level:</b> {predictions['risk_level']}<br/>
        <b>Confidence:</b> {predictions['confidence']*100:.1f}%<br/>
        <b>Model Agreement:</b> RF={predictions['rf_prediction']*100:.1f}%, GB={predictions['gb_prediction']*100:.1f}%
        """
        self.story.append(Paragraph(pred_text, self.normal_style))
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_chart(self, chart_path, caption=""):
        """Add a chart image to the report"""
        try:
            img = Image(chart_path, width=5.5*inch, height=3.5*inch)
            self.story.append(img)
            
            if caption:
                cap = Paragraph(f"<i>{caption}</i>", self.normal_style)
                self.story.append(cap)
            
            self.story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            print(f"Error adding chart: {e}")
    
    def _create_simple_table(self, data):
        """Create a simple 2-column table"""
        table = Table(data, colWidths=[2.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10)
        ]))
        return table
    
    def _get_risk_color(self, risk_level):
        """Get color for risk level"""
        colors_map = {
            'CRITICAL': '#ef4444',
            'HIGH': '#f97316',
            'MEDIUM': '#f59e0b',
            'LOW': '#10b981'
        }
        return colors_map.get(risk_level, '#6b7280')
    
    def _get_kp_status(self, kp):
        """Get Kp index status"""
        if kp >= 7:
            return 'SEVERE STORM'
        elif kp >= 5:
            return 'STORM'
        elif kp >= 4:
            return 'ACTIVE'
        else:
            return 'QUIET'
    
    def generate(self):
        """Generate the PDF report"""
        self.doc.build(self.story)
        print(f"✅ Report generated: {self.output_path}")
        return self.output_path

def generate_satellite_report(satellite_name, space_weather, impacts, predictions, output_path='report.pdf'):
    """
    Generate complete satellite impact report
    
    Args:
        satellite_name (str): Name of satellite
        space_weather (dict): Current conditions
        impacts (dict): Impact analysis results
        predictions (dict): ML predictions
        output_path (str): Output file path
    
    Returns:
        str: Path to generated PDF
    """
    report = SpaceWeatherReport(output_path)
    
    # Title page
    date_range = datetime.now().strftime('%Y-%m-%d')
    report.add_title_page(satellite_name, date_range)
    
    # Executive summary
    summary = {
        'overall_risk': impacts['overall']['level'],
        'key_findings': [
            f"Orbit decay rate: {impacts['drag']['decayRate']:.1f} m/day ({'+' if impacts['drag']['increase'] > 0 else ''}{impacts['drag']['increase']:.0f}% from normal)",
            f"Radiation dose: {impacts['radiation']['dose']:.1f} mrad/day with {impacts['radiation']['seuProbability']:.1f}% SEU probability",
            f"Signal quality: {impacts['signal']['quality']} with {impacts['signal']['degradation']:.0f}% degradation",
            f"ML-predicted anomaly probability: {predictions['anomaly_probability']*100:.1f}%"
        ]
    }
    report.add_executive_summary(summary)
    
    # Space weather conditions
    report.add_space_weather_conditions(space_weather)
    
    # Impact analysis
    report.add_impact_analysis(impacts)
    
    # ML predictions
    report.add_ml_predictions(predictions)
    
    # Recommendations
    report.add_recommendations(impacts['recommendations'])
    
    # Generate PDF
    return report.generate()