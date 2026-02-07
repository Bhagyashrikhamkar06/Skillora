import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app import create_app

if __name__ == '__main__':
    print("Initializing app...")
    app = create_app()
    print("App initialized. Starting server on 0.0.0.0:5000...")
    app.run(debug=False, host='0.0.0.0', port=5000)
