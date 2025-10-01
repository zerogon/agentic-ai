"""
Report Generation Helper Functions
Provides utilities for generating PDF and HTML reports
"""

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict, Optional
import io
import base64
from pathlib import Path


class ReportHelper:
    """Helper class for generating various report formats"""

    def __init__(self):
        """Initialize Report Helper"""
        self.report_data = []

    def add_section(self, title: str, content: str, section_type: str = "text"):
        """
        Add a section to the report

        Args:
            title: Section title
            content: Section content
            section_type: Type of section (text, table, chart)
        """
        self.report_data.append({
            "title": title,
            "content": content,
            "type": section_type,
            "timestamp": datetime.now()
        })

    def add_dataframe(self, title: str, df: pd.DataFrame):
        """
        Add a DataFrame section to the report

        Args:
            title: Section title
            df: DataFrame to add
        """
        self.report_data.append({
            "title": title,
            "content": df,
            "type": "dataframe",
            "timestamp": datetime.now()
        })

    def add_chart(self, title: str, fig: go.Figure):
        """
        Add a chart section to the report

        Args:
            title: Section title
            fig: Plotly figure
        """
        self.report_data.append({
            "title": title,
            "content": fig,
            "type": "chart",
            "timestamp": datetime.now()
        })

    def generate_pdf(
        self,
        output_path: Optional[str] = None,
        title: str = "Data Analysis Report",
        author: str = "Databricks Data Chat"
    ) -> bytes:
        """
        Generate PDF report

        Args:
            output_path: Optional file path to save PDF
            title: Report title
            author: Report author

        Returns:
            PDF content as bytes
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")

        # Create PDF buffer
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Container for the 'Flowable' objects
        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Add title
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))

        # Add metadata
        metadata = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Author: {author}"
        elements.append(Paragraph(metadata, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Add sections
        for section in self.report_data:
            # Add section title
            elements.append(Paragraph(section["title"], heading_style))
            elements.append(Spacer(1, 6))

            if section["type"] == "text":
                # Add text content
                elements.append(Paragraph(section["content"], styles['Normal']))
                elements.append(Spacer(1, 12))

            elif section["type"] == "dataframe":
                # Add DataFrame as table
                df = section["content"]
                if not df.empty:
                    # Limit to first 50 rows for PDF
                    df_display = df.head(50)

                    # Convert DataFrame to list of lists
                    data = [df_display.columns.tolist()] + df_display.values.tolist()

                    # Create table
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))

                    elements.append(table)
                    elements.append(Spacer(1, 12))

            elif section["type"] == "chart":
                # Add chart as image
                fig = section["content"]

                # Convert Plotly figure to image
                img_bytes = fig.to_image(format="png", width=600, height=400)
                img_buffer = io.BytesIO(img_bytes)

                # Add image to PDF
                img = Image(img_buffer, width=5*inch, height=3.33*inch)
                elements.append(img)
                elements.append(Spacer(1, 12))

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        if output_path:
            with open(output_path, 'rb') as f:
                return f.read()
        else:
            buffer.seek(0)
            return buffer.getvalue()

    def generate_html(
        self,
        output_path: Optional[str] = None,
        title: str = "Data Analysis Report",
        author: str = "Databricks Data Chat"
    ) -> str:
        """
        Generate HTML report

        Args:
            output_path: Optional file path to save HTML
            title: Report title
            author: Report author

        Returns:
            HTML content as string
        """
        try:
            from jinja2 import Template
        except ImportError:
            raise ImportError("Jinja2 is required for HTML generation. Install with: pip install jinja2")

        # HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        .metadata {
            font-size: 0.9em;
            opacity: 0.9;
        }
        .section {
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            overflow-x: auto;
            display: block;
        }
        table thead {
            background: #667eea;
            color: white;
        }
        table th, table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        table tbody tr:hover {
            background: #f5f5f5;
        }
        .chart-container {
            margin-top: 20px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <div class="metadata">
            Generated: {{ timestamp }} | Author: {{ author }}
        </div>
    </div>

    {% for section in sections %}
    <div class="section">
        <h2>{{ section.title }}</h2>

        {% if section.type == 'text' %}
        <p>{{ section.content }}</p>
        {% endif %}

        {% if section.type == 'dataframe' %}
        <div style="overflow-x: auto;">
            {{ section.content | safe }}
        </div>
        {% endif %}

        {% if section.type == 'chart' %}
        <div class="chart-container" id="chart-{{ loop.index }}"></div>
        <script>
            {{ section.content | safe }}
        </script>
        {% endif %}
    </div>
    {% endfor %}

    <div class="footer">
        <p>Generated with Databricks Data Chat | Powered by Streamlit & AI</p>
    </div>
</body>
</html>
        """

        # Prepare sections for template
        sections = []
        for idx, section in enumerate(self.report_data):
            section_data = {
                "title": section["title"],
                "type": section["type"]
            }

            if section["type"] == "text":
                section_data["content"] = section["content"]

            elif section["type"] == "dataframe":
                df = section["content"]
                if not df.empty:
                    # Convert DataFrame to HTML table
                    section_data["content"] = df.to_html(
                        classes='dataframe',
                        border=0,
                        index=False
                    )
                else:
                    section_data["content"] = "<p>No data available</p>"

            elif section["type"] == "chart":
                fig = section["content"]
                # Convert Plotly figure to HTML div
                chart_html = fig.to_html(
                    include_plotlyjs=False,
                    div_id=f'chart-{idx+1}'
                )
                section_data["content"] = chart_html

            sections.append(section_data)

        # Render template
        template = Template(html_template)
        html_content = template.render(
            title=title,
            author=author,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            sections=sections
        )

        # Save to file if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        return html_content

    def clear(self):
        """Clear all report data"""
        self.report_data = []
