from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from openai import OpenAI
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> str:
        pass

    @abstractmethod
    def generate_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def generate(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            tools=tools if tools else None
        )
        return response.choices[0].message.content

    def generate_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message
        result = {
            "content": message.content,
            "tool_calls": []
        }

        if message.tool_calls:
            for tool_call in message.tool_calls:
                result["tool_calls"].append({
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                })

        return result


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai":
        try:
            provider = OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature
            )
            # Test the connection
            provider.generate([{"role": "user", "content": "test"}])
            return provider
        except Exception as e:
            print(f"OpenAI API error ({e}), falling back to mock provider")
            from app.agent.mock_llm import MockLLMProvider
            return MockLLMProvider()
    elif settings.llm_provider == "mock":
        from app.agent.mock_llm import MockLLMProvider
        return MockLLMProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
