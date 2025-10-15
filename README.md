# Databricks Data Chat Application

A chat-based interface for interacting with Databricks data using natural language queries, with visualization and report generation capabilities. **Designed for Databricks Apps deployment with full Genie API and LLM integration.**

## 📁 Project Structure

```
databricks/
├── app.py               # Streamlit application (main entry point)
├── app.yaml            # Databricks Apps configuration
├── requirements.txt    # Python dependencies
├── utils/              # Helper modules
│   ├── __init__.py
│   ├── genie_helper.py    # Genie API utilities
│   ├── llm_helper.py      # LLM endpoint utilities
│   └── data_helper.py     # Data processing utilities
├── SPEC.md            # Project specification
├── README.md          # This file
└── .archived/         # Previous backend/frontend structure (archived)
```

## 🚀 Databricks Apps Deployment

### Prerequisites
- Databricks workspace with Apps enabled
- Databricks CLI installed
- Genie Space ID (for Genie API mode)

### Deploy to Databricks Apps

1. **Install Databricks CLI** (if not already installed):
```bash
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
```

2. **Authenticate**:
```bash
databricks auth login --host <your-workspace-url>
```

3. **Deploy the app**:
```bash
databricks apps deploy <app-name> --source-code-path .
```

The app will be available at: `https://<workspace-url>/apps/<app-name>`

## 🛠️ Local Development

### Run Locally (with Databricks authentication)

1. **Set up environment**:
```bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=your-token
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the app**:
```bash
streamlit run app.py
```

The app will start at `http://localhost:8501`

## 🤖 AI Integration Modes

The app supports **multiple AI backends** that can be switched via the UI:

### 1. **Genie API Mode** (Recommended)
- **Natural language to SQL** conversion
- **Automatic query execution** on Databricks tables
- **Conversation context** maintained across queries
- **Data visualization** from query results

**Setup:**
- Get your Genie Space ID from Databricks workspace
- Enter it in the sidebar settings
- Start asking questions in natural language!

**Example queries:**
- "Show me total sales by region for Q4 2024"
- "What are the top 10 customers by revenue?"
- "Compare this month's performance to last month"

### 2. **LLM Endpoint Mode**
- Call any **Databricks Serving Endpoint**
- Support for **chat models** and **completion models**
- **Conversation history** passed for context
- Custom system prompts

**Setup:**
- Deploy an LLM to Databricks Model Serving
- Enter endpoint name in sidebar
- Chat with your custom LLM!

**Supported endpoints:**
- Chat models (GPT-4, Claude, Llama, etc.)
- Completion models
- Custom fine-tuned models

### 3. **Mock Mode** (Demo)
- No configuration needed
- Sample data and visualizations
- Test the UI without backend setup

## 🎨 Features

### Current Implementation

✅ **AI Integration:**
- Databricks Genie API (natural language to SQL)
- LLM Serving Endpoints (chat & completion)
- Conversation context management
- Multi-turn conversations

✅ **Data Processing:**
- SQL query execution via Genie
- Automatic data visualization
- Chart type auto-detection
- SQL code formatting and display

✅ **UI/UX:**
- Streamlit-based chat interface
- Multiple AI mode selection
- User authentication (via Databricks Apps headers)
- Session management
- Chat history persistence

✅ **Visualization:**
- Auto-detect best chart type
- Bar, Line, Pie, Scatter, Heatmap charts
- Interactive Plotly visualizations
- Geographic data visualization:
  - Point maps (lat/lon coordinates)
  - Polygon maps (WKT/GeoJSON boundaries)
  - Choropleth coloring based on values
  - Interactive Folium maps with popups
- Data table display

### Coming Soon

⏳ PDF report generation (ReportLab)
⏳ HTML report generation (Jinja2)
⏳ Vector Search integration (RAG)
⏳ Multi-user collaboration features

## 📋 Configuration Files

### app.yaml
Databricks Apps configuration:
```yaml
command: ['streamlit', 'run', 'app.py']
env:
  - name: 'STREAMLIT_SERVER_HEADLESS'
    value: 'true'
```

