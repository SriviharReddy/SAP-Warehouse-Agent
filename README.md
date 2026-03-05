# SAP Warehouse AI Assistant

A conversational assistant for querying SAP Warehouse Management (WM) systems using natural language. Built with LangGraph for agent orchestration and Streamlit for the UI.

## Features

- **Natural language queries** over warehouse data — inventory, storage bins, inbound deliveries, outbound orders, and picking tasks
- **Conversation history** with a sidebar listing past chats (named after the first message) and a "New Chat" button
- **Tool call transparency** — each SAP API call is shown in an expandable log within the chat
- **Persistent state** — conversations are stored in a local SQLite database across sessions

## SAP Integration Tools (Read-Only)

All tools are query-only and do not modify warehouse state:

| Tool | Description |
|------|-------------|
| `get_stock_level` | Current stock quantity, unit of measure, and bin assignment for a material |
| `get_storage_bin_info` | Bin capacity, utilization, environmental type, and active SKUs |
| `list_inbound_deliveries` | Scheduled inbound shipments with carrier, ETA, and status |
| `get_inbound_delivery_details` | Line items, quantities, supplier, and receiving dock for a delivery |
| `list_outbound_orders` | Outbound shipping orders pending picking and packing |
| `get_outbound_order_details` | Customer, route, priority, and line items for an outbound order |
| `get_picking_task_details` | Assigned picker, staging area, item list, and progress for a task |

## Tech Stack

- **Agent**: [LangGraph](https://github.com/langchain-ai/langgraph) with `AsyncSqliteSaver` for durable state
- **LLM**: DeepSeek V4 via `langchain-deepseek`
- **UI**: [Streamlit](https://streamlit.io/)
- **Package manager**: [`uv`](https://github.com/astral-sh/uv)

## Project Structure

```
.
├── my_agent/
│   ├── agent.py          # Agent graph definition
│   └── utils/
│       ├── tools.py      # SAP query tools
│       ├── nodes.py      # Graph nodes
│       └── state.py      # State schema
├── app.py                # Streamlit UI
├── .env                  # Environment variables (not committed)
├── pyproject.toml        # Dependencies
└── langgraph.json        # LangGraph CLI config
```

## Setup

**1. Install dependencies**

```bash
uv sync
```

**2. Configure environment variables**

Create a `.env` file in the project root:

```env
DEEPSEEK_API_KEY=your_api_key_here
LANGGRAPH_STRICT_MSGPACK=true
```

**3. Run the app**

```bash
uv run streamlit run app.py
```

The app will open at `http://localhost:8501`.
