"""
Quick diagnostic script to check server status
"""
import subprocess
import requests
import sys

def check_port(port):
    """Check what's running on a port"""
    print(f"\n{'='*60}")
    print(f"Checking Port {port}")
    print('='*60)
    
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.stdout:
            print("✓ Port is in use:")
            print(result.stdout)
        else:
            print(f"✗ Port {port} is FREE (nothing listening)")
            
    except Exception as e:
        print(f"Error: {e}")

def test_backend():
    """Test if backend is responding"""
    print(f"\n{'='*60}")
    print("Testing Backend API")
    print('='*60)
    
    endpoints = [
        'http://localhost:5000/api/health',
        'http://127.0.0.1:5000/api/health',
    ]
    
    for url in endpoints:
        try:
            print(f"\nTrying: {url}")
            response = requests.get(url, timeout=3)
            print(f"✓ SUCCESS! Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return True
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection refused")
        except requests.exceptions.Timeout:
            print(f"✗ Request timed out")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    return False

def test_frontend():
    """Test if frontend is responding"""
    print(f"\n{'='*60}")
    print("Testing Frontend Server")
    print('='*60)
    
    try:
        response = requests.get('http://localhost:8000', timeout=3)
        print(f"✓ Frontend is responding! Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ Frontend not responding: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SKILLORA SERVER DIAGNOSTICS")
    print("="*60)
    
    # Check ports
    check_port(5000)
    check_port(8000)
    
    # Test endpoints
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Backend (port 5000):  {'✓ WORKING' if backend_ok else '✗ NOT WORKING'}")
    print(f"Frontend (port 8000): {'✓ WORKING' if frontend_ok else '✗ NOT WORKING'}")
    
    if not backend_ok or not frontend_ok:
        print("\n⚠️  RECOMMENDATION:")
        print("Kill all Python processes and restart servers cleanly:")
        print("1. Close all terminal windows")
        print("2. Open 2 new terminals")
        print("3. Terminal 1: cd backend && python app.py")
        print("4. Terminal 2: cd frontend && python -m http.server 8000")
    else:
        print("\n✅ All servers are working!")
        print("Frontend: http://localhost:8000")
        print("Backend:  http://localhost:5000")
    
    print('='*60)
