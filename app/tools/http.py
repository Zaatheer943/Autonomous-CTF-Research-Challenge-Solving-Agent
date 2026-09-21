import httpx
from typing import Dict, Any
import sys
import os
import ipaddress

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.base import BaseTool, ToolResult
from app.config import settings


class HTTPTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="http_request",
            description="Make HTTP requests to the target. Supports GET, POST, PUT, DELETE methods."
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE"],
                    "description": "HTTP method to use"
                },
                "url": {
                    "type": "string",
                    "description": "URL to request (relative to target or full URL)"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP headers to send"
                },
                "data": {
                    "type": "string",
                    "description": "Request body data"
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters"
                }
            },
            "required": ["method", "url"]
        }

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        try:
            method = parameters.get("method", "GET")
            url = parameters.get("url", "")

            # Validate URL is within allowed networks
            if not self._is_url_allowed(url):
                return ToolResult(
                    success=False,
                    output="",
                    error=f"URL {url} is not in allowed networks"
                )

            # If relative URL, prepend target
            if not url.startswith("http"):
                url = f"http://{settings.ctf_target_host}:{settings.ctf_target_port}{url}"

            headers = parameters.get("headers", {})
            data = parameters.get("data")
            params = parameters.get("params")

            with httpx.Client(timeout=settings.tool_timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    content=data,
                    params=params
                )

            output = f"Status: {response.status_code}\n"
            output += f"Headers: {dict(response.headers)}\n"
            output += f"Body: {response.text[:1000]}"

            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "url": str(response.url)
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )

    def _is_url_allowed(self, url: str) -> bool:
        # If relative URL, it's allowed
        if not url.startswith("http"):
            return True

        # Extract hostname from URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            hostname = parsed.hostname

            if not hostname:
                return False

            # Check against allowed networks
            for network in settings.allowed_networks_list:
                try:
                    # Check if hostname is in allowed network
                    if hostname in ["localhost", "127.0.0.1"]:
                        return True

                    # Check IP range
                    if "/" in network:
                        net = ipaddress.ip_network(network)
                        try:
                            ip = ipaddress.ip_address(hostname)
                            if ip in net:
                                return True
                        except ValueError:
                            pass
                    elif hostname == network:
                        return True
                except ValueError:
                    pass

            return False
        except Exception:
            return False
