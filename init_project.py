import os
import shutil
import sys
from pathlib import Path

# Define project structure
PROJECT_ROOT = Path("/Users/zhaozewei/Project/value-analysist")
BACKEND_DIR = PROJECT_ROOT / "backend"
SRC_DIR = BACKEND_DIR / "src"

def create_structure():
    # 1. Create Directories
    dirs = [
        SRC_DIR / "core",
        SRC_DIR / "api",
        SRC_DIR / "db",
        SRC_DIR / "services",
        SRC_DIR / "models",
        SRC_DIR / "tools",
        SRC_DIR / "agents" / "business_analysis",
        SRC_DIR / "agents" / "mda_analysis",
        SRC_DIR / "agents" / "financial_analysis",
        SRC_DIR / "agents" / "competitor_analysis",
        SRC_DIR / "agents" / "valuation",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        # Add __init__.py
        (d / "__init__.py").touch()
        
    # 2. Add Yaml files for agents
    agent_dirs = [d for d in dirs if "agents" in str(d)]
    for d in agent_dirs:
        (d / "agents.yaml").touch()
        (d / "tasks.yaml").touch()

    print("Project structure created successfully.")

if __name__ == "__main__":
    create_structure()
