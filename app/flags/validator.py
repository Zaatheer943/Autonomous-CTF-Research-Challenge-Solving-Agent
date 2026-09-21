from typing import Dict, Optional
from app.flags.detector import FlagDetector


class FlagValidator:
    def __init__(self):
        self.detector = FlagDetector()
        # Challenge-specific validators could be added here
        self.challenge_validators: Dict[str, callable] = {}

    def validate(self, challenge_id: str, candidate_flag: str) -> bool:
        """Validate a candidate flag."""
        # First check format
        if not self.detector.validate_format(candidate_flag):
            return False

        # Check if there's a challenge-specific validator
        if challenge_id in self.challenge_validators:
            return self.challenge_validators[challenge_id](candidate_flag)

        # For MVP, accept any properly formatted flag
        # In production, this would call the CTF platform's validation API
        return True

    def register_validator(self, challenge_id: str, validator_func: callable):
        """Register a challenge-specific validator."""
        self.challenge_validators[challenge_id] = validator_func

    def unregister_validator(self, challenge_id: str):
        """Unregister a challenge-specific validator."""
        if challenge_id in self.challenge_validators:
            del self.challenge_validators[challenge_id]
