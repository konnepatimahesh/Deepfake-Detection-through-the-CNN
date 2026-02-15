import requests
import json

BASE_URL = 'http://localhost:5000/api'

print("=" * 50)
print("Testing Deepfake Detection API")
print("=" * 50)

# Test 1: Signup
print("\n1. Testing Signup...")
signup_data = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123"
}
try:
    response = requests.post(f'{BASE_URL}/auth/signup', json=signup_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Login
print("\n2. Testing Login...")
login_data = {
    "username": "admin",
    "password": "admin123"
}
try:
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    # Save token for future requests
    if 'access_token' in result:
        token = result['access_token']
        print(f"\n✅ Token received: {token[:50]}...")
        
        # Test 3: Verify Token
        print("\n3. Testing Token Verification...")
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/auth/verify', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("API Testing Complete!")
print("=" * 50)