import os
import sys
import uvicorn

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

if __name__ == "__main__":
    # Run the FastAPI application on all network interfaces (0.0.0.0) and port 8000
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload in development
        reload_dirs=["app"],  # Watch these directories for changes
        workers=1,    # You can increase this in production
        log_level="info"
    )
