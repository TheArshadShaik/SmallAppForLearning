import os
from app import create_app

# Default to production if not specified
env_name = os.getenv("FLASK_ENV", "production")
app = create_app(env_name)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    
    print(f"==================================================")
    print(f" Starting SmallApp Modular Server on {host}:{port}")
    print(f" Environment: {env_name} | Debug: {debug}")
    print(f" Home Gateway: http://{host}:{port}/")
    print(f"==================================================")
    
    app.run(host=host, port=port, debug=debug)
