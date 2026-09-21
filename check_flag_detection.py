#!/usr/bin/env python3
"""
Test flag detection on the actual response
"""
import sys
sys.path.append('.')

import httpx
from app.flags.detector import FlagDetector

# Get the actual response with the working payload
response = httpx.post('http://localhost:8000/login', data={'username': "admin' OR '1'='1--", 'password': 'anything'})

print("Response text preview:", response.text[:300])
print("\nContains CTF{:", "CTF{" in response.text)

# Test flag detection
detector = FlagDetector()
flag = detector.detect(response.text)
print(f"Flag detected from text: {flag}")

# Test with structured data
structured_data = {
    "status_code": 200,
    "structured": {
        "text_content": response.text
    }
}

flag_structured = detector.detect(structured_data)
print(f"Flag detected from structured: {flag_structured}")

# Test detect_all
flags = detector.detect_all(response.text)
print(f"All flags detected: {flags}")
