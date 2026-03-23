import uvicorn
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    print("Starting Subtext AI Server...")
    # Using 'src.main:app' assuming src/main.py has the FastAPI app instance named 'app'
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
