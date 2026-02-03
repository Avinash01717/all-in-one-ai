
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_registration(password, expected_status, description):
    print(f"Testing registration with password: '{password}' ({description})...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": f"test_{password}@example.com",
            "password": password,
            "full_name": "Test User"
        })
        if response.status_code == expected_status:
            print(f"✅ Success: Got expected status {response.status_code}")
            if response.status_code == 400:
                print(f"   Message: {response.json()['detail']}")
        else:
            print(f"❌ Failure: Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print("-" * 20)

def run_tests():
    # 1. Too short
    test_registration("Weak1!", 400, "Too short < 9")
    
    # 2. No Capital
    test_registration("weakpassword1!", 400, "No Uppercase")

    # 3. No Number
    test_registration("Weakpassword!", 400, "No Number")

    # 4. No Symbol
    test_registration("Weakpassword1", 400, "No Symbol")

    # 5. Valid Password
    test_registration("StrongPass1!", 200, "Valid Password")

if __name__ == "__main__":
    run_tests()
