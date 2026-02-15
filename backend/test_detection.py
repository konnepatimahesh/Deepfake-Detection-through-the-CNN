import requests
import os

BASE_URL = 'http://localhost:5000/api'

def test_detection_api():
    print("=" * 60)
    print("Testing Deepfake Detection API")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    
    if response.status_code != 200:
        print("❌ Login failed. Please create an admin user first.")
        return
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Login successful!")
    
    # Step 2: Get user stats
    print("\n2. Getting user stats...")
    response = requests.get(f'{BASE_URL}/detection/stats', headers=headers)
    print(f"Stats: {response.json()}")
    
    # Step 3: Get history
    print("\n3. Getting analysis history...")
    response = requests.get(f'{BASE_URL}/detection/history', headers=headers)
    print(f"History items: {response.json()['total']}")
    
    # Step 4: Admin - Get system stats
    print("\n4. Getting system stats (Admin)...")
    response = requests.get(f'{BASE_URL}/admin/stats', headers=headers)
    if response.status_code == 200:
        print(f"System Stats: {response.json()['stats']}")
    else:
        print(f"Status: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("API Testing Complete!")
    print("=" * 60)
    print("\nTo test file upload:")
    print("1. Use Postman or create a test image")
    print("2. POST to /api/detection/analyze/image")
    print("3. Include the image file in form-data as 'file'")
    print("4. Add Authorization header with Bearer token")

if __name__ == '__main__':
    test_detection_api()