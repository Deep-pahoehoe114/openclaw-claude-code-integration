from oeck.runtime_core.policy import PolicyEngine


def test_policy_engine_blocks_risky_command_in_review_mode():
    engine = PolicyEngine()

    decision = engine.evaluate("bash", {"command": "rm -rf /tmp/demo"}, mode="review")

    assert decision.action == "block"
    assert decision.risk == "HIGH"


def test_policy_engine_requires_confirmation_for_write():
    engine = PolicyEngine()

    decision = engine.evaluate("write", {"path": "notes.txt"}, mode="build")

    assert decision.action == "confirm"
    assert decision.risk == "MEDIUM"
