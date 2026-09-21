from typing import List, Dict, Any, Optional
from app.agent.llm import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing without API credits"""

    def __init__(self):
        self.call_count = 0

    def generate(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> str:
        self.call_count += 1
        return "Mock response for testing"

    def generate_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.call_count += 1

        # Simple mock response that attempts to solve SQL injection
        tool_names = [tool["function"]["name"] for tool in tools]

        # Try HTTP request first
        if "http_request" in tool_names:
            return {
                "content": """hypothesis: The challenge appears to be a web application with potential SQL injection vulnerability
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

        # Try browser if HTTP not available
        if "browser" in tool_names:
            return {
                "content": "Using browser to explore the application",
                "tool_calls": [
                    {
                        "id": "call_2",
                        "type": "function",
                        "function": {
                            "name": "browser",
                            "arguments": '{"action": "navigate", "url": "/"}'
                        }
                    }
                ]
            }

        return {
            "content": "Mock response - no suitable tool found",
            "tool_calls": []
        }
