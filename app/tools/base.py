from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ToolResult(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseTool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments_schema": self.get_schema()
        }
