#!/usr/bin/env python3
"""
Test script to verify CTF Agent components are working correctly.
"""
import sys
sys.path.append('.')

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    from app.config import settings
    print(f"[OK] API Key configured: {bool(settings.openai_api_key)}")
    print(f"[OK] Provider: {settings.llm_provider}")
    print(f"[OK] Model: {settings.llm_model}")
    print(f"[OK] Max steps: {settings.max_agent_steps}")
    return True

def test_flag_detector():
    """Test flag detection"""
    print("\nTesting flag detector...")
    from app.flags.detector import FlagDetector
    detector = FlagDetector()

    test_cases = [
        ("CTF{test_flag}", "CTF{test_flag}"),
        ("FLAG{upper}", "FLAG{upper}"),
        ("flag{lower}", "flag{lower}"),
        ("no flag here", None),
        ("CTF{first} and FLAG{second}", ["CTF{first}", "FLAG{second}"])
    ]

    for text, expected in test_cases:
        if isinstance(expected, list):
            result = detector.detect_all(text)
            assert set(result) == set(expected), f"Expected {expected}, got {result}"
        else:
            result = detector.detect(text)
            assert result == expected, f"Expected {expected}, got {result}"

    print("[OK] Flag detection working correctly")
    return True

def test_tool_security():
    """Test tool security features"""
    print("\nTesting tool security...")
    from app.tools.http import HTTPTool
    from app.tools.files import FilesTool

    http_tool = HTTPTool()
    files_tool = FilesTool()

    # Test HTTP tool blocks unauthorized URLs
    result = http_tool.execute({'method': 'GET', 'url': 'http://evil.com'})
    assert not result.success, "Should block evil.com"
    assert "not in allowed networks" in result.error
    print("[OK] HTTP tool blocks unauthorized URLs")

    # Test files tool blocks unauthorized paths
    result = files_tool.execute({'action': 'read', 'path': 'C:\\Windows\\System32'})
    assert not result.success, "Should block system paths"
    assert "not allowed" in result.error
    print("[OK] Files tool blocks unauthorized paths")

    return True

def test_agent_state():
    """Test agent state management"""
    print("\nTesting agent state...")
    from app.agent.state import AgentState

    state = AgentState(challenge_id='test')
    state.add_observation('Test observation')
    state.add_hypothesis('Test hypothesis')
    state.increment_step()
    state.mark_running()

    assert state.current_step == 1
    assert len(state.observations) == 1
    assert len(state.hypotheses) == 1
    assert state.status.value == 'running'

    print("[OK] Agent state management working")
    return True

def test_knowledge_base():
    """Test knowledge base components"""
    print("\nTesting knowledge base...")
    from app.knowledge.schemas import WriteupMetadata, WriteupChunk

    metadata = WriteupMetadata(
        title="Test Writeup",
        category="web",
        techniques=["sqli"],
        difficulty="easy"
    )

    chunk = WriteupChunk(
        content="Test content about SQL injection",
        metadata=metadata,
        source_file="test.md",
        chunk_id="test_0"
    )

    assert chunk.metadata.title == "Test Writeup"
    assert chunk.metadata.category == "web"
    print("[OK] Knowledge base schemas working")
    return True

def main():
    """Run all tests"""
    print("="*60)
    print("CTF Agent Component Tests")
    print("="*60)

    tests = [
        test_config,
        test_flag_detector,
        test_tool_security,
        test_agent_state,
        test_knowledge_base
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
