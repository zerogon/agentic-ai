# Examples Directory

This directory contains example scripts demonstrating the new Phase 1 & 2 features.

## 📁 Files

### 1. `report_example.py`
Demonstrates report generation capabilities (Phase 1)

**Features Shown:**
- PDF report generation with ReportLab
- HTML report generation with Jinja2
- Multiple chart types (line, bar, pie, heatmap, scatter)
- Data tables and text sections
- Professional formatting

**Run:**
```bash
python examples/report_example.py
```

**Output:**
- `business_report.pdf` - Professional PDF report
- `business_report.html` - Interactive HTML report
- `advanced_report.pdf` - Advanced analytics PDF
- `advanced_report.html` - Advanced analytics HTML

---

### 2. `bedrock_example.py`
Demonstrates AWS Bedrock integration (Phase 2)

**Features Shown:**
- Basic chat completion with Claude
- Data analysis using Claude
- SQL query explanation
- Model comparison (Opus, Sonnet, Haiku)
- Multi-turn conversations

**Prerequisites:**
```bash
# Configure AWS credentials
aws configure
# OR
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

**Run:**
```bash
python examples/bedrock_example.py
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r ../requirements.txt
```

### 2. Run Report Examples
```bash
cd /path/to/databricks
python examples/report_example.py
```

This will generate 4 sample reports in the current directory.

### 3. Run Bedrock Examples (Optional)
```bash
# Configure AWS first
aws configure

# Run examples
python examples/bedrock_example.py
```

---

## 📊 Example Outputs

### Report Example Output
```
=====================================================
Example 1: Generate PDF Report
=====================================================

📝 Building report sections...

📄 Generating PDF...
✅ PDF report generated: business_report.pdf
📊 File size: 127.3 KB

=====================================================
Example 2: Generate HTML Report
=====================================================

📝 Building report sections...

🌐 Generating HTML...
✅ HTML report generated: business_report.html
📊 File size: 245.6 KB
💡 Open in browser to see interactive charts!
```

### Bedrock Example Output
```
=====================================================
Example 1: Basic Chat Completion
=====================================================

✅ Response:
Here are the top 3 benefits of using cloud data warehouses:

1. Scalability and Elasticity: Cloud data warehouses can easily
   scale up or down based on your needs...

2. Cost Efficiency: You only pay for what you use...

3. Performance: Modern cloud data warehouses are optimized...

📊 Token Usage: {'input_tokens': 25, 'output_tokens': 150}
```

---

## 🎓 Learning Path

**Beginner:**
1. Start with `report_example.py` - Example 1
2. Understand PDF generation basics
3. Try modifying chart types

**Intermediate:**
1. Run `report_example.py` - Example 3
2. Explore different chart types
3. Customize report styling

**Advanced:**
1. Run `bedrock_example.py`
2. Implement multi-turn conversations
3. Integrate into your own applications

---

## 💡 Customization Ideas

### Modify Report Styling
```python
# In report_example.py, add custom styling
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor

custom_style = ParagraphStyle(
    'CustomStyle',
    textColor=HexColor('#2c3e50'),
    fontSize=14
)
```

### Add New Chart Types
```python
# Try different Plotly chart types
import plotly.graph_objects as go

# Waterfall chart
fig = go.Figure(go.Waterfall(...))

# Sankey diagram
fig = go.Figure(go.Sankey(...))

# 3D scatter
fig = go.Figure(go.Scatter3d(...))
```

### Use Different Claude Models
```python
# In bedrock_example.py, try different models
models = [
    "anthropic.claude-3-opus-20240229-v1:0",    # Best quality
    "anthropic.claude-3-sonnet-20240229-v1:0",  # Balanced
    "anthropic.claude-3-haiku-20240307-v1:0"    # Fastest
]

for model in models:
    result = bedrock.chat_completion(messages, model_id=model)
```

---

## 🐛 Troubleshooting

### Report Generation Issues

**Error: `ModuleNotFoundError: No module named 'reportlab'`**
```bash
pip install reportlab kaleido jinja2
```

**Error: `Image export failed`**
```bash
# Reinstall kaleido
pip uninstall kaleido
pip install kaleido==0.2.1
```

**Error: `Permission denied`**
```bash
# Check write permissions
ls -la
chmod 755 examples/
```

---

### Bedrock Issues

**Error: `NoCredentialsError`**
```bash
# Configure AWS credentials
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

**Error: `AccessDeniedException`**
```bash
# Check IAM permissions
# Required: bedrock:InvokeModel
```

**Error: `ModelNotFoundError`**
```bash
# Verify model availability in your region
# Claude 3 is available in:
# - us-east-1
# - us-west-2
# - eu-west-1
# - ap-northeast-1
```

---

## 📚 Additional Resources

- **Report Generation**: See `../PHASE2_FEATURES.md`
- **Bedrock Integration**: See `../PHASE2_FEATURES.md`
- **API Reference**: See `../PHASE2_FEATURES.md`
- **Streamlit Integration**: See `../app.py`

---

## 🎯 Next Steps

1. **Experiment** with these examples
2. **Modify** the code to suit your needs
3. **Integrate** into your own applications
4. **Create** your own custom reports
5. **Build** conversational AI features

---

**Happy coding!** 🚀
