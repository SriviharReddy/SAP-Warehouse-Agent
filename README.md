# 📦 SAP Warehouse AI Cockpit

A state-of-the-art **SAP Warehouse Intelligence & Query Agent** built using the latest **LangChain 1.0** and **LangGraph 1.0** standards. It is powered by the **DeepSeek V4** API (`deepseek-v4-flash`) and features thread-safe asynchronous **SQLite conversation persistence** with a visually stunning, dark-themed Streamlit chat interface.

---

## 🚀 Key Architectural Features

*   **Modern LangChain 1.0 & LangGraph 1.0 API**: Completely avoids deprecated structures (like `create_react_agent`) in favor of the new **`langchain.agents.create_agent`** prebuilt, running on the robust LangGraph durable execution engine.
*   **DeepSeek V4 Integration**: Integrates the dedicated **`langchain-deepseek`** provider package. Configured with a specialized API toggle to disable the thinking pre-header (`extra_body={"thinking": {"type": "disabled"}}`), preventing OpenAI-compatible serialization errors during multi-turn tool loops.
*   **Async SQLite Checkpointing**: Leverages the official **`AsyncSqliteSaver`** checkpointer to store complete agent state snapshots asynchronously, ensuring safe database read/writes and conversation persistence under multi-threaded execution.
*   **Premium ChatGPT/Claude-style UI**:
    *   Glowing glassmorphism cockpit interface with curated high-tech dark colors and dynamic layouts.
    *   **➕ New Chat Button** to start a fresh thread with a generated UUID.
    *   **First-Question Titles**: Automatically caches the first user query as the clickable display name for that conversation tab in the sidebar history.
    *   **Visual API Call Logs**: Renders real-time mock SAP payloads returned by the tools inside collapsible visual blocks.

---

## 🛠️ 7 Read-Only mock SAP APIs (Tools)

To maintain a secure, query-only intelligence cockpit, all mock warehouse integration APIs are strictly read-only:

1.  **`async_get_stock_level`**: Queries item quantities, units of measure, and active storage bin locations.
2.  **`async_get_storage_bin_info`**: Retrieves dimensions, capacity utilization, environmental constraints (ambient vs. cold/frozen), and currently stored SKUs for a specific bin.
3.  **`async_list_inbound_deliveries`**: Lists general inbound shipments, ETAs, and carriers scheduled for the day.
4.  **`async_get_inbound_delivery_details`**: Resolves line-items, specific item counts, receiving docks, and handling instructions for an inbound shipment.
5.  **`async_list_outbound_orders`**: Lists general pending customer orders scheduled for picking and packing.
6.  **`async_get_outbound_order_details`**: Resolves recipient address, shipping priority, carrier class, and exact item-level quantities for an outbound order.
7.  **`async_get_picking_task_details`**: Returns progress status, assigned warehouse worker, source bins, and target staging areas for active picking tasks.

---

## 📂 Project Structure

```
.
├── my_agent/                 # Main agent package
│   ├── __init__.py           # Package initializer
│   ├── agent.py              # Graph compilation (using langchain.agents.create_agent)
│   └── utils/                # Utility modules
│       ├── __init__.py       # Package initializer
│       ├── tools.py          # 7 Async SAP mock API tools (read-only)
│       ├── nodes.py          # Placeholder
│       └── state.py          # State definitions (TypedDict)
├── app.py                    # Streamlit frontend app (caching database connections)
├── .env                      # Local environment configurations (ignored by git)
├── .gitignore                # Source control security filters (ignored .env, *.db)
├── langgraph.json            # LangGraph CLI project configuration
├── pyproject.toml            # Project dependency declarations (using Hatchling build system)
├── uv.lock                   # Managed uv package locks
└── README.md                 # Project documentation
```

---

## 🚦 Installation & Local Setup

This project uses **`uv`**, the ultra-fast Python package installer and resolver.

### 1. Prerequisite
Ensure `uv` is installed on your machine:
```bash
pip install uv
```

### 2. Synchronize Dependencies
Run the synchronization script from the project root. This will automatically create a `.venv` virtual environment and resolve all locked dependencies in seconds:
```bash
uv sync
```

### 3. Configure API Credentials
Create a `.env` file in the root directory (standard template provided):
```bash
# DeepSeek API Key
DEEPSEEK_API_KEY=your-real-deepseek-api-key-here

# Security setting for SQLite state serialization
LANGGRAPH_STRICT_MSGPACK=true
```

---

## 🏃 Running the Application

### 1. Launch the Streamlit Cockpit
Run the interactive Streamlit server inside your `uv` environment:
```bash
uv run streamlit run app.py
```
A new tab will automatically launch in your browser at `http://localhost:8501`.

### 2. Run Integration Tests
To verify asynchronous tool calls, database persistence, and DeepSeek connection logic without spawning the UI, run the verification script:
```bash
# On Windows PowerShell
$env:PYTHONIOENCODING="utf-8"
uv run python path/to/your/verify_agent.py
```

---

## 🔒 Source Control & Security
This project has a pre-initialized local Git repository with strict safety boundaries configured in `.gitignore`:
*   **Secrets Blocked**: `.env` and `.env.*` are completely ignored to ensure your live DeepSeek API keys are never leaked to remote repositories.
*   **Database Isolation**: Local database checkpoints (`*.db`, `checkpoints.db`) are excluded to avoid staging active conversational sessions.
