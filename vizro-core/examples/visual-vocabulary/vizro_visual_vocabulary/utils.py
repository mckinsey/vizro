"""Utilities for accessing chart examples."""

import inspect
import importlib
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple

def _get_code_templates() -> Dict[str, str]:
    """Extract the code templates from example charts.
    
    Returns:
        Dictionary mapping chart type names to their code templates.
    """
    templates = {}
    examples_dir = Path(__file__).parent / "pages" / "examples"
    
    for py_file in examples_dir.glob("*.py"):
        # Skip __init__.py and utilities
        if py_file.stem.startswith("_"):
            continue
            
        # Extract the chart type from filename
        chart_type = py_file.stem.replace("_", "-")
        
        # Read the file content
        with open(py_file, "r") as f:
            content = f.read()
            
        # Store the template
        templates[chart_type] = content
        
    return templates

def create_chart_type_enum() -> Enum:
    """Create an Enum of all available chart types.
    
    Returns:
        Enum with all chart types available in the visual vocabulary.
    """
    templates = _get_code_templates()
    
    # Create dynamic Enum class
    ChartType = Enum('ChartType', {
        k.replace('-', '_').upper(): k 
        for k in templates.keys()
    })
    
    return ChartType

def get_chart_groups() -> List[Tuple[str, List[str]]]:
    """Get all chart groups and their associated charts.
    
    Returns:
        List of tuples containing (group_name, [chart_types])
    """
    # Import the chart_groups module
    from . import chart_groups
    
    result = []
    for group in chart_groups.CHART_GROUPS:
        chart_types = [page.path.split('/')[-1] for page in group.pages]
        result.append((group.name, chart_types))
        
    return result 