#!/usr/bin/env python3
"""
Test the exact CLI format requested by the user
"""
import sys
sys.path.append('.')

from app.cli import cli

# Simulate the exact command
print("Testing: ctf-agent solve --challenge demo-web --target http://localhost:8000")
print("="*60)

cli(['solve', '--challenge', 'demo-web', '--target', 'http://localhost:8000'])
