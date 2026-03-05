import asyncio
import os
import sqlite3
import uuid

from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

import streamlit as st

from my_agent.agent import get_agent

# Load environment variables
load_dotenv()

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="SAP Warehouse AI Assistant",
    page_icon="📦",
    layout="wide",
)

# Warn if API key is missing
if not os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY") == "your_deepseek_api_key_here":
    st.warning("⚠️ DEEPSEEK_API_KEY is not configured in .env! Please set it before chatting.")

# ==========================================
# DATABASE METADATA FUNCTIONS
# ==========================================

def init_metadata_table():
    """Initializes the thread_metadata table in SQLite to store conversation titles."""
    conn = sqlite3.connect("checkpoints.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS thread_metadata (
            thread_id TEXT PRIMARY KEY,
            first_message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_metadata_table()


def get_existing_threads_with_titles():
    """Returns a list of (thread_id, display_title) tuples ordered by most recent."""
    try:
        conn = sqlite3.connect("checkpoints.db")
        cursor = conn.cursor()
        cursor.execute("SELECT thread_id, first_message FROM thread_metadata ORDER BY timestamp DESC")
        threads = [(row[0], row[1]) for row in cursor.fetchall()]
        conn.close()
        return threads
    except Exception:
        return []


def save_thread_metadata(tid, first_msg):
    """Saves the first message of a thread as its display name (only once)."""
    try:
        conn = sqlite3.connect("checkpoints.db")
        cursor = conn.cursor()
        cursor.execute("SELECT first_message FROM thread_metadata WHERE thread_id = ?", (tid,))
        if not cursor.fetchone():
            clean_title = first_msg[:50] + ("..." if len(first_msg) > 50 else "")
            cursor.execute(
                "INSERT OR REPLACE INTO thread_metadata (thread_id, first_message) VALUES (?, ?)",
                (tid, clean_title),
            )
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving thread metadata: {e}")


# ==========================================
# SIDEBAR — CONVERSATION HISTORY
# ==========================================
st.sidebar.title("SAP Warehouse Assistant")

if st.sidebar.button("+ New Chat", use_container_width=True, type="primary"):
    st.session_state.current_thread_id = f"thread-{uuid.uuid4().hex[:8]}"
    st.rerun()

st.sidebar.subheader("Recent Conversations")

threads = get_existing_threads_with_titles()

if "current_thread_id" not in st.session_state:
    if threads:
        st.session_state.current_thread_id = threads[0][0]
    else:
        st.session_state.current_thread_id = f"thread-{uuid.uuid4().hex[:8]}"

if threads:
    for tid, title in threads:
        if tid == st.session_state.current_thread_id:
            st.sidebar.button(title, key=f"active-{tid}", use_container_width=True, disabled=True)
        else:
            if st.sidebar.button(title, key=f"link-{tid}", use_container_width=True):
                st.session_state.current_thread_id = tid
                st.rerun()
else:
    st.sidebar.info("No conversations yet. Start chatting below.")

st.sidebar.divider()

st.sidebar.subheader("Example Queries")
st.sidebar.markdown("""
- What inbound deliveries do we have today for WH-101?
- Get details for shipment INB-99821.
- Check capacity for storage bin B-402.
- Check inventory levels for SKU-8892 in WH-101.
- List outbound orders scheduled for picking.
- Get details of picking task TSK-SAP-98124.
""")

# ==========================================
# CHAT HISTORY (FROM SQLITE)
# ==========================================
thread_id = st.session_state.current_thread_id
config = {"configurable": {"thread_id": thread_id}}

st.title("📦 SAP Warehouse Assistant")


async def load_chat_history_async():
    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
        agent = get_agent(checkpointer=checkpointer)
        state_snapshot = await agent.aget_state(config)
        return state_snapshot.values.get("messages", [])


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    saved_messages = loop.run_until_complete(load_chat_history_async())
finally:
    loop.close()

for msg in saved_messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        if msg.content:
            with st.chat_message("assistant"):
                st.markdown(msg.content)
    elif isinstance(msg, ToolMessage):
        with st.chat_message("assistant"):
            with st.expander(f"Tool call: `{msg.name}`", expanded=False):
                st.json(msg.content)

# ==========================================
# USER INPUT & AGENT INVOCATION
# ==========================================
user_query = st.chat_input("Ask about warehouse inventory, deliveries, orders, or picking tasks...")

if user_query:
    save_thread_metadata(thread_id, user_query)

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.spinner("Thinking..."):
        async def run_agent_async():
            async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
                agent = get_agent(checkpointer=checkpointer)
                await agent.ainvoke(
                    {"messages": [HumanMessage(content=user_query)]},
                    config=config,
                )
                new_state = await agent.aget_state(config)
                return new_state.values.get("messages", [])

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            all_messages = loop.run_until_complete(run_agent_async())
            loop.close()

            # Find messages added after the user's message in this turn
            user_msg_idx = -1
            for idx, m in enumerate(all_messages):
                if isinstance(m, HumanMessage) and m.content == user_query:
                    user_msg_idx = idx

            new_run_messages = all_messages[user_msg_idx + 1:] if user_msg_idx != -1 else []

            for m in new_run_messages:
                if isinstance(m, AIMessage) and m.content:
                    with st.chat_message("assistant"):
                        st.markdown(m.content)
                elif isinstance(m, ToolMessage):
                    with st.chat_message("assistant"):
                        with st.expander(f"Tool call: `{m.name}`", expanded=True):
                            st.json(m.content)

            st.rerun()

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.exception(e)
