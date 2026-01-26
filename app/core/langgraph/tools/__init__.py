"""LangGraph tools for enhanced language model capabilities.

This package contains custom tools that can be used with LangGraph to extend
the capabilities of language models.
"""
from langchain_experimental.tools import PythonAstREPLTool
from app.core.langgraph.tools.basic_statistics import describe_dataset
from app.core.langgraph.tools.relative_statistics import get_correlation_matrix
from app.core.langgraph.tools.graphical_statistics import get_normal_distribution

# Initialize the generic Python REPL
python_repl = PythonAstREPLTool()

# Export all tools as a list
all_tools = [
    python_repl,
    describe_dataset,
    get_correlation_matrix,
    get_normal_distribution
]