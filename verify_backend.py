import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def print_result(step, success, details=None):
    if success:
        print(f"✅ {step}")
    else:
        print(f"❌ {step}")
        if details:
            print(f"   Details: {details}")
        sys.exit(1)

def run_verification():
    print("Starting Backend Verification...")

    # 1. Register Recruiter
    recruiter_email = "verifier_recruiter@example.com"
    recruiter_pass = "Password123!"
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json={
            "email": recruiter_email,
            "password": recruiter_pass,
            "role": "recruiter",
            "full_name": "Verifier Recruiter"
        })
        if res.status_code == 201 or res.status_code == 409:
            print_result("Recruiter Registration", True)
        else:
            print_result("Recruiter Registration", False, res.text)
    except Exception as e:
        print_result("Recruiter Registration", False, str(e))

    # 2. Login Recruiter
    recruiter_token = None
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": recruiter_email,
            "password": recruiter_pass
        })
        if res.status_code == 200:
            recruiter_token = res.json()['access_token']
            print_result("Recruiter Login", True)
        else:
            print_result("Recruiter Login", False, res.text)
    except Exception as e:
        print_result("Recruiter Login", False, str(e))

    # 3. Post Job
    job_id = None
    try:
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        res = requests.post(f"{BASE_URL}/jobs/", headers=headers, json={
            "title": "Verification Engineer",
            "company_name": "Test Co",
            "description": "Testing the backend",
            "required_skills": ["Python", "Testing"]
        })
        if res.status_code == 201:
            job_id = res.json()['job']['id']
            print_result("Post Job", True, f"Job ID: {job_id}")
        else:
            print_result("Post Job", False, res.text)
    except Exception as e:
        print_result("Post Job", False, str(e))

    # 4. Register Seeker
    seeker_email = "verifier_seeker@example.com"
    seeker_pass = "Password123!"
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json={
            "email": seeker_email,
            "password": seeker_pass,
            "role": "job_seeker",
            "full_name": "Verifier Seeker"
        })
        if res.status_code == 201 or res.status_code == 409:
            print_result("Seeker Registration", True)
        else:
            print_result("Seeker Registration", False, res.text)
    except Exception as e:
        print_result("Seeker Registration", False, str(e))

    # 5. Login Seeker
    seeker_token = None
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": seeker_email,
            "password": seeker_pass
        })
        if res.status_code == 200:
            seeker_token = res.json()['access_token']
            print_result("Seeker Login", True)
        else:
            print_result("Seeker Login", False, res.text)
    except Exception as e:
        print_result("Seeker Login", False, str(e))

    # 6. Apply to Job
    try:
        headers = {"Authorization": f"Bearer {seeker_token}"}
        res = requests.post(f"{BASE_URL}/jobs/{job_id}/apply", headers=headers, json={
            "cover_letter": "I want to test this."
        })
        if res.status_code == 201:
            print_result("Apply to Job", True)
        elif res.status_code == 409:
            print_result("Apply to Job", True, "Already applied")
        else:
            print_result("Apply to Job", False, res.text)
    except Exception as e:
        print_result("Apply to Job", False, str(e))

    # 7. Get Applications (Recruiter)
    application_id = None
    try:
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        res = requests.get(f"{BASE_URL}/jobs/{job_id}/applications", headers=headers)
        if res.status_code == 200:
            apps = res.json()['applications']
            if len(apps) > 0:
                print_result("Get Applications", True, f"Found {len(apps)} applications")
                application_id = apps[0]['id']
            else:
                print_result("Get Applications", False, "No applications found")
        else:
            print_result("Get Applications", False, res.text)
    except Exception as e:
        print_result("Get Applications", False, str(e))

    # 8. Update Status (Recruiter)
    try:
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        res = requests.put(f"{BASE_URL}/jobs/applications/{application_id}/status", headers=headers, json={
            "status": "interview"
        })
        if res.status_code == 200:
            print_result("Update Status", True)
        else:
            print_result("Update Status", False, res.text)
    except Exception as e:
        print_result("Update Status", False, str(e))

if __name__ == "__main__":
    run_verification()
