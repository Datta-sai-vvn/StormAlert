import requests
import sys

BASE_URL = "https://dv6280.online"
EMAIL = "datta24sai@gmail.com"
PASSWORD = "Datta@1234"

def register():
    print(f"Registering {EMAIL}...")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json={"email": EMAIL, "password": PASSWORD})
        if resp.status_code == 200:
            print("✅ Registration successful!")
            return True
        elif resp.status_code == 400 and "already exists" in resp.text:
            print("⚠️ User already exists.")
            return True
        else:
            print(f"❌ Registration failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = register()
    if not success:
        sys.exit(1)
