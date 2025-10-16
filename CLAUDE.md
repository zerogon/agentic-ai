# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Databricks Apps** application that provides a chat-based interface for interacting with data using natural language queries. The app integrates multiple AI backends (Genie, Databricks LLM) and generates professional reports (PDF/HTML).

**Key constraint**: Databricks Apps requires a single-process architecture. There is no separate backend/frontend - everything runs in one Streamlit process.

## Architecture

### Core Design Pattern

```
app.py (Streamlit UI + Business Logic)
    ↓
Helper Modules (utils/)
    ↓
External Services (Databricks SDK, Plotly)
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
   - Supports **two providers**: `databricks`
   - Single unified interface: `chat_completion()` works for both
   - Provider switching via `provider` parameter in constructor
   - **Important**: For Databricks provider, pass `WorkspaceClient`

3. **`data_helper.py`**: Visualization and data processing
   - `create_chart()` - Generate Plotly charts from DataFrames
   - `auto_detect_chart_type()` - Smart chart type selection
   - `format_sql_code()` - SQL formatting for display

4. **`report_helper.py`**: Report generation (PDF/HTML)
   - `generate_pdf()` - ReportLab-based PDF reports with Korean font support
   - `generate_html()` - Jinja2-based HTML reports
   - Accumulate sections with `add_section()`, `add_dataframe()`, `add_chart()`
   - Korean font handling: AppleSDGothicNeo.ttc → AppleGothic.ttf → Helvetica
   - Call `clear()` before building new report

5. **`map_helper.py`**: Geospatial visualization with automatic geometry detection
   - `auto_create_map()` - Automatically create appropriate map type
   - `create_point_map()` - Point markers with lat/lon data
   - `create_polygon_map()` - Polygon/choropleth maps from geometry data
   - `detect_geo_columns()` - Automatic column detection (lat/lon, geometry)
   - Priority: Geometry columns → Lat/Lon columns → Other map types

6. **`report_generator.py`**: Business report generation from chat sessions
   - `generate_business_report()` - Generate comprehensive business analysis report
   - `_extract_conversation_data()` - Extract queries, domains, data samples from messages
   - `_generate_llm_analysis()` - LLM-based business insights in Korean
   - `generate_report_preview()` - Preview statistics before generation

7. **`loading_helper.py`**: Loading video display during query processing
   - `display_loading_video()` - Display looping video during async operations
   - `remove_loading_video()` - Remove loading video after completion
   - Uses `static/test.mp4` for visual feedback during query processing

### State Management

**Session state keys** (in `st.session_state`):
- `messages` - Chat history (list of dicts with role/content/chart_data/table_data/code/domain)
- `conversation_id` - Genie conversation ID for multi-turn queries
- `chat_sessions` - List of all chat sessions with metadata
- `current_session_id` - Active session identifier
- `generated_report` - Cached business report data (PDF and HTML bytes)

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

## Working with AI Modes

The app uses a **simplified single-Genie architecture**:

### Genie API (REGION_GENIE Only)
- **Best for**: Regional and geographic data queries (NL2SQL)
- **Requires**: `REGION_GENIE` Space ID in secrets configuration
- **Simplified Flow**:
  1. User query → REGION_GENIE (direct, no routing)
  2. Generate SQL → Execute → Return DataFrame
  3. **Automatic geometry detection** → Create map if `geometry` column exists
  4. **Mandatory LLM analysis** → All responses get business insights
- **Maintains conversation context** automatically per domain
- **Map Generation**:
  - Geometry column detected → Folium polygon map
  - No geometry column → Standard charts/tables

## Report Generation

### 1. Manual Report Building (Low-level API)
```python
from utils.report_helper import ReportHelper

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

### 2. Business Report Generation (High-level API)
```python
from utils.report_generator import generate_business_report
from core.config import init_databricks_client

w = init_databricks_client()
messages = st.session_state.get("messages", [])

result = generate_business_report(
    w=w,
    messages=messages,
    title="Business Analysis Report",
    author="Databricks Data Chat"
)

if result["success"]:
    pdf_bytes = result["pdf"]
    html_string = result["html"]
else:
    error = result["error"]
```

**Features**:
- Extracts all queries, data, and charts from chat session
- Generates LLM-based business insights in Korean
- Creates structured report with:
  - Executive Summary (경영진 요약)
  - Analysis Details (분석 상세)
  - Key Insights (주요 인사이트)
  - Business Recommendations (비즈니스 권장사항)
  - Conclusion (결론)
- Supports Korean text in PDF with proper font handling
- Available in sidebar: "📊 Reports" section with preview and download buttons

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
   - Korean font support requires macOS system fonts (AppleSDGothicNeo.ttc or AppleGothic.ttf)
   - Report data persists in `st.session_state.generated_report` for download button stability


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


## Testing

### Manual Testing Checklist
```bash
# 1. Test Genie mode
streamlit run app.py
# Select "Genie API", enter Space ID, ask data question


### Example Scripts
```bash
# Run report generation examples
python examples/report_example.py
# Generates: business_report.pdf, business_report.html


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

### PDF Generation Fails
**Problem**: Image export errors or kaleido issues
**Solution**: `pip install kaleido==0.2.1` (specific version required)

