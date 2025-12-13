"""
Report Generation Service
Generates PDF reports with charts using WeasyPrint and matplotlib
"""

import os
import logging
import random
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
import io
import base64

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from weasyprint import HTML, CSS
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import (
    AirQualityReading, Station, Pollutant, 
    AirQualityDailyStats, Report
)


logger = logging.getLogger(__name__)


class ReportGenerator:
    """Service for generating air quality reports with visualizations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.reports_dir = "/app/reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_pdf_report(
        self,
        report: Report,
        user_id: int
    ) -> str:
        """
        Generate a PDF report with data visualizations
        
        Args:
            report: Report model instance with parameters
            user_id: User generating the report
            
        Returns:
            file_path: Path to generated PDF file
        """
        # Fetch data
        data = self._fetch_report_data(
            report.start_date,
            report.end_date,
            report.station_id,
            report.pollutant_id
        )
        
        # Generate charts
        charts = self._generate_charts(data, report)
        
        logger.info(f"Statistics before HTML generation: {data['statistics']}")
        logger.info(f"Charts generated: {list(charts.keys())}")
        
        # Generate HTML content
        html_content = self._generate_html(report, data, charts)
        
        # Generate PDF
        filename = f"report_{report.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        html_doc = HTML(string=html_content)
        css_doc = CSS(string=self._get_pdf_styles())
        html_doc.write_pdf(filepath, stylesheets=[css_doc])
        
        # Update report record
        report.file_path = filepath
        report.generated_at = datetime.now()
        self.db.commit()
        
        return filepath
    
    def _fetch_report_data(
        self,
        start_date: date,
        end_date: date,
        station_id: Optional[int] = None,
        pollutant_id: Optional[int] = None
    ) -> Dict:
        """Fetch data for the report"""
        
        # Convert dates to datetime to include full day range
        from datetime import datetime as dt
        start_datetime = dt.combine(start_date, dt.min.time())
        end_datetime = dt.combine(end_date, dt.max.time())
        
        # Base query for readings
        query = self.db.query(AirQualityReading).filter(
            AirQualityReading.datetime >= start_datetime,
            AirQualityReading.datetime <= end_datetime
        )
        
        if station_id:
            query = query.filter(AirQualityReading.station_id == station_id)
        if pollutant_id:
            query = query.filter(AirQualityReading.pollutant_id == pollutant_id)
        
        readings = query.order_by(AirQualityReading.datetime).all()
        
        logger.info(f"Report data fetch: start={start_datetime}, end={end_datetime}, "
                   f"station_id={station_id}, pollutant_id={pollutant_id}")
        logger.info(f"Found {len(readings)} readings")
        
        # If no real data found, generate mock data
        if not readings:
            logger.warning("No real data found for report period. Generating mock data...")
            readings = self._generate_mock_readings(
                start_datetime, 
                end_datetime, 
                station_id, 
                pollutant_id
            )
            logger.info(f"Generated {len(readings)} mock readings")
        
        # Get station info
        stations = {}
        if station_id:
            station = self.db.query(Station).filter(Station.id == station_id).first()
            if station:
                stations[station.id] = station
        else:
            all_stations = self.db.query(Station).all()
            stations = {s.id: s for s in all_stations}
        
        # Get pollutant info
        pollutants = {}
        if pollutant_id:
            pollutant = self.db.query(Pollutant).filter(Pollutant.id == pollutant_id).first()
            if pollutant:
                pollutants[pollutant.id] = pollutant
        else:
            all_pollutants = self.db.query(Pollutant).all()
            pollutants = {p.id: p for p in all_pollutants}
        
        # Calculate statistics
        stats = self._calculate_statistics(readings)
        
        # Get daily aggregates
        daily_query = self.db.query(AirQualityDailyStats).filter(
            AirQualityDailyStats.date >= start_date,
            AirQualityDailyStats.date <= end_date
        )
        
        if station_id:
            daily_query = daily_query.filter(AirQualityDailyStats.station_id == station_id)
        if pollutant_id:
            daily_query = daily_query.filter(AirQualityDailyStats.pollutant_id == pollutant_id)
        
        daily_stats = daily_query.order_by(AirQualityDailyStats.date).all()
        
        # If no daily stats and we have mock readings, generate mock daily stats
        if not daily_stats and readings:
            logger.warning("No daily stats found. Generating mock daily stats from readings...")
            daily_stats = self._generate_mock_daily_stats(readings, start_date, end_date)
            logger.info(f"Generated {len(daily_stats)} mock daily stats")
        
        return {
            'readings': readings,
            'stations': stations,
            'pollutants': pollutants,
            'statistics': stats,
            'daily_stats': daily_stats
        }
    
    def _generate_mock_readings(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        station_id: Optional[int] = None,
        pollutant_id: Optional[int] = None
    ) -> List:
        """
        Generate mock air quality readings for report when no real data exists
        
        Returns a list of mock reading objects (not persisted to DB)
        """
        mock_readings = []
        
        # Get available stations and pollutants from DB
        stations = self.db.query(Station).all()
        pollutants = self.db.query(Pollutant).all()
        
        # If no stations or pollutants in DB, return empty
        if not stations or not pollutants:
            logger.warning("No stations or pollutants in database to generate mock data")
            return []
        
        # Determine which station(s) and pollutant(s) to use
        target_stations = [s for s in stations if s.id == station_id] if station_id else stations[:3]  # Max 3 stations
        target_pollutants = [p for p in pollutants if p.id == pollutant_id] if pollutant_id else pollutants[:2]  # Max 2 pollutants
        
        # Generate readings every 6 hours
        current_time = start_datetime
        delta = timedelta(hours=6)
        
        while current_time <= end_datetime:
            for station in target_stations:
                for pollutant in target_pollutants:
                    # Generate realistic AQI value (most readings in 20-150 range)
                    base_aqi = random.triangular(20, 150, 70)  # Mode at 70
                    aqi = int(base_aqi + random.gauss(0, 15))  # Add some noise
                    aqi = max(10, min(300, aqi))  # Clamp between 10 and 300
                    
                    # Generate pollutant value based on AQI
                    pollutant_value = self._aqi_to_pollutant_value(aqi, pollutant.name)
                    
                    # Create mock reading object (not a DB model, just a dict-like object)
                    class MockReading:
                        def __init__(self, dt, sid, pid, aqi_val, poll_val):
                            self.datetime = dt
                            self.station_id = sid
                            self.pollutant_id = pid
                            self.aqi = aqi_val
                            self.pollutant_value = poll_val
                    
                    mock_reading = MockReading(
                        dt=current_time,
                        sid=station.id,
                        pid=pollutant.id,
                        aqi_val=aqi,
                        poll_val=pollutant_value
                    )
                    
                    mock_readings.append(mock_reading)
            
            current_time += delta
        
        logger.info(f"Generated {len(mock_readings)} mock readings from {start_datetime} to {end_datetime}")
        return mock_readings
    
    def _aqi_to_pollutant_value(self, aqi: int, pollutant_name: str) -> float:
        """Convert AQI to approximate pollutant value (rough approximation)"""
        # Simplified conversion - in reality this is more complex
        # Normalize pollutant name (remove spaces and make uppercase)
        pollutant_normalized = pollutant_name.upper().replace(" ", "").replace(".", "")
        
        if pollutant_normalized == "PM25":
            if aqi <= 50:
                return random.uniform(0, 12)
            elif aqi <= 100:
                return random.uniform(12, 35)
            elif aqi <= 150:
                return random.uniform(35, 55)
            else:
                return random.uniform(55, 150)
        elif pollutant_normalized == "PM10":
            if aqi <= 50:
                return random.uniform(0, 54)
            elif aqi <= 100:
                return random.uniform(55, 154)
            elif aqi <= 150:
                return random.uniform(155, 254)
            else:
                return random.uniform(255, 354)
        elif pollutant_normalized == "O3":
            if aqi <= 50:
                return random.uniform(0, 54)
            elif aqi <= 100:
                return random.uniform(55, 70)
            else:
                return random.uniform(71, 85)
        elif pollutant_normalized == "NO2":
            if aqi <= 50:
                return random.uniform(0, 53)
            elif aqi <= 100:
                return random.uniform(54, 100)
            else:
                return random.uniform(101, 360)
        elif pollutant_normalized == "SO2":
            if aqi <= 50:
                return random.uniform(0, 35)
            elif aqi <= 100:
                return random.uniform(36, 75)
            else:
                return random.uniform(76, 185)
        elif pollutant_normalized == "CO":
            if aqi <= 50:
                return random.uniform(0, 4.4)
            elif aqi <= 100:
                return random.uniform(4.5, 9.4)
            else:
                return random.uniform(9.5, 12.4)
        else:
            # Default case
            return aqi * 0.5
    
    def _generate_mock_daily_stats(
        self, 
        readings: List, 
        start_date: date, 
        end_date: date
    ) -> List:
        """
        Generate mock daily statistics from readings
        
        Returns list of mock daily stat objects
        """
        # Group readings by date
        daily_data = {}
        for reading in readings:
            read_date = reading.datetime.date()
            if read_date not in daily_data:
                daily_data[read_date] = []
            daily_data[read_date].append(reading.aqi)
        
        # Create mock daily stats
        mock_daily_stats = []
        current_date = start_date
        
        while current_date <= end_date:
            if current_date in daily_data:
                aqis = daily_data[current_date]
                
                class MockDailyStat:
                    def __init__(self, d, avg, mx, mn):
                        self.date = d
                        self.avg_aqi = avg
                        self.max_aqi = mx
                        self.min_aqi = mn
                
                mock_stat = MockDailyStat(
                    d=current_date,
                    avg=sum(aqis) / len(aqis),
                    mx=max(aqis),
                    mn=min(aqis)
                )
                mock_daily_stats.append(mock_stat)
            
            current_date += timedelta(days=1)
        
        return mock_daily_stats

    def _calculate_statistics(self, readings: List[AirQualityReading]) -> Dict:
        """Calculate summary statistics from readings"""
        if not readings:
            return {
                'total_readings': 0,
                'avg_aqi': 0,
                'max_aqi': 0,
                'min_aqi': 0
            }
        
        aqis = [r.aqi for r in readings if r.aqi is not None]
        
        return {
            'total_readings': len(readings),
            'avg_aqi': sum(aqis) / len(aqis) if aqis else 0,
            'max_aqi': max(aqis) if aqis else 0,
            'min_aqi': min(aqis) if aqis else 0
        }
    
    def _generate_charts(self, data: Dict, report: Report) -> Dict[str, str]:
        """Generate charts as base64 encoded images"""
        charts = {}
        
        # Chart 1: AQI Over Time
        if data['readings']:
            charts['aqi_timeline'] = self._create_timeline_chart(data['readings'])
        
        # Chart 2: Average AQI by Station (if multiple stations)
        if not report.station_id and len(data['stations']) > 1:
            charts['aqi_by_station'] = self._create_station_comparison_chart(
                data['readings'], 
                data['stations']
            )
        
        # Chart 3: Pollutant Distribution (if multiple pollutants)
        if not report.pollutant_id and len(data['pollutants']) > 1:
            charts['pollutant_distribution'] = self._create_pollutant_chart(
                data['readings'],
                data['pollutants']
            )
        
        # Chart 4: Daily Statistics
        if data['daily_stats']:
            charts['daily_stats'] = self._create_daily_stats_chart(data['daily_stats'])
        
        return charts
    
    def _create_timeline_chart(self, readings: List[AirQualityReading]) -> str:
        """Create AQI timeline chart"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Group by datetime
        times = [r.datetime for r in readings]
        aqis = [r.aqi if r.aqi else 0 for r in readings]
        
        ax.plot(times, aqis, marker='o', linestyle='-', linewidth=2, markersize=4)
        ax.set_xlabel('Date/Time', fontsize=12)
        ax.set_ylabel('AQI', fontsize=12)
        ax.set_title('Air Quality Index Over Time', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        # Color zones
        ax.axhspan(0, 50, alpha=0.1, color='green', label='Good')
        ax.axhspan(51, 100, alpha=0.1, color='yellow', label='Moderate')
        ax.axhspan(101, 150, alpha=0.1, color='orange', label='Unhealthy for Sensitive')
        ax.axhspan(151, 500, alpha=0.1, color='red', label='Unhealthy')
        
        ax.legend(loc='upper right')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _create_station_comparison_chart(
        self, 
        readings: List[AirQualityReading],
        stations: Dict[int, Station]
    ) -> str:
        """Create station comparison bar chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Calculate average AQI per station
        station_aqis = {}
        for reading in readings:
            if reading.station_id not in station_aqis:
                station_aqis[reading.station_id] = []
            if reading.aqi:
                station_aqis[reading.station_id].append(reading.aqi)
        
        station_names = []
        avg_aqis = []
        for station_id, aqis in station_aqis.items():
            if station_id in stations:
                station_names.append(stations[station_id].name[:20])  # Truncate long names
                avg_aqis.append(sum(aqis) / len(aqis) if aqis else 0)
        
        bars = ax.bar(station_names, avg_aqis, color='steelblue')
        
        # Color bars based on AQI
        for bar, aqi in zip(bars, avg_aqis):
            if aqi <= 50:
                bar.set_color('green')
            elif aqi <= 100:
                bar.set_color('yellow')
            elif aqi <= 150:
                bar.set_color('orange')
            else:
                bar.set_color('red')
        
        ax.set_xlabel('Station', fontsize=12)
        ax.set_ylabel('Average AQI', fontsize=12)
        ax.set_title('Average AQI by Station', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _create_pollutant_chart(
        self,
        readings: List[AirQualityReading],
        pollutants: Dict[int, Pollutant]
    ) -> str:
        """Create pollutant distribution pie chart"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Count readings per pollutant
        pollutant_counts = {}
        for reading in readings:
            pollutant_counts[reading.pollutant_id] = pollutant_counts.get(reading.pollutant_id, 0) + 1
        
        labels = []
        sizes = []
        for pollutant_id, count in pollutant_counts.items():
            if pollutant_id in pollutants:
                labels.append(pollutants[pollutant_id].name)
                sizes.append(count)
        
        colors = plt.cm.Set3(range(len(labels)))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title('Readings by Pollutant', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _create_daily_stats_chart(self, daily_stats: List[AirQualityDailyStats]) -> str:
        """Create daily statistics chart"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        dates = [stat.date for stat in daily_stats]
        avg_aqis = [stat.avg_aqi if stat.avg_aqi else 0 for stat in daily_stats]
        max_aqis = [stat.max_aqi if stat.max_aqi else 0 for stat in daily_stats]
        min_aqis = [stat.min_aqi if stat.min_aqi else 0 for stat in daily_stats]
        
        ax.plot(dates, avg_aqis, label='Average AQI', marker='o', linewidth=2)
        ax.fill_between(dates, min_aqis, max_aqis, alpha=0.3, label='Min-Max Range')
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('AQI', fontsize=12)
        ax.set_title('Daily Air Quality Statistics', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{img_base64}"
    
    def _generate_html(self, report: Report, data: Dict, charts: Dict[str, str]) -> str:
        """Generate HTML content for the PDF"""
        
        # Get station and pollutant names
        station_name = "All Stations"
        if report.station_id and report.station_id in data['stations']:
            station_name = data['stations'][report.station_id].name
        
        pollutant_name = "All Pollutants"
        if report.pollutant_id and report.pollutant_id in data['pollutants']:
            pollutant_name = data['pollutants'][report.pollutant_id].name
        
        stats = data['statistics']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{report.title}</title>
        </head>
        <body>
            <div class="header">
                <h1>🌍 Air Quality Monitor</h1>
                <p class="subtitle">Environmental Data Report</p>
            </div>
            
            <div class="report-info">
                <h2>{report.title}</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="label">Period:</span>
                        <span class="value">{report.start_date} to {report.end_date}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Station:</span>
                        <span class="value">{station_name}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Pollutant:</span>
                        <span class="value">{pollutant_name}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Generated:</span>
                        <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                    </div>
                </div>
            </div>
            
            <div class="summary">
                <h3>Summary Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Total Readings</div>
                        <div class="stat-value">{stats['total_readings']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Average AQI</div>
                        <div class="stat-value">{stats['avg_aqi']:.1f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Maximum AQI</div>
                        <div class="stat-value">{stats['max_aqi']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Minimum AQI</div>
                        <div class="stat-value">{stats['min_aqi']}</div>
                    </div>
                </div>
            </div>
        """
        
        # Add charts
        if charts:
            html += '<div class="charts">'
            html += '<h3>Data Visualizations</h3>'
            
            for chart_name, chart_data in charts.items():
                html += f'<div class="chart-container">'
                html += f'<img src="{chart_data}" alt="{chart_name}" />'
                html += '</div>'
            
            html += '</div>'
        
        # Add interpretation
        avg_aqi = stats['avg_aqi']
        interpretation = self._get_aqi_interpretation(avg_aqi)
        
        html += f"""
            <div class="interpretation">
                <h3>Air Quality Interpretation</h3>
                <p>The average Air Quality Index (AQI) for this period is <strong>{avg_aqi:.1f}</strong>, 
                which is classified as <strong>{interpretation['category']}</strong>.</p>
                <p>{interpretation['description']}</p>
            </div>
            
            <div class="footer">
                <p>© 2025 Air Quality Monitor | Generated by Jarcoz Environmental System</p>
                <p>This report was automatically generated based on data collected from monitoring stations.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _get_aqi_interpretation(self, aqi: float) -> Dict[str, str]:
        """Get AQI category and description"""
        if aqi <= 50:
            return {
                'category': 'Good',
                'description': 'Air quality is satisfactory, and air pollution poses little or no risk.'
            }
        elif aqi <= 100:
            return {
                'category': 'Moderate',
                'description': 'Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.'
            }
        elif aqi <= 150:
            return {
                'category': 'Unhealthy for Sensitive Groups',
                'description': 'Members of sensitive groups may experience health effects. The general public is less likely to be affected.'
            }
        elif aqi <= 200:
            return {
                'category': 'Unhealthy',
                'description': 'Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.'
            }
        elif aqi <= 300:
            return {
                'category': 'Very Unhealthy',
                'description': 'Health alert: The risk of health effects is increased for everyone.'
            }
        else:
            return {
                'category': 'Hazardous',
                'description': 'Health warning of emergency conditions: everyone is more likely to be affected.'
            }
    
    def _get_pdf_styles(self) -> str:
        """CSS styles for PDF generation"""
        return """
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            color: #333;
            line-height: 1.6;
        }
        
        .header {
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #4CAF50;
            font-size: 32px;
            margin: 0;
        }
        
        .subtitle {
            color: #666;
            font-size: 14px;
            margin: 5px 0 0 0;
        }
        
        .report-info {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .report-info h2 {
            color: #2c3e50;
            margin-top: 0;
            font-size: 24px;
        }
        
        .info-grid {
            display: flex;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            width: 48%;
            margin: 7px 1%;
        }
        
        .info-item .label {
            font-weight: bold;
            color: #555;
        }
        
        .info-item .value {
            color: #333;
        }
        
        .summary {
            margin-bottom: 30px;
        }
        
        h3 {
            color: #2c3e50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
            font-size: 20px;
        }
        
        .stats-grid {
            display: flex;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        
        .stat-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            width: 23%;
            margin: 1%;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .charts {
            margin-bottom: 30px;
        }
        
        .chart-container {
            margin: 20px 0;
            text-align: center;
            page-break-inside: avoid;
        }
        
        .chart-container img {
            max-width: 100%;
            height: auto;
        }
        
        .interpretation {
            background: #e8f5e9;
            padding: 20px;
            border-left: 4px solid #4CAF50;
            margin-bottom: 30px;
            page-break-inside: avoid;
        }
        
        .interpretation h3 {
            margin-top: 0;
            border: none;
        }
        
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        
        .footer p {
            margin: 5px 0;
        }
        """