### requirements.txt
```
streamlit>=1.28.0
databricks-sdk>=0.23.0
databricks-sql-connector>=3.0.0
plotly>=5.17.0
pandas>=2.0.0
```

## 🔌 Databricks Integration

### Genie API Integration
```python
from utils.genie_helper import GenieHelper
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
genie = GenieHelper(w, "your-genie-space-id")

# Start conversation
result = genie.start_conversation("Show me sales data")

# Continue conversation
result = genie.continue_conversation(
    conversation_id,
    "What about last quarter?"
)
```

### LLM Endpoint Integration
```python
from utils.llm_helper import LLMHelper
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
llm = LLMHelper(w)

# Chat completion
result = llm.chat_completion(
    "chat-model-endpoint",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Analyze this data..."}
    ]
)
```

### User Authentication
The app retrieves user info from Databricks Apps headers:
- `X-Forwarded-Email` - User email
- `X-Forwarded-Preferred-Username` - Username
- `X-Forwarded-Access-Token` - User access token (for OBO)

## 📊 Architecture

### Data Flow

```
User Query
    ↓
Streamlit UI
    ↓
AI Mode Selection
    ├── Genie API → SQL Generation → Query Execution → Results
    ├── LLM Endpoint → Model Inference → Response
    └── Mock Mode → Sample Data
    ↓
Data Processing (utils/)
    ↓
Visualization (Plotly)
    ↓
Display Results
```

### Why This Architecture?
- **Single Process**: Databricks Apps requirement
- **Direct SDK Access**: No intermediate API needed
- **Simplified Auth**: Automatic via Databricks Apps
- **Modular Helpers**: Easy to extend and maintain

## 🔒 Security

- **Authentication**: Handled by Databricks Apps platform
- **Authorization**: Uses user's Databricks permissions
- **On-behalf-of-user**: App acts with user's credentials
- **Secrets**: Can use Databricks Secret Scopes

## 📝 Usage Examples

### Using Genie API

1. Select "Genie API" mode in sidebar
2. Enter your Genie Space ID
3. Ask questions:
   - "Show me revenue by product category"
   - "What were our top 5 selling items last month?"
   - "Compare Q3 and Q4 performance"

### Using LLM Endpoint

1. Select "LLM Endpoint" mode
2. Enter your endpoint name (e.g., "llama-3-chat")
3. Chat with the model:
   - "Explain this sales trend"
   - "Summarize these findings"
   - "Generate a marketing strategy based on this data"

### Visualization

- Select chart type in sidebar (or use "Auto")
- Charts automatically generated from query results
- Interactive Plotly charts (zoom, pan, hover)
- Download charts as images

## 🐛 Troubleshooting

### Genie API Issues
- **Error: Invalid Space ID**: Check your Genie Space ID in Databricks UI
- **Error: No data returned**: Verify your question matches available data
- **Error: Permission denied**: Ensure user has access to Genie Space

### LLM Endpoint Issues
- **Error: Endpoint not found**: Check endpoint name in Model Serving
- **Error: Model timeout**: Increase timeout or check endpoint status
- **Error: Invalid response**: Check model endpoint configuration

### Local Development Issues
- **Error: Authentication failed**: Set `DATABRICKS_HOST` and `DATABRICKS_TOKEN`
- **Error: Module not found**: Run `pip install -r requirements.txt`
- **Error: Import error**: Ensure you're in the project root directory

## 📚 Resources

- [Databricks Apps Documentation](https://docs.databricks.com/dev-tools/databricks-apps/)
- [Databricks Genie API](https://docs.databricks.com/genie/)
- [Databricks Model Serving](https://docs.databricks.com/machine-learning/model-serving/)
- [Databricks Apps Cookbook](https://github.com/databricks-solutions/databricks-apps-cookbook)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Databricks SDK for Python](https://docs.databricks.com/dev-tools/sdk-python.html)

## 🚀 Next Steps

1. **Get Genie Space ID**: Create a Genie Space in your Databricks workspace
2. **Deploy the app**: Follow deployment instructions above
3. **Configure AI mode**: Select Genie API or LLM Endpoint
4. **Start chatting**: Ask questions about your data!

---

**Built with ❤️ using Databricks, Streamlit, and AI**
