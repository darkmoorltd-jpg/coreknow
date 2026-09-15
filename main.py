"""Root entrypoint. Forwards to backend/main.py so Render works
regardless of the Root Directory setting or working directory.
"""
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_MAIN = os.path.join(HERE, "backend", "main.py")

if not os.path.exists(BACKEND_MAIN):
    raise RuntimeError("backend/main.py not found at " + BACKEND_MAIN)

# Load backend/main.py as a module
spec = importlib.util.spec_from_file_location("backend_main", BACKEND_MAIN)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Expose for uvicorn:  uvicorn main:app
app = mod.app