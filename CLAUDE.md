# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**SK Shieldus Chat Bot** is a Databricks Apps application that provides a natural language interface for querying regional data. The application uses Databricks Genie API for SQL generation and LLM for business insights.

**Key Constraint**: Single-process architecture required by Databricks Apps - everything runs in one Streamlit process without separate backend/frontend.

## Architecture

### Core Design Pattern

**Single-Process Flow**:
- Streamlit UI + Business Logic in one unified process
- Helper modules for reusable business logic
- Direct Databricks SDK calls from Streamlit
- Authentication via Databricks Apps headers

### Project Structure

**Entry Point**:
- `app.py` - Streamlit application entry point

**Core Components** (`core/`):
- `config.py` - Databricks client initialization and configuration
- `message_handler.py` - Chat input processing and response handling

**UI Components** (`ui/`):
- `sidebar.py` - Sidebar with settings and report generation
- `chat_display.py` - Message rendering with visualizations
- `session.py` - Session state management
- `styles.py` - Custom CSS styling
- `landing.py` - Landing page display
- `theme_config.py` - Theme configurations

**Helper Modules** (`utils/`):
- `genie_helper.py` - Databricks Genie API (NL2SQL conversion)
- `llm_helper.py` - LLM endpoint interface
- `data_helper.py` - Data visualization and charts
- `map_helper.py` - Geospatial visualization
- `report_helper.py` - PDF/HTML report generation
- `report_generator.py` - Business report generation
- `loading_helper.py` - Loading video display
- `prompt_selector.py` - Dynamic prompt selection
- `seoul_boundary.py` - Seoul boundary data

**Prompt System** (`prompts/`):
- `manager.py` - Prompt loading
- Various `.txt` files for analysis scenarios

## Key Features

### Natural Language Querying
- Users ask questions in natural language
- Genie API converts queries to SQL
- Direct REGION_GENIE execution
- Automatic result processing

### Automatic Visualization
- **Geometry Detection**: Automatically detects and creates maps
- **Chart Generation**: Plotly charts based on data
- **Interactive Tables**: DataFrames with proper formatting

### LLM Analysis
- **Mandatory**: All data responses include business insights
- **Streaming**: Real-time response display
- **Inq-Based Prompts**: Dynamic prompt selection
- **Korean Support**: Business insights in Korean

### Session Management
- **Chat History**: Maintains conversation context
- **Session Switching**: Multiple chat sessions
- **Message Persistence**: Complete message storage

### Report Generation
- **Business Reports**: Comprehensive analysis from sessions
- **Multiple Formats**: PDF and HTML export
- **Korean Support**: Proper font handling
- **Structured Output**: Executive summary, insights, recommendations

### Loading Experience
- **Video Feedback**: Animated loading video
- **Sequential Messages**: Step-by-step progress
- **Smooth Transitions**: Automatic cleanup

## Configuration

### Required Secrets

**Databricks Configuration** (`.streamlit/secrets.toml`):
- `HOST` - Workspace URL
- `TOKEN` - Personal access token
- `GENIE_SPACE_ID` - Default Genie Space ID

**Genie Spaces**:
- `REGION_GENIE` - Regional data space ID

**LLM Configuration**:
- `llm_endpoint` - Databricks serving endpoint

### Application Configuration

**app.yaml**: Defines Streamlit command and environment variables for deployment.

## Development

### Local Development

**Setup**:
1. Install dependencies: `pip install -r requirements.txt`
2. Configure secrets in `.streamlit/secrets.toml`
3. Run: `streamlit run app.py`
4. Access: http://localhost:8501

**Environment Variables**:
- `DATABRICKS_HOST` - Workspace URL
- `DATABRICKS_TOKEN` - Access token

### Deployment

**Databricks Apps**:
1. Authenticate: `databricks auth login --host <workspace-url>`
2. Deploy: `databricks apps deploy <app-name> --source-code-path .`

## Data Flow

### Query Processing

1. **User Input**: Natural language query submitted
2. **Loading Phase**: Video display with sequential messages
3. **Genie Processing**: SQL generation and execution
4. **Visualization**: Automatic geometry detection and chart creation
5. **LLM Analysis**: Business insights generation (streaming)
6. **Session Update**: Messages stored with complete data

