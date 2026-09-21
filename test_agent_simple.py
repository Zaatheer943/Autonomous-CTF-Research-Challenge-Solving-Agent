#!/usr/bin/env python3
"""
Simple test of the agent using the CLI directly
"""
import sys
sys.path.append('.')

from app.agent.controller import AgentController
import json

print("Starting agent test...")
controller = AgentController('demo-web', 'Simple web login challenge with SQL injection vulnerability', 'http://localhost:8000')
result = controller.run()

print("\n" + "="*60)
print("AGENT RUN RESULTS")
print("="*60)
print(f"Challenge: {result['challenge_id']}")
print(f"Status: {result['status']}")
print(f"Steps: {result['steps']}")
print(f"Flag: {result.get('flag', 'None')}")

if result['trajectory']:
    print(f"\nFirst 3 steps:")
    for step in result['trajectory'][:3]:
        print(f"\nStep {step['step']}:")
        print(f"  Hypothesis: {step['hypothesis']}")
        print(f"  Action: {step['action']}")
        print(f"  Result: {step['result'][:100]}...")

print("\n" + "="*60)
