import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "True") == "True"
    
    print(f"Starting {os.environ.get("APP_NAME", 'Cerberus')} on {host}:{port} | Debug={debug}")
    app.run(debug=debug, host=host, port=port)