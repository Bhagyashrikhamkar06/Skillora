import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
os.chdir('backend')

print("=" * 50)
print("STARTING BACKEND SERVER")
print("=" * 50)

try:
    print("Step 1: Loading environment...")
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), '..', '.env'))
    print("✓ Environment loaded")
    
    print("\nStep 2: Importing Flask app...")
    from app import create_app
    print("✓ App imported")
    
    print("\nStep 3: Creating app instance...")
    app = create_app()
    print("✓ App created")
    
    print("\nStep 4: Starting server on 0.0.0.0:5000...")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
