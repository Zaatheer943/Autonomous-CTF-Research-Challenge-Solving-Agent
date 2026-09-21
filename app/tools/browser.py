from typing import Dict, Any
from playwright.async_api import async_playwright, Browser
import sys
import os
import asyncio

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.base import BaseTool, ToolResult
from app.config import settings


class BrowserTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="browser",
            description="Interact with web pages using a headless browser. Navigate, click, fill forms, and extract text."
        )
        self.browser: Browser = None

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["navigate", "click", "fill", "get_text", "screenshot"],
                    "description": "Browser action to perform"
                },
                "url": {
                    "type": "string",
                    "description": "URL to navigate to (for navigate action)"
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector for click/fill/get_text actions"
                },
                "text": {
                    "type": "string",
                    "description": "Text to fill (for fill action)"
                }
            },
            "required": ["action"]
        }

    async def execute_async(self, parameters: Dict[str, Any]) -> ToolResult:
        try:
            action = parameters.get("action", "navigate")

            if not self.browser:
                playwright = await async_playwright().start()
                self.browser = await playwright.chromium.launch(headless=True)

            page = await self.browser.new_page()

            if action == "navigate":
                url = parameters.get("url", "")
                if not url.startswith("http"):
                    url = f"http://{settings.ctf_target_host}:{settings.ctf_target_port}{url}"

                await page.goto(url, timeout=settings.tool_timeout * 1000)
                output = f"Navigated to {url}\nPage title: {await page.title()}"

            elif action == "click":
                selector = parameters.get("selector", "")
                await page.click(selector, timeout=settings.tool_timeout * 1000)
                output = f"Clicked element: {selector}"

            elif action == "fill":
                selector = parameters.get("selector", "")
                text = parameters.get("text", "")
                await page.fill(selector, text, timeout=settings.tool_timeout * 1000)
                output = f"Filled {selector} with: {text}"

            elif action == "get_text":
                selector = parameters.get("selector", "")
                if selector:
                    element = await page.query_selector(selector)
                    text = await element.text_content() if element else ""
                else:
                    text = await page.inner_text("body")
                output = f"Text content: {text}"

            elif action == "screenshot":
                screenshot_bytes = await page.screenshot()
                output = f"Screenshot taken ({len(screenshot_bytes)} bytes)"

            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Unknown action: {action}"
                )

            await page.close()
            return ToolResult(success=True, output=output)

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        # Run async method in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.execute_async(parameters))

    async def close(self):
        if self.browser:
            await self.browser.close()
