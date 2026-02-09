"""Tests for risk_discovery package."""

from risk_discovery.eval import _resource_match, _token_overlap, match_risks
from risk_discovery.models import RiskFinding, ScanResult


# --- models ---


def test_risk_finding():
    f = RiskFinding(
        category="tr1", resource="my-policy", issue="wildcard", severity="critical"
    )
    assert f.category == "tr1"
    assert f.severity == "critical"


def test_scan_result():
    r = ScanResult(findings=[])
    assert len(r.findings) == 0


# --- token overlap ---


def test_token_overlap_exact():
    assert _token_overlap("my-bucket", "my-bucket") == 1.0


def test_token_overlap_partial():
    assert _token_overlap("my-bucket-logs", "my-bucket") >= 0.5


def test_token_overlap_none():
    assert _token_overlap("alpha", "beta") == 0.0


def test_token_overlap_empty():
    assert _token_overlap("", "something") == 0.0


# --- resource match ---


def test_resource_match_exact():
    assert _resource_match("my-policy", "my-policy")


def test_resource_match_substring():
    assert _resource_match("my-sg", "my-sg (sg-abc123)")


def test_resource_match_reverse_substring():
    assert _resource_match("my-sg (sg-abc123)", "my-sg")


def test_resource_match_no_match():
    assert not _resource_match("alpha-bucket", "beta-policy")


# --- match_risks ---


def test_match_perfect():
    findings = [
        RiskFinding(
            category="tr1", resource="admin-policy", issue="x", severity="critical"
        ),
        RiskFinding(category="tr4", resource="open-sg", issue="x", severity="high"),
    ]
    gt = [
        {"category": "tr1", "resource": "admin-policy"},
        {"category": "tr4", "resource": "open-sg"},
    ]
    m = match_risks(findings, gt)
    assert m["tp"] == 2
    assert m["fp"] == 0
    assert m["fn"] == 0
    assert m["precision"] == 1.0
    assert m["recall"] == 1.0


def test_match_category_mismatch_resource_match():
    """Agent finds the right resource but uses different category (pass 2)."""
    findings = [
        RiskFinding(
            category="tr4", resource="ssh-wide-open", issue="x", severity="high"
        ),
    ]
    gt = [
        {"category": "tr1", "resource": "ssh-wide-open"},
    ]
    m = match_risks(findings, gt)
    assert m["tp"] == 1, "Should match on resource in pass 2"
    assert m["fn"] == 0


def test_match_no_overlap():
    findings = [
        RiskFinding(
            category="tr3", resource="some-bucket", issue="x", severity="medium"
        ),
    ]
    gt = [
        {"category": "tr1", "resource": "admin-policy"},
    ]
    m = match_risks(findings, gt)
    assert m["tp"] == 0
    assert m["fp"] == 1
    assert m["fn"] == 1


def test_match_empty_findings():
    m = match_risks([], [{"category": "tr1", "resource": "x"}])
    assert m["recall"] == 0.0


def test_match_empty_ground_truth():
    findings = [RiskFinding(category="tr1", resource="x", issue="x", severity="low")]
    m = match_risks(findings, [])
    assert m["precision"] == 0.0
    assert m["tp"] == 0
