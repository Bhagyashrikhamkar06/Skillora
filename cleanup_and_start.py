"""
Cleanup script to kill all running Python processes and start the servers cleanly
"""
import subprocess
import time
import sys

def kill_processes_on_ports():
    """Kill processes running on ports 5000 and 8000"""
    ports = [5000, 8000]
    
    for port in ports:
        try:
            # Find process using the port
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                pids = set()
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        pids.add(pid)
                
                # Kill each PID
                for pid in pids:
                    try:
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                        print(f"✓ Killed process {pid} on port {port}")
                    except Exception as e:
                        print(f"✗ Could not kill PID {pid}: {e}")
            else:
                print(f"✓ Port {port} is free")
                
        except Exception as e:
            print(f"Error checking port {port}: {e}")

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting backend server on port 5000...")
    subprocess.Popen(
        [sys.executable, "backend/app.py"],
        cwd=r"C:\Users\bhagy\OneDrive\Desktop\Skillora"
    )
    time.sleep(3)
    print("✓ Backend started")

def start_frontend():
    """Start the frontend server"""
    print("\n🚀 Starting frontend server on port 8000...")
    subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000"],
        cwd=r"C:\Users\bhagy\OneDrive\Desktop\Skillora\frontend"
    )
    time.sleep(2)
    print("✓ Frontend started")

def check_health():
    """Check if backend is responding"""
    print("\n🔍 Checking backend health...")
    time.sleep(2)
    try:
        result = subprocess.run(
            'curl http://localhost:5000/api/health',
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ Backend is healthy!")
            print(f"Response: {result.stdout}")
        else:
            print("✗ Backend health check failed")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"✗ Health check error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("SKILLORA - Server Cleanup & Startup")
    print("=" * 60)
    
    print("\n📋 Step 1: Killing existing processes on ports 5000 and 8000...")
    kill_processes_on_ports()
    
    print("\n📋 Step 2: Starting servers...")
    start_backend()
    start_frontend()
    
    print("\n📋 Step 3: Health check...")
    check_health()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\n📍 Access your application:")
    print("   Frontend: http://localhost:8000")
    print("   Backend:  http://localhost:5000")
    print("\nPress Ctrl+C to stop all servers")
    print("=" * 60)
    
    # Keep script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        kill_processes_on_ports()
        print("✓ All servers stopped")
