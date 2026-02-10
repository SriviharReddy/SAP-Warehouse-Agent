from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """The standard state for the LangChain 1.0 agent, keeping track of conversation messages."""
    messages: Annotated[list[AnyMessage], add_messages]
