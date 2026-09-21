import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.flags.detector import FlagDetector


def test_detect_standard_flag():
    detector = FlagDetector()
    text = "The flag is CTF{test_flag_123}"
    result = detector.detect(text)
    assert result == "CTF{test_flag_123}"


def test_detect_flag_uppercase():
    detector = FlagDetector()
    text = "Congratulations! FLAG{upper_case_flag}"
    result = detector.detect(text)
    assert result == "FLAG{upper_case_flag}"


def test_detect_flag_lowercase():
    detector = FlagDetector()
    text = "Found flag{lower_case_flag}"
    result = detector.detect(text)
    assert result == "flag{lower_case_flag}"


def test_detect_no_flag():
    detector = FlagDetector()
    text = "This is just normal text without any flags"
    result = detector.detect(text)
    assert result is None


def test_detect_multiple_flags():
    detector = FlagDetector()
    text = "First CTF{flag1} and then FLAG{flag2}"
    results = detector.detect_all(text)
    assert len(results) == 2
    assert "CTF{flag1}" in results
    assert "FLAG{flag2}" in results


def test_detect_malformed_flags():
    detector = FlagDetector()
    text = "CTF{incomplete CTF{another} malformed"
    results = detector.detect_all(text)
    # Should only find complete flags
    assert "CTF{another}" in results


def test_validate_format_valid():
    detector = FlagDetector()
    assert detector.validate_format("CTF{valid_flag}")
    assert detector.validate_format("FLAG{valid_flag}")
    assert detector.validate_format("flag{valid_flag}")


def test_validate_format_invalid():
    detector = FlagDetector()
    assert not detector.validate_format("not_a_flag")
    assert not detector.validate_format("CTFinvalid")
    assert not detector.validate_format("")
    assert not detector.validate_format(None)
