import httpx
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


class TargetHealthChecker:
    def __init__(self, target_url: str):
        self.target_url = target_url

    def check(self) -> Dict[str, Any]:
        """Check if the target is reachable and healthy"""
        try:
            # Normalize URL
            if not self.target_url.startswith('http'):
                self.target_url = f"http://{self.target_url}"

            # Try to reach the target
            with httpx.Client(timeout=10) as client:
                response = client.get(self.target_url, timeout=5.0)

            return {
                "reachable": True,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "target": self.target_url
            }

        except httpx.TimeoutException:
            return {
                "reachable": False,
                "error": "Connection timeout",
                "target": self.target_url,
                "suggestions": [
                    "Check if docker compose is running",
                    "Verify the target URL is correct",
                    "Check if the target port is available"
                ]
            }
        except httpx.ConnectError:
            return {
                "reachable": False,
                "error": "Connection refused",
                "target": self.target_url,
                "suggestions": [
                    "Ensure the target server is running",
                    "Check if the target URL is correct",
                    "Verify port mapping in docker-compose"
                ]
            }
        except Exception as e:
            return {
                "reachable": False,
                "error": str(e),
                "target": self.target_url,
                "suggestions": [
                    "Check network connectivity",
                    "Verify the target URL format",
                    "Ensure the target service is running"
                ]
            }
