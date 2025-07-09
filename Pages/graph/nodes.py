from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState, serialize_state
import json
from typing import Literal
from .tools import complete_python_task
# from langgraph.prebuilt import ToolInvocation, ToolExecutor

# Minimal local replacements for ToolInvocation and ToolExecutor
class ToolInvocation:
    def __init__(self, tool, tool_input):
        self.tool = tool
        self.tool_input = tool_input

class ToolExecutor:
    def __init__(self, tools):
        self.tools = {t.name: t for t in tools}

    def batch(self, tool_invocations, return_exceptions=True):
        results = []
        for invocation in tool_invocations:
            tool_func = self.tools.get(invocation.tool)
            if tool_func:
                try:
                    # Only pass the arguments expected by the tool
                    if invocation.tool == "complete_python_task":
                        tool_input = invocation.tool_input
                        allowed_args = {k: v for k, v in tool_input.items() if k in ["graph_state", "python_code"]}
                        result = tool_func(**allowed_args)
                    else:
                        result = tool_func(**invocation.tool_input)
                    results.append((result, {}))  # Adjust as needed for your return type
                except Exception as e:
                    if return_exceptions:
                        results.append(e)
                    else:
                        raise
            else:
                results.append(Exception(f"Tool {invocation.tool} not found"))
        return results
import os


llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

tools = [complete_python_task]

model = llm.bind_tools(tools)
tool_executor = ToolExecutor(tools)

with open(os.path.join(os.path.dirname(__file__), "../prompts/main_prompt.md"), "r") as file:
    prompt = file.read()

chat_template = ChatPromptTemplate.from_messages([
    ("system", prompt),
    ("placeholder", "{messages}"),
])
model = chat_template | model

def create_data_summary(state: AgentState) -> str:
    summary = ""
    variables = []
    for d in state["input_data"]:
        # Handle both InputData objects and dictionaries (from serialization)
        if hasattr(d, 'variable_name'):
            # InputData object
            variable_name = d.variable_name
            description = d.data_description
        elif isinstance(d, dict) and 'variable_name' in d:
            # Dictionary from serialized InputData
            variable_name = d['variable_name']
            description = d.get('data_description', '')
        else:
            # Fallback for unexpected types
            variable_name = str(d)
            description = ''
        
        variables.append(variable_name)
        summary += f"\n\nVariable: {variable_name}\n"
        summary += f"Description: {description}"
    
    current_variables = state.get("current_variables") or {}
    remaining_variables = [v for v in current_variables if v not in variables]
    for v in remaining_variables:
        summary += f"\n\nVariable: {v}"
    return summary

def route_to_tools(
    state: AgentState,
) -> Literal["tools", "__end__"]:
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route back to the agent.
    """

    # Ensure messages is a list (in case it was serialized as a string)
    if isinstance(state.get("messages"), str):
        state["messages"] = []
    elif not isinstance(state.get("messages"), list):
        state["messages"] = []

    if messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"

def call_model(state: AgentState):
    # Ensure messages is a list (in case it was serialized as a string)
    if isinstance(state.get("messages"), str):
        state["messages"] = []
    elif not isinstance(state.get("messages"), list):
        state["messages"] = []

    current_data_template  = """The following data is available:\n{data_summary}"""
    current_data_message = HumanMessage(content=current_data_template.format(data_summary=create_data_summary(state)))
    state["messages"] = [current_data_message] + state["messages"]

    llm_outputs = model.invoke(state)
    print("llm_outputs: ", llm_outputs)

    return {"messages": [llm_outputs], "intermediate_outputs": [current_data_message.content]}

def call_tools(state: AgentState):
    # Ensure messages is a list (in case it was serialized as a string)
    if isinstance(state.get("messages"), str):
        state["messages"] = []
    elif not isinstance(state.get("messages"), list):
        state["messages"] = []

    last_message = state["messages"][-1]
    tool_invocations = []
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls'):
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = dict(tool_call["args"])
            # For complete_python_task, remove 'thought' from tool_args if present
            if tool_name == "complete_python_task":
                thought = tool_args.pop("thought", None)
                python_code = tool_args.get("python_code", "")
                if thought:
                    python_code = f"# Thought: {thought}\n{python_code}"
                tool_input = {"python_code": python_code, "graph_state": state}
            else:
                tool_input = {**tool_args, "graph_state": state}
            tool_invocations.append(ToolInvocation(tool=tool_name, tool_input=tool_input))

    responses = tool_executor.batch(tool_invocations, return_exceptions=True)
    tool_messages = []
    state_updates = {}

    for tc, response in zip(last_message.tool_calls, responses):
        if isinstance(response, Exception):
            raise response
        message, updates = response
        tool_messages.append(ToolMessage(
            content=str(message),
            name=tc["name"],
            tool_call_id=tc["id"]
        ))
        state_updates.update(updates)

    if 'messages' not in state_updates:
        state_updates["messages"] = []

    state_updates["messages"] = tool_messages 
    
    print("Tool node state:", state)
    return state_updates

