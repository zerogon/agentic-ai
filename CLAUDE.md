# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Databricks Apps** application that provides a chat-based interface for interacting with data using natural language queries. The app integrates multiple AI backends (Genie, Databricks LLM, AWS Bedrock) and generates professional reports (PDF/HTML).

**Key constraint**: Databricks Apps requires a single-process architecture. There is no separate backend/frontend - everything runs in one Streamlit process.

## Architecture

### Core Design Pattern

```
app.py (Streamlit UI + Business Logic)
    ↓
Helper Modules (utils/)
    ↓
External Services (Databricks SDK, AWS Bedrock, Plotly)
```

**Why this matters**:
- Don't try to separate into Flask backend + Streamlit frontend
- All API calls happen directly from Streamlit via SDK
- Authentication is handled via Databricks Apps headers (`st.context.headers`)
- WorkspaceClient auto-authenticates when deployed to Databricks Apps

### Helper Module Architecture

All business logic is in `utils/` as standalone helper classes:

1. **`genie_helper.py`**: Databricks Genie API (NL2SQL)
   - `start_conversation()` - Start new Genie conversation
   - `continue_conversation()` - Multi-turn conversations
   - `process_response()` - Parse Genie responses into messages with data/code

2. **`llm_helper.py`**: Multi-provider LLM interface
   - Supports **two providers**: `databricks` and `bedrock`
   - Single unified interface: `chat_completion()` works for both
   - Provider switching via `provider` parameter in constructor
   - **Important**: For Databricks provider, pass `WorkspaceClient`; for Bedrock, pass AWS credentials

3. **`bedrock_helper.py`**: AWS Bedrock Claude models
   - Direct boto3 integration
   - Supports Claude 3 family (Opus, Sonnet, Haiku) and Claude 2.x
   - `analyze_data()` and `generate_sql_explanation()` for specialized tasks

4. **`data_helper.py`**: Visualization and data processing
   - `create_chart()` - Generate Plotly charts from DataFrames
   - `auto_detect_chart_type()` - Smart chart type selection
   - `format_sql_code()` - SQL formatting for display

5. **`report_helper.py`**: Report generation
   - `generate_pdf()` - ReportLab-based PDF reports
   - `generate_html()` - Jinja2-based HTML reports
   - Accumulate sections with `add_section()`, `add_dataframe()`, `add_chart()`
   - Call `clear()` before building new report

### State Management

**Session state keys** (in `st.session_state`):
- `messages` - Chat history (list of dicts with role/content/chart_data/table_data)
- `conversation_id` - Genie conversation ID for multi-turn queries

## Development Commands

### Local Development
```bash
# Setup environment
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=your-token

# Install dependencies
pip install -r requirements.txt

# Run app locally
streamlit run app.py
# App starts at http://localhost:8501
```

### Databricks Apps Deployment
```bash
# Authenticate
databricks auth login --host <workspace-url>

# Deploy
databricks apps deploy <app-name> --source-code-path .
```

### AWS Bedrock Setup (Optional)
```bash
# Configure AWS credentials
aws configure
# OR
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

## Working with AI Modes

The app supports **4 AI modes** (selected via sidebar):

### 1. Genie API
- Best for: Data queries (NL2SQL)
- Requires: `GENIE_SPACE_ID` in secrets or sidebar input
- Flow: User query → Genie generates SQL → Executes → Returns DataFrame
- Maintains conversation context automatically

## Report Generation

### Building Reports
```python
report = ReportHelper()

# Add content
report.add_section("Title", "Text content", "text")
report.add_dataframe("Data", df)
report.add_chart("Visualization", plotly_fig)

# Generate
pdf_bytes = report.generate_pdf(title="Report", author="User")
html_str = report.generate_html(title="Report", author="User")

