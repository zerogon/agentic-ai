"""
Example: Report Generation

This example demonstrates how to use the new report helper
to generate PDF and HTML reports.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.report_helper import ReportHelper
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_sample_data():
    """Create sample data for demonstration"""
    # Sales data
    sales_df = pd.DataFrame({
        'Region': ['North', 'South', 'East', 'West', 'Central'],
        'Q1_Sales': [45000, 52000, 48000, 61000, 58000],
        'Q2_Sales': [48000, 55000, 51000, 64000, 61000],
        'Q3_Sales': [52000, 58000, 54000, 67000, 64000],
        'Q4_Sales': [55000, 61000, 57000, 70000, 67000]
    })

    # Customer data
    customer_df = pd.DataFrame({
        'Customer_Type': ['Enterprise', 'SMB', 'Startup', 'Government'],
        'Count': [45, 120, 85, 30],
        'Avg_Revenue': [125000, 35000, 15000, 95000]
    })

    return sales_df, customer_df


def create_sample_charts(sales_df, customer_df):
    """Create sample charts"""
    # Sales trend chart
    sales_trend = pd.DataFrame({
        'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
        'Total_Sales': [
            sales_df['Q1_Sales'].sum(),
            sales_df['Q2_Sales'].sum(),
            sales_df['Q3_Sales'].sum(),
            sales_df['Q4_Sales'].sum()
        ]
    })

    trend_chart = px.line(
        sales_trend,
        x='Quarter',
        y='Total_Sales',
        title='Quarterly Sales Trend',
        markers=True
    )
    trend_chart.update_layout(
        xaxis_title='Quarter',
        yaxis_title='Total Sales ($)',
        showlegend=False
    )

    # Regional sales chart
    regional_chart = px.bar(
        sales_df,
        x='Region',
        y='Q4_Sales',
        title='Q4 Sales by Region',
        color='Q4_Sales',
        color_continuous_scale='Blues'
    )
    regional_chart.update_layout(
        xaxis_title='Region',
        yaxis_title='Sales ($)',
        showlegend=False
    )

    # Customer distribution pie chart
    customer_chart = px.pie(
        customer_df,
        names='Customer_Type',
        values='Count',
        title='Customer Distribution by Type'
    )

    return trend_chart, regional_chart, customer_chart


def example_pdf_report():
    """Example 1: Generate PDF Report"""
    print("\n" + "="*60)
    print("Example 1: Generate PDF Report")
    print("="*60)

    # Create report helper
    report = ReportHelper()

    # Get sample data
    sales_df, customer_df = create_sample_data()
    trend_chart, regional_chart, customer_chart = create_sample_charts(sales_df, customer_df)

    # Build report
    print("\n📝 Building report sections...")

    # Executive Summary
    report.add_section(
        "Executive Summary",
        """This quarterly business report provides an overview of sales performance,
        regional trends, and customer distribution. Key highlights include strong
        growth in the West region and increased enterprise customer acquisition.""",
        "text"
    )

    # Sales Analysis
    report.add_section(
        "Sales Performance",
        "The following table shows quarterly sales performance across all regions:",
        "text"
    )
    report.add_dataframe("Regional Sales Data", sales_df)
    report.add_chart("Quarterly Trend", trend_chart)
    report.add_chart("Regional Breakdown", regional_chart)

    # Customer Analysis
    report.add_section(
        "Customer Analysis",
        "Our customer base continues to grow across all segments:",
        "text"
    )
    report.add_dataframe("Customer Metrics", customer_df)
    report.add_chart("Customer Distribution", customer_chart)

    # Key Findings
    report.add_section(
        "Key Findings",
        """• West region leads with $70,000 in Q4 sales
        • 13% quarter-over-quarter growth
        • SMB segment represents 42% of customer base
        • Enterprise customers drive highest revenue per customer""",
        "text"
    )

    # Generate PDF
    print("\n📄 Generating PDF...")
    try:
        pdf_bytes = report.generate_pdf(
            title="Q4 2024 Business Report",
            author="Analytics Team"
        )

        # Save to file
        output_path = "business_report.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)

        print(f"✅ PDF report generated: {output_path}")
        print(f"📊 File size: {len(pdf_bytes) / 1024:.1f} KB")

    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")


def example_html_report():
    """Example 2: Generate HTML Report"""
    print("\n" + "="*60)
    print("Example 2: Generate HTML Report")
    print("="*60)

    # Create report helper
    report = ReportHelper()

    # Get sample data
    sales_df, customer_df = create_sample_data()
    trend_chart, regional_chart, customer_chart = create_sample_charts(sales_df, customer_df)

    # Build report (same structure as PDF)
    print("\n📝 Building report sections...")

    report.add_section(
        "Executive Summary",
        """This quarterly business report provides an overview of sales performance,
        regional trends, and customer distribution. Key highlights include strong
        growth in the West region and increased enterprise customer acquisition.""",
        "text"
    )

    report.add_section(
        "Sales Performance",
        "The following table shows quarterly sales performance across all regions:",
        "text"
    )
    report.add_dataframe("Regional Sales Data", sales_df)
    report.add_chart("Quarterly Trend", trend_chart)
    report.add_chart("Regional Breakdown", regional_chart)

    report.add_section(
        "Customer Analysis",
        "Our customer base continues to grow across all segments:",
        "text"
    )
    report.add_dataframe("Customer Metrics", customer_df)
    report.add_chart("Customer Distribution", customer_chart)

    report.add_section(
        "Key Findings",
        """• West region leads with $70,000 in Q4 sales
        • 13% quarter-over-quarter growth
        • SMB segment represents 42% of customer base
        • Enterprise customers drive highest revenue per customer""",
        "text"
    )

    # Generate HTML
    print("\n🌐 Generating HTML...")
    try:
        html_content = report.generate_html(
            title="Q4 2024 Business Report",
            author="Analytics Team"
        )

        # Save to file
        output_path = "business_report.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML report generated: {output_path}")
        print(f"📊 File size: {len(html_content) / 1024:.1f} KB")
        print(f"💡 Open in browser to see interactive charts!")

    except Exception as e:
        print(f"❌ Error generating HTML: {str(e)}")


def example_custom_report():
    """Example 3: Custom Report with Different Chart Types"""
    print("\n" + "="*60)
    print("Example 3: Custom Report with Various Chart Types")
    print("="*60)

    # Create report helper
    report = ReportHelper()

    # Sample data for different chart types
    print("\n📝 Creating diverse visualizations...")

    # 1. Heatmap
    correlation_data = pd.DataFrame({
        'Marketing': [1.0, 0.85, 0.72, 0.65],
        'Sales': [0.85, 1.0, 0.78, 0.70],
        'Support': [0.72, 0.78, 1.0, 0.82],
        'Product': [0.65, 0.70, 0.82, 1.0]
    }, index=['Marketing', 'Sales', 'Support', 'Product'])

    heatmap = go.Figure(data=go.Heatmap(
        z=correlation_data.values,
        x=correlation_data.columns,
        y=correlation_data.index,
        colorscale='Blues'
    ))
    heatmap.update_layout(title='Department Correlation Matrix')

    # 2. Scatter plot
    scatter_data = pd.DataFrame({
        'Ad_Spend': [5000, 7500, 6000, 8500, 9000, 6500, 7000],
        'Revenue': [45000, 62000, 51000, 73000, 78000, 55000, 59000]
    })

    scatter = px.scatter(
        scatter_data,
        x='Ad_Spend',
        y='Revenue',
        title='Marketing Spend vs Revenue',
        trendline='ols'
    )

    # 3. Stacked bar chart
    stacked_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
        'Product_A': [12000, 13500, 14000, 15200],
        'Product_B': [8000, 8500, 9200, 9800],
        'Product_C': [6000, 6200, 6800, 7100]
    })

    stacked = go.Figure(data=[
        go.Bar(name='Product A', x=stacked_data['Month'], y=stacked_data['Product_A']),
        go.Bar(name='Product B', x=stacked_data['Month'], y=stacked_data['Product_B']),
        go.Bar(name='Product C', x=stacked_data['Month'], y=stacked_data['Product_C'])
    ])
    stacked.update_layout(barmode='stack', title='Product Revenue by Month')

    # Build report
    report.add_section(
        "Advanced Analytics Report",
        "This report showcases various visualization techniques for different data types.",
        "text"
    )

    report.add_section(
        "Correlation Analysis",
        "Department performance correlation matrix:",
        "text"
    )
    report.add_chart("Heatmap", heatmap)

    report.add_section(
        "Marketing ROI",
        "Relationship between advertising spend and revenue:",
        "text"
    )
    report.add_dataframe("Marketing Data", scatter_data)
    report.add_chart("Scatter Plot", scatter)

    report.add_section(
        "Product Performance",
        "Monthly revenue breakdown by product line:",
        "text"
    )
    report.add_chart("Stacked Bar Chart", stacked)

    # Generate both formats
    print("\n📄 Generating PDF...")
    try:
        pdf_bytes = report.generate_pdf(
            title="Advanced Analytics Report",
            author="Data Science Team"
        )
        with open("advanced_report.pdf", 'wb') as f:
            f.write(pdf_bytes)
        print("✅ PDF: advanced_report.pdf")
    except Exception as e:
        print(f"❌ PDF Error: {str(e)}")

    print("\n🌐 Generating HTML...")
    try:
        html_content = report.generate_html(
            title="Advanced Analytics Report",
            author="Data Science Team"
        )
        with open("advanced_report.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ HTML: advanced_report.html")
    except Exception as e:
        print(f"❌ HTML Error: {str(e)}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Report Generation Examples")
    print("="*60)

    try:
        # Run examples
        example_pdf_report()
        example_html_report()
        example_custom_report()

        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        print("\n📂 Generated files:")
        print("  • business_report.pdf")
        print("  • business_report.html")
        print("  • advanced_report.pdf")
        print("  • advanced_report.html")
        print("\n💡 Open the HTML files in a browser to see interactive charts!")

    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Install dependencies: pip install reportlab jinja2 kaleido")
        print("  2. Make sure plotly is installed: pip install plotly")
        print("  3. Check write permissions in current directory")


if __name__ == "__main__":
    main()
