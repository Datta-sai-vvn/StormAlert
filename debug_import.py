import sys
import os

print("Current CWD:", os.getcwd())
print("Sys Path:", sys.path)

try:
    from backend.main import app
    print("Successfully imported app")
except Exception as e:
    print(f"Failed to import app: {e}")
    import traceback
    traceback.print_exc()
