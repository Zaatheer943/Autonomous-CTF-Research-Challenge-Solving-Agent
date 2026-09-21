#!/usr/bin/env python3
"""
Run end-to-end tests without pytest (since server is already running)
"""
import sys
sys.path.append('.')

import httpx
from app.agent.health import TargetHealthChecker
from app.agent.controller import AgentController
from app.flags.detector import FlagDetector
from app.flags.validator import FlagValidator
import json
import glob

print("="*60)
print("Running End-to-End Tests")
print("="*60)

# Test 1: Target health check
print("\n[TEST 1] Target health check...")
checker = TargetHealthChecker("http://localhost:8000")
result = checker.check()
assert result["reachable"] == True, "Target should be reachable"
assert result["status_code"] == 200, "Target should return 200"
print("[PASS] Target health check")

# Test 2: Flag detection in response
print("\n[TEST 2] Flag detection in response...")
response = httpx.post(
    'http://localhost:8000/login',
    data={'username': "admin' OR '1'='1--", 'password': 'anything'}
)
detector = FlagDetector()
flag = detector.detect(response.text)
assert flag == 'CTF{demo_sql_injection_flag_12345}', f"Should detect flag, got: {flag}"
print("[PASS] Flag detection")

# Test 3: Flag validation
print("\n[TEST 3] Flag validation...")
validator = FlagValidator()
validator.register_challenge('demo-web', 'CTF{demo_sql_injection_flag_12345}')
assert validator.validate('demo-web', 'CTF{demo_sql_injection_flag_12345}') == True
assert validator.validate('demo-web', 'CTF{wrong_flag}') == False
print("[PASS] Flag validation")

# Test 4: Agent solve challenge
print("\n[TEST 4] Agent solve challenge...")
controller = AgentController(
    challenge_id='demo-web',
    challenge_description='Simple web login challenge with SQL injection vulnerability',
    target_url='http://localhost:8000'
)
result = controller.run()
assert result['status'].value == 'solved', f"Should be solved, got: {result['status']}"
assert result['flag'] == 'CTF{demo_sql_injection_flag_12345}', f"Should find correct flag, got: {result['flag']}"
assert result['steps'] <= 10, f"Should solve in reasonable steps, got: {result['steps']}"
print("[PASS] Agent solve challenge")

# Test 5: Trajectory persistence
print("\n[TEST 5] Trajectory persistence...")
trajectory_files = glob.glob(f"./data/trajectories/demo-web_{result['run_id']}.json")
assert len(trajectory_files) == 1, "Trajectory file should exist"
with open(trajectory_files[0], 'r') as f:
    trajectory_data = json.load(f)
assert trajectory_data['challenge_id'] == 'demo-web'
assert trajectory_data['run_id'] == result['run_id']
assert len(trajectory_data['trajectory']) > 0
print("[PASS] Trajectory persistence")

# Test 6: No hardcoded solution
print("\n[TEST 6] No hardcoded solution...")
with open(trajectory_files[0], 'r') as f:
    trajectory_data = json.load(f)
http_actions = [step for step in trajectory_data['trajectory'] if step['action'].get('action') == 'http_request']
assert len(http_actions) > 0, "Agent should make HTTP requests"
assert result['steps'] > 0, "Agent should take steps to solve"
print("[PASS] No hardcoded solution")

# Test 7: Knowledge retrieval influences actions
print("\n[TEST 7] Knowledge retrieval influences actions...")
with open(trajectory_files[0], 'r') as f:
    trajectory_data = json.load(f)
step_1 = trajectory_data['trajectory'][0]
assert len(step_1['knowledge_retrieved']) > 0, "Agent should retrieve knowledge"
knowledge_text = ' '.join(step_1['knowledge_retrieved']).lower()
# Check for various SQL injection related terms
sql_terms = ['sql', 'injection', 'authentication', 'bypass']
has_sql_knowledge = any(term in knowledge_text for term in sql_terms)
assert has_sql_knowledge, f"Should retrieve SQL-related knowledge, got: {knowledge_text[:200]}..."
print("[PASS] Knowledge retrieval influences actions")

# Test 8: Intelligent termination
print("\n[TEST 8] Intelligent termination...")
controller2 = AgentController(
    challenge_id='test',
    challenge_description='Test',
    target_url='http://nonexistent-target-12345.com'
)
result2 = controller2.run()
assert result2['status'].value == 'failed'
assert result2['steps'] == 0  # Should fail fast
assert 'error' in result2
print("[PASS] Intelligent termination")

print("\n" + "="*60)
print("ALL TESTS PASSED")
print("="*60)
