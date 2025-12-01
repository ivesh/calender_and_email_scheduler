import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

try:
    from app.jarvis_adk.agent import root_agent
    print("Successfully imported root_agent")
except Exception as e:
    print(f"Failed to import root_agent: {e}")
    import traceback
    traceback.print_exc()
