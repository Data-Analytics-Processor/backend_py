"""This file contains the LangGraph Agent/workflow and interactions with the LLM."""

import pandas as pd
from typing import Annotated, Literal, TypedDict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.core.langgraph.tools import all_tools

# --- 1. State Definition ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    csv_file_path: Optional[str]

# --- 2. Tool Binding ---
tools_by_name = {t.name: t for t in all_tools}

# --- 3. Node Definitions ---

def agent_node(state: AgentState):
    llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    llm_with_tools = llm.bind_tools(all_tools)
    
    csv_path = state.get("csv_file_path")
    
    base_prompt = (
        "You are a senior data analyst. You have a set of specialized statistical tools:\n"
        "1. 'describe_dataset': For general summary statistics.\n"
        "2. 'get_correlation_matrix': For finding relationships between columns.\n"
        "3. 'get_normal_distribution': For plotting distribution curves.\n"
        "4. 'python_repl': For any custom analysis or plotting not covered above.\n\n"
        "Always prefer using the specialized tools (1-3) if they fit the user's request. "
        "Only use 'python_repl' if the request is complex or custom."
    )
    
    if csv_path:
        data_context = (
            f"\n\nDATA CONTEXT:\n"
            f"The file is available at: '{csv_path}'.\n"
            f"Pass this path to the tools when calling them."
        )
        sys_msg = SystemMessage(content=base_prompt + data_context)
    else:
        sys_msg = SystemMessage(content=base_prompt)
    
    response = llm_with_tools.invoke([sys_msg] + state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    outputs = []
    for tool_call in last_message.tool_calls:
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        outputs.append(
            {
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": tool_call["name"],
                "content": str(tool_result),
            }
        )
        
    return {"messages": outputs}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    if messages[-1].tool_calls:
        return "tools"
    return "__end__"

# --- 4. Graph Construction ---
def create_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile(checkpointer=MemorySaver())

graph_app = create_graph()