# Clear for next report
report.clear()
```

**In app.py**: Report is built from `st.session_state.messages` by iterating over assistant messages and adding their content/tables/charts.

## Adding New Features

### Adding a New AI Provider
1. Create `utils/newprovider_helper.py` with `chat_completion()` method
2. Modify `llm_helper.py` to add provider option:
   ```python
   if self.provider == "newprovider":
       return self.newprovider.chat_completion(...)
   ```
3. Add UI config in `app.py` sidebar
4. Add mode handling in chat input section

### Adding a New Chart Type
1. Modify `data_helper.py`:
   ```python
   elif chart_type == "newtype":
       fig = px.newtype(df, ...)
   ```
2. Add to chart type selector in `app.py` sidebar

### Adding a New Report Format
1. Add method to `report_helper.py`:
   ```python
   def generate_markdown(self, ...):
       # Implementation
   ```
2. Add export button in `app.py` sidebar

## Important Constraints

1. **Databricks Apps Limitations**:
   - Single process only (no separate API server)
   - Uses Streamlit's app model
   - Authentication via headers, not manual token passing

2. **Genie API**:
   - Requires valid Genie Space ID
   - Returns conversation objects with attachments
   - SQL results accessed via `statement_id` → `get_statement()`

3. **Report Generation**:
   - PDF requires kaleido for Plotly image export
   - HTML embeds Plotly.js (large file size)
   - Tables truncated to 50 rows in PDF

4. **AWS Bedrock**:
   - Model IDs must match exact format: `anthropic.claude-3-sonnet-20240229-v1:0`
   - Token usage in `response["usage"]` (input_tokens, output_tokens)
   - Requires IAM permission: `bedrock:InvokeModel`

## Configuration Files

### app.yaml (Databricks Apps Config)
```yaml
command: ['streamlit', 'run', 'app.py']
env:
  - name: 'STREAMLIT_SERVER_HEADLESS'
    value: 'true'
```
**Do not add Flask/Gunicorn** - Databricks Apps expects single Streamlit command.

### requirements.txt
Core dependencies:
- `streamlit>=1.28.0` - UI framework
- `databricks-sdk>=0.23.0` - Databricks API client
- `plotly>=5.17.0` - Visualizations
- `reportlab>=4.0.0` - PDF generation
- `jinja2>=3.1.0` - HTML templating
- `boto3>=1.34.0` - AWS Bedrock (optional)

## Testing

### Manual Testing Checklist
```bash
# 1. Test Genie mode
streamlit run app.py
# Select "Genie API", enter Space ID, ask data question

# 2. Test Bedrock mode
export AWS_ACCESS_KEY_ID=...
streamlit run app.py
# Select "LLM Endpoint (Bedrock)", choose model, chat

# 3. Test report export
# Have conversation → Click "Export PDF" → Verify download

# 4. Test visualization
# Get data from Genie → Check chart appears → Try different chart types
```

### Example Scripts
```bash
# Run report generation examples
python examples/report_example.py
# Generates: business_report.pdf, business_report.html

# Run Bedrock examples (requires AWS setup)
python examples/bedrock_example.py
```

## Common Issues

### Import Errors
**Problem**: `ModuleNotFoundError: utils.xxx`
**Solution**: Always run from project root: `streamlit run app.py` (not `python app.py`)

### Genie Conversation Errors
**Problem**: Genie returns no data or errors
**Solution**: Check that:
- Space ID is valid and accessible
- User has permissions to Genie Space
- Query matches available data schemas

### Bedrock Authentication
**Problem**: `NoCredentialsError` or `AccessDeniedException`
**Solution**:
- Verify AWS credentials: `aws sts get-caller-identity`
- Check IAM policy has `bedrock:InvokeModel`
- Confirm model available in region (Claude 3 in us-east-1, us-west-2, eu-west-1)

### PDF Generation Fails
**Problem**: Image export errors or kaleido issues
**Solution**: `pip install kaleido==0.2.1` (specific version required)

## File References

When discussing code locations, use these patterns:
- `app.py:50` - Sidebar configuration starts here
- `utils/genie_helper.py:101` - Response processing logic
- `utils/llm_helper.py:13` - Multi-provider constructor
- `utils/report_helper.py:85` - PDF generation method

## Documentation

- **User Guide**: `PHASE2_FEATURES.md` - Complete feature documentation
- **Examples**: `examples/` - Standalone examples for report generation and Bedrock
- **README**: Overview and deployment instructions

## Key Learnings for New Features

1. **Always use helpers**: Don't put business logic directly in `app.py`
2. **Preserve message structure**: Include all optional fields (code, chart_data, table_data)
3. **Handle both success and error cases**: Return `{"success": bool, "content": str, "error": str}`
4. **Test locally before deploying**: Use mock mode or local credentials
5. **Remember single-process constraint**: No background workers, no separate API servers
