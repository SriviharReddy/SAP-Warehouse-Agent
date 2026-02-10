import os
import sqlite3
import asyncio
import uuid
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Verify that DeepSeek API Key is present
if not os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY") == "your_deepseek_api_key_here":
    st.warning("⚠️ DEEPSEEK_API_KEY is not configured in .env! Please set it before chatting.")

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from my_agent.agent import get_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# ==========================================
# 1. STREAMLIT AESTHETICS & HIGH-TECH STYLING
# ==========================================
st.set_page_config(
    page_title="SAP Warehouse AI Cockpit",
    page_icon="📦",
    layout="wide"
)

# Custom High-End CSS Injection for Glassmorphism and Dark Mode
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Main Background & Fonts */
    .stApp {
        background: linear-gradient(135deg, #0d0f1b 0%, #151a30 100%) !important;
        font-family: 'Outfit', sans-serif !important;
        color: #e2e8f0 !important;
    }
    
    /* Header Card with Glassmorphism */
    .header-container {
        background: rgba(25, 33, 62, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 8px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .header-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        margin: 0;
        font-weight: 400;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #090b14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Input Box Glassmorphism */
    div[data-testid="stChatInput"] {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: rgba(13, 15, 27, 0.8) !important;
        backdrop-filter: blur(8px);
    }
    
    /* Expander/Tool Calls Styling */
    .stExpander {
        border: 1px solid rgba(129, 140, 248, 0.2) !important;
        background-color: rgba(9, 11, 20, 0.6) !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
    }
    
    /* Custom Sidebar Header */
    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #818cf8;
        margin-bottom: 16px;
    }
    
    /* Sidebar conversation tab label */
    .conversation-title {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Layout Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📦 SAP Warehouse AI Cockpit</h1>
    <p class="header-subtitle">State-of-the-art LangGraph Agent powered by DeepSeek V4 and Async SQLite persistence. Direct async control over core SAP warehouse queries.</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE METADATA FUNCTIONS
# ==========================================
def init_metadata_table():
    """Initializes the thread_metadata table in SQLite to cache conversation titles."""
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
    """Retrieves list of existing threads with their first question display name."""
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
    """Saves first message metadata as conversation display name."""
    try:
        conn = sqlite3.connect("checkpoints.db")
        cursor = conn.cursor()
        
        # Check if already exists
        cursor.execute("SELECT first_message FROM thread_metadata WHERE thread_id = ?", (tid,))
        row = cursor.fetchone()
        if not row:
            # Truncate title for cleaner display
            clean_title = first_msg[:35] + ("..." if len(first_msg) > 35 else "")
            cursor.execute("INSERT OR REPLACE INTO thread_metadata (thread_id, first_message) VALUES (?, ?)", (tid, clean_title))
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving thread metadata: {e}")

# ==========================================
# 3. SIDEBAR CONVERSATION LIST (CHATGPT STYLE)
# ==========================================
st.sidebar.markdown('<div class="sidebar-header">🛠️ SAP Console</div>', unsafe_allow_html=True)

# 1. New Chat Button
if st.sidebar.button("➕ New Chat", use_container_width=True, type="primary"):
    # Generate fresh unique thread ID
    st.session_state.current_thread_id = f"thread-{uuid.uuid4().hex[:8]}"
    st.rerun()

st.sidebar.markdown('<div class="conversation-title">Recent Conversations</div>', unsafe_allow_html=True)

# 2. Render clickable history tabs
threads = get_existing_threads_with_titles()

# Default session state initialization
if "current_thread_id" not in st.session_state:
    if threads:
        st.session_state.current_thread_id = threads[0][0]
    else:
        st.session_state.current_thread_id = f"thread-{uuid.uuid4().hex[:8]}"

# Render threads list
if threads:
    for tid, title in threads:
        # Highlight active conversation
        if tid == st.session_state.current_thread_id:
            st.sidebar.button(f"💬 {title}", key=f"active-{tid}", use_container_width=True, disabled=True)
        else:
            if st.sidebar.button(f"💬 {title}", key=f"link-{tid}", use_container_width=True):
                st.session_state.current_thread_id = tid
                st.rerun()
else:
    st.sidebar.info("No active history. Start chatting below!")

st.sidebar.markdown("---")

# Quick command guidelines in sidebar
st.sidebar.subheader("📖 Quick SAP Commands")
st.sidebar.markdown("""
Try asking the assistant:
- *What inbound deliveries do we have today for WH-101?*
- *Get detailed receiving info for shipment INB-99821.*
- *Check capacity and env settings for storage bin B-402.*
- *Check inventory levels for SKU-8892 in WH-101.*
- *List outbound orders scheduled for picking.*
- *Check details of picking task TSK-SAP-98124.*
""")

# ==========================================
# 4. CHAT HISTORY LOADING (FROM SQLITE)
# ==========================================
thread_id = st.session_state.current_thread_id
config = {"configurable": {"thread_id": thread_id}}

async def load_chat_history_async():
    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
        agent = get_agent(checkpointer=checkpointer)
        state_snapshot = await agent.aget_state(config)
        return state_snapshot.values.get("messages", [])

# Fetch history inside event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    saved_messages = loop.run_until_complete(load_chat_history_async())
finally:
    loop.close()

# Display current chat history
for msg in saved_messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
            
    elif isinstance(msg, AIMessage):
        if msg.content:
            with st.chat_message("assistant"):
                st.markdown(msg.content)
                
    elif isinstance(msg, ToolMessage):
        # Present tool calls inside clean visual logs/expanders
        with st.chat_message("assistant"):
            with st.expander(f"⚙️ SAP API Execution: `{msg.name}` (Success)", expanded=False):
                st.json(msg.content)

# ==========================================
# 5. USER INPUT & ASYNC GRAPH RUN
# ==========================================
user_query = st.chat_input("Send command to SAP Gateway...")

if user_query:
    # 1. Save metadata (first question as title) on the very first query
    save_thread_metadata(thread_id, user_query)
    
    # 2. Display user query immediately
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # 3. Invoke the agent graph asynchronously
    with st.spinner("🔄 Querying SAP Gateway via DeepSeek V4..."):
        async def run_agent_async():
            async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
                agent = get_agent(checkpointer=checkpointer)
                # Invoke graph asynchronously
                await agent.ainvoke(
                    {"messages": [HumanMessage(content=user_query)]},
                    config=config
                )
                
                # Fetch new messages added during this turn
                new_state = await agent.aget_state(config)
                return new_state.values.get("messages", [])
                
        try:
            # Execute async calling
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            all_messages = loop.run_until_complete(run_agent_async())
            loop.close()
            
            # Find the new messages that were added after our user message
            user_msg_idx = -1
            for idx, m in enumerate(all_messages):
                if isinstance(m, HumanMessage) and m.content == user_query:
                    user_msg_idx = idx
            
            new_run_messages = all_messages[user_msg_idx + 1:] if user_msg_idx != -1 else []
            
            # 4. Render new AI response and tool calls
            for m in new_run_messages:
                if isinstance(m, AIMessage) and m.content:
                    with st.chat_message("assistant"):
                        st.markdown(m.content)
                elif isinstance(m, ToolMessage):
                    with st.chat_message("assistant"):
                        with st.expander(f"⚙️ SAP API Execution: `{m.name}` (Success)", expanded=True):
                            st.json(m.content)
            
            # Refresh the sidebar to show the newly added chat title immediately
            st.rerun()
                            
        except Exception as e:
            st.error(f"❌ Execution Error: {str(e)}")
            st.exception(e)
