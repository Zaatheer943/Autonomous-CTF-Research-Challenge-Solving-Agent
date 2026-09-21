#!/usr/bin/env python3
"""
End-to-end test for the demo challenge
"""
import pytest
import sys
import os
import time
import subprocess
import json
import httpx
import signal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.controller import AgentController
from app.agent.health import TargetHealthChecker
from app.flags.detector import FlagDetector
from app.flags.validator import FlagValidator


class TestDemoE2E:
    """End-to-end test for demo challenge"""

    @pytest.fixture(scope="class")
    def local_server(self):
        """Start the local demo challenge server"""
        # Start the local server in background
        server_process = subprocess.Popen(
            ["python", "docker/demo-challenge/local_server.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for server to start
        time.sleep(3)

        # Verify server is running
        max_retries = 10
        for i in range(max_retries):
            try:
                response = httpx.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    break
            except:
                if i < max_retries - 1:
                    time.sleep(1)
                else:
                    raise Exception("Server failed to start")

        yield server_process

        # Cleanup
        server_process.terminate()
        server_process.wait(timeout=5)

    def test_target_health_check(self, local_server):
        """Test that target health check works"""
        from app.agent.health import TargetHealthChecker

        checker = TargetHealthChecker("http://localhost:8000")
        result = checker.check()

        assert result["reachable"] == True
        assert result["status_code"] == 200

    def test_agent_solve_demo_challenge(self, local_server):
        """Test that agent can solve the demo challenge"""
        controller = AgentController(
            challenge_id='demo-web',
            challenge_description='Simple web login challenge with SQL injection vulnerability',
            target_url='http://localhost:8000'
        )

        result = controller.run()

        # Verify solution
        assert result['status'].value == 'solved'
        assert result['flag'] == 'CTF{demo_sql_injection_flag_12345}'
        assert result['steps'] <= 10  # Should solve in reasonable steps

    def test_flag_detection_in_response(self, local_server):
        """Test that flag can be detected from response"""
        response = httpx.post(
            'http://localhost:8000/login',
            data={'username': "admin' OR '1'='1--", 'password': 'anything'}
        )

        detector = FlagDetector()
        flag = detector.detect(response.text)

        assert flag == 'CTF{demo_sql_injection_flag_12345}'

    def test_flag_validation(self):
        """Test that flag validation works"""
        validator = FlagValidator()
        validator.register_challenge('demo-web', 'CTF{demo_sql_injection_flag_12345}')

        # Test valid flag
        assert validator.validate('demo-web', 'CTF{demo_sql_injection_flag_12345}') == True

        # Test invalid flag
        assert validator.validate('demo-web', 'CTF{wrong_flag}') == False

    def test_trajectory_persistence(self, local_server):
        """Test that trajectory is properly persisted"""
        controller = AgentController(
            challenge_id='demo-web',
            challenge_description='Simple web login challenge with SQL injection vulnerability',
            target_url='http://localhost:8000'
        )

        result = controller.run()

        # Check trajectory file exists
        import glob
        trajectory_files = glob.glob(f"./data/trajectories/demo-web_{result['run_id']}.json")
        assert len(trajectory_files) == 1

        # Load and verify trajectory
        with open(trajectory_files[0], 'r') as f:
            trajectory_data = json.load(f)

        assert trajectory_data['challenge_id'] == 'demo-web'
        assert trajectory_data['run_id'] == result['run_id']
        assert len(trajectory_data['trajectory']) > 0

    def test_no_hardcoded_solution(self, local_server):
        """Test that agent doesn't use hard-coded solution"""
        # This test verifies the agent actually interacts with the target
        controller = AgentController(
            challenge_id='demo-web',
            challenge_description='Simple web login challenge with SQL injection vulnerability',
            target_url='http://localhost:8000'
        )

        result = controller.run()

        # Verify the agent made HTTP requests
        trajectory = result['trajectory']
        http_actions = [step for step in trajectory if step['action'].get('action') == 'http_request']

        assert len(http_actions) > 0, "Agent should make HTTP requests"

        # Verify the agent didn't magically know the flag without requests
        assert result['steps'] > 0, "Agent should take steps to solve"

    def test_knowledge_retrieval_influences_actions(self, local_server):
        """Test that knowledge retrieval influences agent actions"""
        controller = AgentController(
            challenge_id='demo-web',
            challenge_description='Simple web login challenge with SQL injection vulnerability',
            target_url='http://localhost:8000'
        )

        result = controller.run()

        # Check that knowledge was retrieved
        trajectory = result['trajectory']
        step_1 = trajectory[0]

        assert len(step_1['knowledge_retrieved']) > 0, "Agent should retrieve knowledge"

        # Check that SQL injection writeup was retrieved
        knowledge_text = ' '.join(step_1['knowledge_retrieved'])
        assert 'SQL injection' in knowledge_text.lower(), "Should retrieve SQL injection knowledge"

    def test_intelligent_termination_conditions(self):
        """Test that agent has intelligent termination conditions"""
        from app.agent.controller import AgentController

        controller = AgentController(
            challenge_id='test',
            challenge_description='Test',
            target_url='http://nonexistent-target-12345.com'
        )

        result = controller.run()

        # Should fail fast with health check
        assert result['status'].value == 'failed'
        assert result['steps'] == 0  # Should not waste steps on unreachable target
        assert 'error' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
