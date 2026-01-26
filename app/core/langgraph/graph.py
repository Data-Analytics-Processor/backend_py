"""This file contains the LangGraph Agent/workflow and interactions with the LLM."""

import pandas as pd
from typing import Annotated, Literal, TypedDict, Optional

from langchain_openai import ChatOpenAI
from langchain_experimental.tools import PythonAstREPLTool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config import settings

# --- 1. State Definition ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    # Add a field to hold the CSV file path
    csv_file_path: Optional[str]

# --- 2. Tool Setup ---
python_repl = PythonAstREPLTool()

# Allow the agent to use pandas inside the tool
# (We define locals so the agent can access 'df' if we pre-load it, 
# but usually it's safer to let the agent write 'pd.read_csv' itself.)
tools = [python_repl]
tools_by_name = {t.name: t for t in tools}

# --- 3. Node Definitions ---

def agent_node(state: AgentState):
    llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    llm_with_tools = llm.bind_tools(tools)
    
    # Dynamic System Prompt
    csv_path = state.get("csv_file_path")
    
    base_prompt = (
        "You are a senior data analyst. You have access to a python_repl tool."
        "When asked to analyze data, ALWAYS write Python code to inspect the data first."
    )
    
    if csv_path:
        # Give the agent the exact path so it can write: df = pd.read_csv(...)
        data_context = (
            f"\n\nDATA CONTEXT:\n"
            f"There is a CSV file available at this path: '{csv_path}'.\n"
            f"To analyze it, start your code with:\n"
            f"df = pd.read_csv('{csv_path}')"
        )
        sys_msg = SystemMessage(content=base_prompt + data_context)
    else:
        sys_msg = SystemMessage(content=base_prompt)
    
    # Invoke
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
    last_message = messages[-1]
    if last_message.tool_calls:
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