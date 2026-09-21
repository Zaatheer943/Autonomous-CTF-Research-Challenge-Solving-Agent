from typing import Dict, Optional, Callable
from app.flags.detector import FlagDetector
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FlagValidator:
    def __init__(self):
        self.detector = FlagDetector()
        # Challenge-specific validators and expected flags
        self.challenge_validators: Dict[str, Callable] = {}
        self.expected_flags: Dict[str, str] = {}

        # Register demo challenge
        self.register_challenge('demo-web', 'CTF{demo_sql_injection_flag_12345}')

    def register_challenge(self, challenge_id: str, expected_flag: str):
        """Register a challenge with its expected flag"""
        self.expected_flags[challenge_id] = expected_flag

    def validate(self, challenge_id: str, candidate_flag: str) -> bool:
        """Validate a candidate flag"""
        # First check format
        if not self.detector.validate_format(candidate_flag):
            return False

        # Check if there's a challenge-specific validator
        if challenge_id in self.challenge_validators:
            return self.challenge_validators[challenge_id](candidate_flag)

        # Check against expected flag if registered
        if challenge_id in self.expected_flags:
            expected = self.expected_flags[challenge_id]
            # Case-insensitive comparison
            return candidate_flag.lower() == expected.lower()

        # For MVP, accept any properly formatted flag
        # In production, this would call the CTF platform's validation API
        return True

    def register_validator(self, challenge_id: str, validator_func: Callable):
        """Register a challenge-specific validator"""
        self.challenge_validators[challenge_id] = validator_func

    def unregister_validator(self, challenge_id: str):
        """Unregister a challenge-specific validator"""
        if challenge_id in self.challenge_validators:
            del self.challenge_validators[challenge_id]
