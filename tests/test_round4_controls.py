"""Validation tests for the Round-4 source-boundary experiment design.

Run: .venv/bin/python -I -m pytest tests/test_round4_controls.py -q
(or plain: .venv/bin/python -I tests/test_round4_controls.py)
These check EXPERIMENT INTEGRITY, not model behavior.
"""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("r4", os.path.join(HERE, "..", "scripts", "round4_source_boundary.py"))
r4 = importlib.util.module_from_spec(spec)
# avoid executing main; module only defines helpers at import
spec.loader.exec_module(r4)


def test_T_identical_in_U_and_R():
    tx = r4.make_texts("APPROVED-CASE017", r4.BENIGN_READS[0])
    # U's prompt is exactly T; R's record contains T verbatim.
    assert tx["U_PROMPT"] == tx["T"]
    assert tx["T"] in tx["R_RECORD"]
    # sha matches
    assert tx["T_SHA"] == hashlib.sha256(tx["T"].encode()).hexdigest()[:16]


def test_N_has_no_imperative_T():
    tx = r4.make_texts("APPROVED-CASE017", r4.BENIGN_READS[0])
    # Neutral record must NOT contain the imperative action text T.
    assert tx["T"] not in tx["N_RECORD"]
    # but should mention the field value (matched business info)
    assert "APPROVED-CASE017" in tx["N_RECORD"]


def test_R_payload_is_yaml_safe():
    # No double quotes (they break the YAML environment substitution).
    tx = r4.make_texts("APPROVED-CASE017", r4.BENIGN_READS[0])
    assert '"' not in tx["R_RECORD"] and '"' not in tx["N_RECORD"]


def test_vector_and_sentinel_defined():
    assert r4.VECTOR in ("injection_incoming_transaction", "injection_bill_text",
                         "injection_landloard_notice", "injection_address_change")
    assert r4.SUITE == "banking" and r4.MODEL


def test_raw_log_has_provenance_fields():
    # If a run exists, every row must carry traceable fields.
    raw = os.path.join(HERE, "..", "eval", "round4_source_boundary_raw.jsonl")
    if not os.path.exists(raw):
        return
    import json
    for line in open(raw):
        r = json.loads(line)
        for k in ("pair_id", "arm", "model", "T_sha16", "sentinel", "vector", "executed"):
            assert k in r, f"missing {k}"
        assert r["arm"] in ("U", "R", "N")
        # R/N source must be the tool turn, U the user turn
        assert r["prompt_role"] == ("user" if r["arm"] == "U" else "tool")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("all tests passed")
