import httpx
from typing import Dict, Any, List
import re
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

            # Handle form data - if data is a string, try to parse it
            if data and isinstance(data, str):
                # Try to parse as form data
                if '=' in data:
                    try:
                        parsed_data = {}
                        for pair in data.split('&'):
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                parsed_data[key] = value
                        data = parsed_data
                    except:
                        pass  # Keep as string if parsing fails

            with httpx.Client(timeout=settings.tool_timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    params=params
                )

            # Extract structured information from response
            structured_response = self._extract_structured_info(response)

            output = {
                "status_code": response.status_code,
                "url": str(response.url),
                "headers": dict(response.headers),
                "content_type": response.headers.get("content-type", ""),
                "structured": structured_response,
                "body": response.text
            }

            return ToolResult(
                success=True,
                output=str(output),
                metadata=output
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )

    def _extract_structured_info(self, response) -> Dict[str, Any]:
        """Extract structured information from HTTP response"""
        content_type = response.headers.get("content-type", "")
        body = response.text

        structured = {
            "links": self._extract_links(body),
            "forms": self._extract_forms(body),
            "text_content": body[:1000] if len(body) > 1000 else body,
            "potential_inputs": self._extract_input_fields(body),
            "has_login_form": self._has_login_form(body),
            "title": self._extract_title(body)
        }

        return structured

    def _extract_links(self, html: str) -> List[str]:
        """Extract links from HTML"""
        link_pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(link_pattern, html, re.IGNORECASE)
        # Filter out javascript links and anchors
        return [link for link in links if not link.startswith('javascript:') and not link.startswith('#')]

    def _extract_forms(self, html: str) -> List[Dict[str, Any]]:
        """Extract forms from HTML"""
        forms = []
        form_pattern = r'<form[^>]*action=["\']([^"\']*)["\'][^>]*method=["\']([^"\']*)["\'][^>]*>(.*?)</form>'
        form_matches = re.findall(form_pattern, html, re.IGNORECASE | re.DOTALL)

        for action, method, form_content in form_matches:
            fields = self._extract_input_fields(form_content)
            forms.append({
                "action": action,
                "method": method.upper(),
                "fields": fields
            })

        return forms

    def _extract_input_fields(self, html: str) -> List[str]:
        """Extract input field names from HTML"""
        input_pattern = r'<input[^>]*name=["\']([^"\']+)["\']'
        return re.findall(input_pattern, html, re.IGNORECASE)

    def _has_login_form(self, html: str) -> bool:
        """Check if the page has a login form"""
        login_indicators = [
            r'username',
            r'password',
            r'login',
            r'signin',
            r'auth'
        ]
        html_lower = html.lower()
        return any(re.search(indicator, html_lower) for indicator in login_indicators)

    def _extract_title(self, html: str) -> str:
        """Extract page title"""
        title_pattern = r'<title>(.*?)</title>'
        match = re.search(title_pattern, html, re.IGNORECASE)
        return match.group(1) if match else ""

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
