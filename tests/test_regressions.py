"""Regression tests for signed audit chain, CSV conversion, inputs and API."""
import csv
from pathlib import Path

import pytest
from pydantic import ValidationError

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from cli import main, parse_csv_bool
from critical_values import lookup


def test_hmac_chain_detects_mutated_fields_and_protects_snapshot():
    trail = AuditTrail("synthetic-test-secret")
    trail.log("alice", "tester", "EVENT", {"a": 1})
    trail.log("bob", "tester", "EVENT", {"b": 2})
    assert trail.verify_integrity()
    snapshot = trail.get_trail()
    snapshot[0]["event_type"] = "MODIFIED"
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "MODIFIED"
    assert not trail.verify_integrity()


def test_hmac_detects_bad_signature():
    trail = AuditTrail("synthetic-test-secret")
    trail.log("alice", "tester", "EVENT", {"a": 1})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


@pytest.mark.parametrize("raw,expected", [
    ("true", True), ("YES", True), ("1", True),
    ("False", False), ("0", False), ("", False)
])
def test_csv_boolean_parser(raw, expected):
    assert parse_csv_bool(raw) is expected


def test_reject_unknown_csv_boolean():
    with pytest.raises(ValueError):
        parse_csv_bool("maybe")


def test_batch_false_flag_does_not_escalate(tmp_path: Path):
    inp, out = tmp_path / "tasks.csv", tmp_path / "results.csv"
    inp.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag\n"
        "T1,SYNTH-1,1,1,False\nT2,SYNTH-2,1,1,True\n",
        encoding="utf-8"
    )
    assert main(["batch", "-i", str(inp), "-o", str(out)]) == 0
    with out.open(newline="", encoding="utf-8") as f:
        results = list(csv.DictReader(f))
    assert results[0]["overall_urgency"] == "ROUTINE"
    assert results[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_reject_nonfinite_metrics(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="SYNTH", primary_metric=value)


def test_reject_phi_pattern_inside_attributes():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="T", target_identifier="SYNTH", primary_metric=1,
        attributes={"note": "MRN-123456"}
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


def test_unknown_lookup_remains_unmatched():
    result = lookup("zzzz_unrecognized_test")
    assert result["score"] == 0
    assert result["top_hit"] is None


def test_api_key_enforcement(monkeypatch):
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    monkeypatch.delenv("LAB_API_KEY", raising=False)
    assert client.get("/health").status_code == 200
    assert client.get("/api/audit/logs").status_code == 503
    monkeypatch.setenv("LAB_API_KEY", "synthetic-test-key")
    assert client.get("/api/audit/logs").status_code == 401
    assert client.get("/api/audit/logs", headers={"X-API-Key": "synthetic-test-key"}).status_code == 200
