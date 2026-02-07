import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("Starting debug...")
try:
    print("Attempting to import app...")
    from backend.app import create_app
    print("Import successful.")
    
    print("Creating app instance...")
    app = create_app()
    print("App created successfully.")
    
    print("Configuration loaded:")
    print(f"DB URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"DEBUG: {app.config.get('DEBUG')}")

except Exception as e:
    print(f"CAUGHT ERROR: {e}")
    import traceback
    traceback.print_exc()