### Korean Text Broken in PDF
**Problem**: Korean characters appear as boxes or garbled text
**Solution**: Ensure macOS system fonts are accessible:
- AppleSDGothicNeo.ttc at `/System/Library/Fonts/AppleSDGothicNeo.ttc`
- AppleGothic.ttf at `/System/Library/Fonts/AppleGothic.ttf`
- ReportLab TTFont registration handles font loading automatically

### Download Buttons Disappear After Click
**Problem**: After clicking PDF download, HTML download button disappears
**Solution**: Report data is now persisted in `st.session_state.generated_report`
- Download buttons remain visible after any download
- Click "🔄 Generate New Report" to regenerate

## File References

When discussing code locations, use these patterns:
- `app.py:45` - Chat input handling
- `ui/sidebar.py:104` - Report generation UI section
- `utils/genie_helper.py:101` - Response processing logic
- `utils/llm_helper.py:13` - Multi-provider constructor
- `utils/report_helper.py:68` - PDF generation method with Korean font support
- `utils/report_generator.py:15` - Business report generation
- `utils/map_helper.py:50` - Geometry parsing and map creation
- `utils/loading_helper.py:10` - Loading video display and removal
- `core/config.py:31` - Genie Space configuration
- `core/message_handler.py` - Chat message processing

## Documentation

- **User Guide**: `PHASE2_FEATURES.md` - Complete feature documentation
- **Examples**: `examples/` - Standalone examples for report generatio
- **README**: Overview and deployment instructions

## Key Learnings for New Features

1. **Always use helpers**: Don't put business logic directly in `app.py`
2. **Preserve message structure**: Include all optional fields (code, chart_data, table_data, domain)
3. **Handle both success and error cases**: Return `{"success": bool, "content": str, "error": str}`
4. **Test locally before deploying**: Use mock mode or local credentials
5. **Remember single-process constraint**: No background workers, no separate API servers
6. **Session state persistence**: Use `st.session_state` for data that must survive reruns (e.g., generated reports)
7. **Korean text support**: Register Korean fonts in ReportLab for PDF generation
8. **Simplified architecture**: Direct REGION_GENIE queries with automatic map detection
9. **Message structure for reports**: Extract conversation data from `messages` list with proper filtering of queries and data
10. **LLM Analysis**: All data responses now include mandatory LLM business insights

## UI Components

### Main Components
- **`ui/sidebar.py`**: Sidebar with chat history, search, and report generation
- **`ui/chat_display.py`**: Message display with code, tables, and charts
- **`ui/session.py`**: Session state initialization and management
- **`ui/styles.py`**: Custom CSS styling

### Core Logic
- **`core/config.py`**: Databricks client initialization and configuration
- **`core/message_handler.py`**: Chat input processing and response handling

## Recent Additions

### Business Report Generation (2024)
- **Purpose**: Generate comprehensive business analysis reports from chat sessions
- **Implementation**: `utils/report_generator.py` + sidebar UI integration
- **Features**:
  - LLM-based business insights in Korean
  - Structured report with executive summary, analysis, insights, recommendations
  - PDF/HTML export with Korean font support
  - Session state persistence for stable download buttons
- **Known Issues Fixed**:
  - Korean text encoding in PDF (resolved with TTFont registration)
  - Download button disappearance (resolved with session state caching)

### Simplified Architecture (2025)
- **Purpose**: Streamline query processing by removing routing complexity
- **Implementation**: Direct REGION_GENIE queries with automatic map and LLM analysis
- **Key Changes**:
  - **Router removed**: No more multi-domain routing or query analysis phase
  - **Single Genie**: All queries go directly to REGION_GENIE
  - **Auto map detection**: Checks for `geometry` column and creates maps automatically
  - **Mandatory LLM**: All data responses include LLM business insights
  - **Code reduction**: ~250 lines removed from message_handler.py
- **Benefits**:
  - Faster response times (no router LLM call)
  - Simpler code maintenance
  - Enhanced functionality (LLM analysis on all responses)
  - More predictable behavior

### Loading Video Integration (2024)
- **Purpose**: Provide visual feedback during query processing with looping video
- **Implementation**: `utils/loading_helper.py` + `core/message_handler.py` integration
- **Features**:
  - Displays `static/test.mp4` during async operations
  - Automatic video removal after query completion or error
  - Integrated into REGION_GENIE queries
  - Base64 encoding for reliable video delivery
  - Configurable width and loop behavior
- **Usage**: Automatically activated during query processing phases

### Polygon Map Visualization (2024)
- **Purpose**: Visualize geographic boundary data (polygons) from REGION_GENIE queries
- **Implementation**: `utils/map_helper.py` polygon map support + automatic geometry detection
- **Features**:
  - WKT format support (e.g., `POLYGON((lng lat, ...))`)
  - GeoJSON format support (e.g., `{"type": "Polygon", "coordinates": [...]}`)
  - Automatic geometry column detection
  - Choropleth-style coloring based on numeric values
  - Interactive popups with region information
  - Automatic name/value column detection
  - Seamless integration with existing point map functionality
- **Usage**: Automatically activated when REGION_GENIE returns data with `geometry` column
- **Testing**: Run `python test_polygon_map.py` to verify functionality
- **Technical Details**:
  - Uses Folium GeoJson for rendering
  - Shapely for WKT/GeoJSON parsing
  - GeoPandas for polygon data handling
  - Priority: Geometry columns → Lat/Lon columns → Other map types
- 별도의 언급이 없는 이상 추가 md파일을 생성하게 하지마
- 서버를 재시작하지마 