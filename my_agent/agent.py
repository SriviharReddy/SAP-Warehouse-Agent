from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from my_agent.utils.tools import sap_tools

# Load env variables at file import time
load_dotenv()

def get_agent(checkpointer=None):
    """Constructs the compiled LangGraph agent using the new LangChain 1.0 standard.
    
    Args:
        checkpointer: The state checkpointer (e.g., SqliteSaver or InMemorySaver).
    """
    # 1. Initialize the official DeepSeek chat model
    llm = ChatDeepSeek(
        model="deepseek-v4-flash",
        temperature=0.0,
        extra_body={
            "thinking": {"type": "disabled"}
        }
    )
    
    # 2. Compile the agent graph natively via create_agent
    agent = create_agent(
        model=llm,
        tools=sap_tools,
        checkpointer=checkpointer,
        system_prompt=(
            "You are an elite, highly capable SAP Warehouse Management Assistant. "
            "You have direct access to 7 mock asynchronous SAP APIs to query stock levels, storage bins, "
            "deliveries, outbound orders, create picking tasks, monitor tasks, and transfer inventory bins.\n\n"
            "Guidelines:\n"
            "1. When answering user queries, always utilize the appropriate SAP tool asynchronously.\n"
            "2. If multiple operations are needed (e.g., checking stock levels before executing a transfer), "
            "perform them in sequence using your toolset.\n"
            "3. Present your findings clearly, citing bin numbers, SKU numbers, quantity, and document reference IDs.\n"
            "4. Be precise and professional. Act as if you are directly connected to the SAP Gateway."
        )
    )
    return agent

# Export a default graph for LangGraph CLI / Studio compatibility (uses memory saver by default)
from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402
graph = get_agent(checkpointer=InMemorySaver())