### Message Structure

**User Messages**:
- `role`: "user"
- `content`: Query text

**Assistant Messages**:
- `role`: "assistant"
- `content`: Response text
- `code`: SQL query (optional)
- `table_data`: DataFrame (optional)
- `chart_data`: Plotly HTML (optional)
- `domain`: Data domain (optional)
- `is_llm_analysis`: LLM flag (optional)
- `sql_expanded`: Display state (optional)
- `show_table`: Display state (optional)

## Helper Module Details

### GenieHelper

**Purpose**: Databricks Genie API interface

**Key Methods**:
- `start_conversation(prompt)` - New conversation
- `continue_conversation(conversation_id, prompt)` - Follow-up
- `get_query_result(statement_id)` - Retrieve results
- `process_response(response)` - Parse responses
- `set_progress_callback(callback)` - Progress updates

### LLMHelper

**Purpose**: LLM completion interface

**Key Methods**:
- `chat_completion()` - Standard completion
- `chat_completion_stream()` - Streaming responses
- `text_completion()` - Text-only completion
- `get_embeddings()` - Generate embeddings

### MapHelper

**Purpose**: Geospatial visualization

**Key Methods**:
- `create_point_map()` - Point markers
- `create_choropleth_map()` - Polygon maps
- `detect_geometry_columns()` - Auto detection
- `parse_geometry()` - WKT/GeoJSON parsing

**Features**:
- WKT and GeoJSON support
- Rank-based coloring
- Seoul boundary integration
- Interactive Plotly maps

### ReportHelper

**Purpose**: Low-level report generation

**Key Methods**:
- `add_section()` - Add report section
- `add_dataframe()` - Add data table
- `add_chart()` - Add visualization
- `generate_pdf()` - Create PDF
- `generate_html()` - Create HTML
- `clear()` - Reset state

**Features**:
- ReportLab PDF generation
- Jinja2 HTML templating
- Korean font support
- Plotly chart export

### ReportGenerator

**Purpose**: Business report generation

**Key Functions**:
- `generate_business_report()` - Full pipeline
- `generate_report_preview()` - Preview statistics
- `_extract_conversation_data()` - Parse messages
- `_generate_llm_analysis()` - LLM insights
- `_build_report_structure()` - Assemble report

**Report Structure**:
- Executive Summary (경영진 요약)
- Analysis Details (분석 상세)
- Key Insights (주요 인사이트)
- Business Recommendations (비즈니스 권장사항)
- Conclusion (결론)

### LoadingHelper

**Purpose**: Visual feedback during operations

**Key Functions**:
- `display_loading_video()` - Show video
- `remove_loading_video()` - Hide video
- `update_loading_message()` - Update text
- `display_loading_with_sequential_messages()` - Sequential display
- `update_to_next_message()` - Progress step

**Default Messages**:
1. "Understanding your query..."
2. "Connecting to Genie API..."
3. "Generating SQL query..."
4. "Fetching data..."
5. "Preparing results..."
6. "Complete!"

## State Management

### Session State Keys

**Core State**:
- `messages` - Chat messages in current session
- `conversation_id` - Active Genie conversation
- `conversation_ids` - Domain to conversation map
- `pending_prompt` - Query awaiting processing

**Session Management**:
- `chat_sessions` - All chat sessions
- `current_session_id` - Active session identifier
- `current_session_index` - Session list index

**Report State**:
- `generated_report` - Cached report data (dict with 'pdf' and 'html')

### Update Patterns

**Immediate Update**: After every message
- Add to `st.session_state.messages`
- Call `update_current_session_messages()`
- Ensures consistency

**Session Switching**: When changing sessions
- Load messages from session
- Update identifiers and indices
- Restore conversation context

## Important Constraints

### Databricks Apps
- Single process only
- No separate API server
- Authentication via headers
- WorkspaceClient auto-authenticates

### Genie API
- Valid Space ID required
- User permissions needed
- Conversation IDs per domain
- Statement ID for results

### Report Generation
- kaleido 0.2.1 for Plotly export
- Korean fonts required (macOS)
- Table truncation (50 rows)
- Large HTML files with Plotly.js

