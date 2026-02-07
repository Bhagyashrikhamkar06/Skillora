import requests
import time
import os

# Create a large dummy PDF file (> 5MB)
# 6MB = 6 * 1024 * 1024 bytes
size = 6 * 1024 * 1024
with open('large_resume.pdf', 'wb') as f:
    f.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length ' + str(size).encode() + b'\n>>\nstream\n' + b' ' * size + b'\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000236 00000 n\n0000000323 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n417\n%%EOF')

BASE_URL = 'http://localhost:5000/api'
email = f'testuser_large_{int(time.time())}@example.com'
password = 'TestPassword123!'

try:
    # 1. Register with correct fields
    print(f"Registering {email}...")
    reg_resp = requests.post(f'{BASE_URL}/auth/register', json={
        'full_name': 'Test User',
        'email': email,
        'password': password,
        'role': 'job_seeker'
    })
    
    if reg_resp.status_code not in [201, 409]: # 409 if already exists
        print(f"Registration failed: {reg_resp.status_code} - {reg_resp.text}")
        if reg_resp.status_code != 409:
            exit(1)

    # 2. Login
    print("Logging in...")
    login_resp = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': password})
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code} - {login_resp.text}")
        exit(1)
    
    token = login_resp.json()['access_token']
    print("Login successful.")

    # 3. Upload
    print("Uploading large resume (6MB)...")
    with open('large_resume.pdf', 'rb') as f:
        files = {'file': ('large_resume.pdf', f, 'application/pdf')}
        headers = {'Authorization': f'Bearer {token}'}
        
        # Timeout to detect hang
        resp = requests.post(f'{BASE_URL}/resume/upload', files=files, headers=headers, timeout=30)
        
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")

except Exception as e:
    print(f"An error occurred: {e}")
