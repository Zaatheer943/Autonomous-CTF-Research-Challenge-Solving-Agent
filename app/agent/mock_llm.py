from typing import List, Dict, Any, Optional
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.llm import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing without API credits"""

    def __init__(self):
        self.call_count = 0
        self.step_number = 0
        self.flag_found = False

    def generate(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> str:
        self.call_count += 1
        return "Mock response for testing"

    def generate_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.call_count += 1
        self.step_number += 1

        # If flag was already found, stop
        if self.flag_found:
            return {
                "content": "Flag already found, challenge solved",
                "tool_calls": []
            }

        # Progressive solving strategy - exact working sequence
        if self.step_number == 1:
            # Step 1: Initial reconnaissance
            return {
                "content": """hypothesis: The challenge appears to be a web application that may have vulnerabilities
reason: I should start by exploring the target with HTTP requests to understand the application structure
action: http_request
parameters: {"method": "GET", "url": "/"}
next_step: Analyze the response to identify login forms or input fields""",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "http_request",
                            "arguments": '{"method": "GET", "url": "/"}'
                        }
                    }
                ]
            }

        elif self.step_number == 2:
            # Step 2: SQL injection with exact working payload
            return {
                "content": """hypothesis: The login form appears to be vulnerable to SQL injection based on the retrieved knowledge
reason: The writeups suggest testing authentication bypass with SQL injection payloads like ' OR '1'='1
action: http_request
parameters: {"method": "POST", "url": "/login", "data": {"username": "admin' OR '1'='1--", "password": "anything"}}
next_step: Analyze the response to see if authentication was bypassed and flag is retrieved""",
                "tool_calls": [
                    {
                        "id": "call_2",
                        "type": "function",
                        "function": {
                            "name": "http_request",
                            "arguments": '{"method": "POST", "url": "/login", "data": {"username": "admin\' OR \'1\'=\'1--", "password": "anything"}}'
                        }
                    }
                ]
            }

        else:
            # Default: stop trying if we've reached step 3 without success
            return {
                "content": "Unable to solve challenge with current approach",
                "tool_calls": []
            }

    def _extract_state(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract state information from messages"""
        state = {
            "step": 0,
            "observations": [],
            "hypotheses": []
        }

        for message in messages:
            if message.get("role") == "user":
                content = message.get("content", "")
                if "Step:" in content:
                    try:
                        state["step"] = int(content.split("Step:")[1].split(":")[0].strip())
                    except:
                        pass

        return state
