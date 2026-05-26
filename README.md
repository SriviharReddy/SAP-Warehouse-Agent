# 📦 SAP Warehouse AI Cockpit

An intelligent, conversational dashboard providing natural language access to SAP Warehouse Management (WM) systems. Powered by DeepSeek V4 and LangGraph, the assistant allows warehouse managers and operators to query inventory levels, storage parameters, shipping schedules, and picking tasks in real time.

---

## ✨ Core Features

*   **Natural Language SAP Queries**: Instant query access to stock levels, bin configurations, inbound freight, outbound orders, and picking status.
*   **User Authentication**: Secure signup and login with bcrypt-hashed passwords. Each user's session and conversation history is fully isolated.
*   **Per-User Chat History**: A sidebar for managing multiple conversation threads, scoped to the logged-in user. The first query is used as the conversation title.
*   **Tool Call Logs**: Expandable JSON payloads showing the real-time response from each SAP tool call.
*   **Durable State Persistence**: Asynchronous SQLite checkpointing keeps conversation state across sessions.

---

## 🛠️ SAP Warehouse Integration APIs

The Cockpit is built on top of 7 asynchronous, read-only query tools:

1.  **`get_stock_level`**: Retrieves current material stock numbers, units of measure, and active storage bin assignments.
2.  **`get_storage_bin_info`**: Inspects bin capacities, current utilization rates, environmental constraints (e.g., Ambient vs. Cold Storage), and active SKUs in the bin.
3.  **`list_inbound_deliveries`**: Lists expected daily freight shipments, carriers, ETAs, and status.
4.  **`get_inbound_delivery_details`**: Resolves line-items, quantities, supplier names, receiving docks, and handling instructions for an inbound delivery.
5.  **`list_outbound_orders`**: Lists pending outbound shipping orders scheduled for picking and packing.
6.  **`get_outbound_order_details`**: Resolves customer destinations, shipping routes, priority status, and line-item details for outbound orders.
7.  **`get_picking_task_details`**: Returns assigned pickers, target staging areas, item lists, and active progress status for picking operations.

---

## 🏗️ Technical Stack & Architecture

*   **Orchestration Framework**: LangGraph / LangChain (for graph execution and state checkpointing)
*   **Language Model**: DeepSeek V4 via `langchain-deepseek`
*   **Persistence Layer**: Async SQLite Checkpointer (`AsyncSqliteSaver`)
*   **Authentication**: bcrypt password hashing, stored in SQLite alongside LangGraph checkpoints
*   **Frontend**: Streamlit
*   **Package Manager**: `uv`

---

## 📂 Project Structure

```
.
├── auth/                         # Application-level auth package
│   ├── __init__.py
│   ├── db.py                     # User storage & bcrypt credential logic
│   └── ui.py                     # Streamlit login / signup gate
├── my_agent/                     # Core Agent Package
│   ├── __init__.py
│   ├── agent.py                  # Compiled LangGraph agent graph
│   └── utils/
│       ├── __init__.py
│       └── tools.py              # 7 read-only SAP tools
├── app.py                        # Streamlit UI entry point
├── checkpoints.db                # SQLite state (auto-created, not committed)
├── .env                          # Environment variables (not committed)
├── .gitignore
├── langgraph.json                # LangGraph CLI config
├── pyproject.toml                # Project dependencies
└── README.md
```

---

## 🚦 Installation & Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
LANGGRAPH_STRICT_MSGPACK=true
```

---

## 🏃 Running the App

```bash
uv run streamlit run app.py
```

Opens at `http://localhost:8501`.

On first launch, create an account via the **Sign Up** tab. All subsequent visits will require login. Each user's conversation history is private and persists across sessions.
