#!/usr/bin/env python3
"""
Simple test to verify API routes can be loaded
"""
import sys
sys.path.append('.')

try:
    from app.api.routes import router
    print("[OK] API routes loaded successfully")
    print(f"Routes: {[route.path for route in router.routes]}")
except Exception as e:
    print(f"[FAIL] API routes failed to load: {e}")
    sys.exit(1)

try:
    from app.config import settings
    print(f"[OK] Config loaded - API will run on {settings.api_host}:{settings.api_port}")
except Exception as e:
    print(f"[FAIL] Config failed to load: {e}")
    sys.exit(1)

print("\nAPI components are ready. You can start the server with:")
print("  python -m app.main")
print("  or")
print("  ctf-agent server")
