import re
from typing import List, Optional
from app.config import settings
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FlagDetector:
    def __init__(self):
        self.patterns = settings.flag_patterns_list

    def detect(self, text: str) -> Optional[str]:
        """Detect flag patterns in text."""
        if not text:
            return None

        # Handle both string and dict inputs
        if isinstance(text, dict):
            # Extract text from structured data
            text = self._extract_text_from_structured(text)

        for pattern in self.patterns:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Return the first match
                    return matches[0]
            except re.error:
                continue

        return None

    def detect_all(self, text: str) -> List[str]:
        """Detect all flag patterns in text."""
        if not text:
            return []

        # Handle both string and dict inputs
        if isinstance(text, dict):
            text = self._extract_text_from_structured(text)

        flags = []
        for pattern in self.patterns:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE)
                flags.extend(matches)
            except re.error:
                continue

        return list(set(flags))  # Remove duplicates

    def validate_format(self, flag: str) -> bool:
        """Validate that a flag matches at least one pattern."""
        if not flag:
            return False

        for pattern in self.patterns:
            try:
                if re.fullmatch(pattern, flag, re.IGNORECASE):
                    return True
            except re.error:
                continue

        return False

    def _extract_text_from_structured(self, data: dict) -> str:
        """Extract text from structured data."""
        text_parts = []

        # Prioritize specific fields that are likely to contain flags
        if 'text_content' in data:
            text_parts.append(data['text_content'])
        if 'body' in data:
            text_parts.append(data['body'])
        if 'content' in data:
            text_parts.append(data['content'])

        # Add all other string values
        for key, value in data.items():
            if key not in ['text_content', 'body', 'content']:  # Skip already processed
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, dict):
                    text_parts.append(self._extract_text_from_structured(value))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            text_parts.append(item)

        return " ".join(text_parts)