**Font Fallback**:
1. AppleSDGothicNeo.ttc
2. AppleGothic.ttf
3. Helvetica

### Performance
- LLM temperature: 0.3
- LLM max_tokens: 2000
- DataFrame preview: 10 rows
- Streaming for UX

## File References

Use this format for code locations:
- `app.py:17` - Page configuration
- `core/config.py:7` - Client init
- `core/message_handler.py:135` - Chat handler
- `utils/genie_helper.py:38` - Conversation start
- `utils/llm_helper.py:32` - Chat completion
- `utils/map_helper.py:64` - Auto zoom
- `utils/report_generator.py:16` - Report generation
- `ui/sidebar.py:1` - Sidebar rendering

## Dependencies

### Core Framework
- `streamlit==1.50.0` - UI framework
- `pandas>=2.0.0` - Data manipulation

### Databricks Integration
- `databricks-sdk==0.67.0` - API client
- `databricks-sql-connector>=3.0.0` - SQL execution

### Visualization
- `plotly>=5.17.0` - Interactive charts
- `kaleido>=0.2.1` - Chart export

### Geospatial
- `geopandas>=0.14.0` - Geometry handling
- `shapely>=2.0.0` - Geometry operations
- `pyproj>=3.6.0` - Coordinate transforms

### Report Generation
- `reportlab>=4.0.0` - PDF creation
- `jinja2>=3.1.0` - HTML templating

### Other
- `openai>=1.0.0` - OpenAI-compatible client

## Common Issues

### Import Errors
**Problem**: ModuleNotFoundError
**Solution**: Run from project root: `streamlit run app.py`

### Genie Errors
**Problem**: No data or API errors
**Solution**:
- Verify Space ID
- Check permissions
- Confirm query schema match

### PDF Generation
**Problem**: Image export errors
**Solution**: `pip install kaleido==0.2.1`

### Korean Text
**Problem**: Broken characters in PDF
**Solution**:
- Verify system fonts exist
- Check `/System/Library/Fonts/`
- TTFont registration automatic

### Download Buttons
**Problem**: Buttons disappear
**Solution**:
- Data persisted in `st.session_state.generated_report`
- Use "Generate New Report" to regenerate

### Loading Video
**Problem**: Not displaying
**Solution**:
- Verify `static/test.mp4` exists
- Check base64 encoding
- Confirm container not cleared early

## Recent Changes

### Simplified Architecture (2025)
- **Router removed**: Direct REGION_GENIE queries
- **Auto map detection**: Checks geometry columns
- **Mandatory LLM**: All responses analyzed
- **Code reduction**: ~250 lines removed

**Benefits**:
- Faster responses
- Simpler maintenance
- Enhanced functionality
- Predictable behavior

### Dynamic Prompt System (2025)
- Prompt selection by data attributes
- Multiple template types
- Automatic grouping by characteristics
- Merged analysis strategies

### Business Report Generation (2024)
- LLM-based Korean insights
- Structured report sections
- PDF/HTML export
- Session state persistence

### Polygon Map Visualization (2024)
- WKT/GeoJSON support
- Rank-based coloring
- Interactive popups
- Automatic detection

### Loading Video Integration (2024)
- Visual feedback during processing
- Sequential message display
- Base64 encoding
- Automatic cleanup

## Best Practices

### Development Guidelines
1. Put business logic in helper modules
2. Update session state immediately
3. Return success/error dicts
4. Preserve message structure
5. Test locally with credentials
6. Remember single-process constraint
7. Register Korean fonts for PDFs
8. Use automatic geometry detection
9. Stream LLM for UX
10. Persist state for stability

### Error Handling
- Wrap API calls in try/except
- Return dicts with success flag
- Include error messages
- Display user-friendly errors

### Testing
- Use mock mode for UI
- Configure real credentials for integration
- Test Korean text rendering
- Verify full query → analysis flow

## Documentation

- **CLAUDE.md**: This file (developer guidance)
- **README.md**: Project overview
- **PHASE2_FEATURES.md**: Feature documentation (if exists)

## Important Notes

- Do not create additional md files and python files unless otherwise stated.
- Do not restart the server for testing
