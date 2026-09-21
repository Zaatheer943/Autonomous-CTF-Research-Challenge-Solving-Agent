import re
from typing import List, Optional
from app.config import settings


class FlagDetector:
    def __init__(self):
        self.patterns = settings.flag_patterns_list

    def detect(self, text: str) -> Optional[str]:
        """Detect flag patterns in text."""
        if not text:
            return None

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
