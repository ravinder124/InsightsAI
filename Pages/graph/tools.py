from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

from langchain_core.messages import AIMessage
from typing import Tuple
import sys
from io import StringIO
import os
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import pandas as pd
import sklearn
import json
from datetime import datetime, date
import numpy as np
from pydantic import BaseModel


repl = PythonREPL()

persistent_vars = {}

# Custom JSON encoder to handle pandas Period objects and other non-serializable types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'freq'):  # pandas Period objects
            return str(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super().default(obj)

def serialize_variable(var):
    """Safely serialize a variable, converting non-serializable types to strings"""
    try:
        # Handle pandas Period objects specifically
        if hasattr(var, 'freq') and hasattr(var, 'year'):
            return str(var)
        
        # Handle pandas Series and DataFrames with Period objects
        if isinstance(var, pd.Series):
            # Convert Period objects in Series to strings
            if var.dtype == 'object':
                return var.astype(str)
            return var
        
        if isinstance(var, pd.DataFrame):
            # Convert Period objects in DataFrame to strings
            for col in var.columns:
                if var[col].dtype == 'object':
                    var[col] = var[col].astype(str)
            return var
        
        # Try to serialize to JSON to test if it's serializable
        json.dumps(var, cls=CustomJSONEncoder)
        return var
    except (TypeError, ValueError):
        # If not serializable, convert to string representation
        return str(var)

def clean_persistent_vars(vars_dict):
    """Clean persistent variables to ensure they are JSON serializable"""
    cleaned = {}
    for key, value in vars_dict.items():
        if key not in globals():  # Only process user-defined variables
            try:
                cleaned[key] = serialize_variable(value)
            except Exception:
                # If all else fails, convert to string
                cleaned[key] = str(value)
    return cleaned

plotly_saving_code = """import pickle
import uuid
import plotly

for figure in plotly_figures:
    pickle_filename = f"images/plotly_figures/pickle/{uuid.uuid4()}.pickle"
    with open(pickle_filename, 'wb') as f:
        pickle.dump(figure, f)
"""

class PythonTaskInput(BaseModel):
    thought: str = ""
    python_code: str = ""

@tool
def complete_python_task(
        thought: str = "", python_code: str = "", graph_state: dict = None, **kwargs
) -> Tuple[str, dict]:
    """Completes a python task

    Args:
        thought: Internal thought about the next action to be taken, and the reasoning behind it. This should be formatted in MARKDOWN and be high quality.
        python_code: Python code to be executed to perform analyses, create a new dataset or create a visualization.
    """
    current_variables = graph_state.get("current_variables") or {}
    for input_dataset in graph_state["input_data"]:
        # Handle both InputData objects and dictionaries (from serialization)
        if hasattr(input_dataset, 'variable_name'):
            # InputData object
            variable_name = input_dataset.variable_name
            data_path = input_dataset.data_path
        elif isinstance(input_dataset, dict) and 'variable_name' in input_dataset:
            # Dictionary from serialized InputData
            variable_name = input_dataset['variable_name']
            data_path = input_dataset['data_path']
        else:
            # Skip if we can't determine the variable name
            continue
            
        if variable_name not in current_variables:
            current_variables[variable_name] = pd.read_csv(data_path)
    if not os.path.exists("images/plotly_figures/pickle"):
        os.makedirs("images/plotly_figures/pickle")

    current_image_pickle_files = os.listdir("images/plotly_figures/pickle")
    try:
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Execute the code and capture the result
        exec_globals = globals().copy()
        exec_globals.update(persistent_vars)
        exec_globals.update(current_variables)
        exec_globals.update({"plotly_figures": []})


        exec(python_code, exec_globals)
        
        # Clean the persistent variables to ensure they are JSON serializable
        new_persistent_vars = {k: v for k, v in exec_globals.items() if k not in globals()}
        cleaned_persistent_vars = clean_persistent_vars(new_persistent_vars)
        persistent_vars.update(cleaned_persistent_vars)

        # Get the captured stdout
        output = sys.stdout.getvalue()

        # Restore stdout
        sys.stdout = old_stdout

        updated_state = {
            "intermediate_outputs": [{"thought": thought, "code": python_code, "output": output}],
            "current_variables": cleaned_persistent_vars
        }

        if 'plotly_figures' in exec_globals:
            exec(plotly_saving_code, exec_globals)
            # Check if any images were created
            new_image_folder_contents = os.listdir("images/plotly_figures/pickle")
            new_image_files = [file for file in new_image_folder_contents if file not in current_image_pickle_files]
            if new_image_files:
                updated_state["output_image_paths"] = new_image_files
            
            persistent_vars["plotly_figures"] = []

        return output, updated_state
    except Exception as e:
        return str(e), {"intermediate_outputs": [{"thought": thought, "code": python_code, "output": str(e)}]}