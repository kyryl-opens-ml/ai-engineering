"""Tests for risk_generator package."""

import json
from pathlib import Path

import pytest
import yaml

from risk_generator.categories import (
    LOCALSTACK_FREE_CATEGORIES,
    RISK_CATEGORIES,
    get_category,
    list_categories,
)
from risk_generator.deployer import deploy_resources, get_field


# --- categories ---


def test_all_categories_have_required_fields():
    for code, cat in RISK_CATEGORIES.items():
        assert cat.code == code
        assert cat.name
        assert cat.description
        assert len(cat.aws_resources) > 0


def test_localstack_free_excludes_pro():
    pro = {"tr6", "tr7", "tr10", "tr11", "tr12"}
    for code in LOCALSTACK_FREE_CATEGORIES:
        assert code not in pro


def test_get_category_valid():
    cat = get_category("tr1")
    assert cat.code == "tr1"
    assert cat.name == "IAM Overprivilege"


def test_get_category_invalid():
    with pytest.raises(ValueError):
        get_category("tr999")


def test_list_categories_count():
    assert len(list_categories()) == 15


# --- get_field helper ---


def test_get_field_pascal():
    obj = {"PolicyName": "admin"}
    assert get_field(obj, "PolicyName", "policy_name") == "admin"


def test_get_field_snake():
    obj = {"policy_name": "admin"}
    assert get_field(obj, "PolicyName", "policy_name") == "admin"


def test_get_field_default():
    assert get_field({}, "PolicyName", "policy_name", default="x") == "x"


# --- deployer ---


def test_deploy_resources_empty():
    """Deploy empty state should return empty results."""
    # We can't connect to real LocalStack in unit tests,
    # but we can test with empty state (no boto calls).
    result = deploy_resources({}, "http://localhost:0")
    assert result == {"deployed": [], "failed": [], "skipped": []}


def test_deploy_resources_skips_rds():
    state = {"rds": {"instances": [{"DBInstanceIdentifier": "mydb"}]}}
    result = deploy_resources(state, "http://localhost:0")
    assert "rds:db:mydb" in result["skipped"]
    assert len(result["deployed"]) == 0


def test_deploy_resources_skips_eks():
    state = {"eks": {"clusters": [{"name": "mycluster"}]}}
    result = deploy_resources(state, "http://localhost:0")
    assert "eks:cluster:mycluster" in result["skipped"]


# --- case file validation ---


CASES_DIR = Path(__file__).parent.parent / "cases"


@pytest.mark.skipif(not CASES_DIR.exists(), reason="No cases directory")
def test_all_cases_have_required_files():
    cases = [d for d in CASES_DIR.iterdir() if d.is_dir()]
    assert len(cases) > 0
    for case_dir in cases:
        assert (case_dir / "aws_state.json").exists(), (
            f"{case_dir.name} missing aws_state.json"
        )
        assert (case_dir / "risks.yaml").exists(), f"{case_dir.name} missing risks.yaml"


@pytest.mark.skipif(not CASES_DIR.exists(), reason="No cases directory")
def test_all_cases_valid_json_yaml():
    for case_dir in CASES_DIR.iterdir():
        if not case_dir.is_dir():
            continue
        state_file = case_dir / "aws_state.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            assert isinstance(state, dict)

        risks_file = case_dir / "risks.yaml"
        if risks_file.exists():
            risks = yaml.safe_load(risks_file.read_text())
            assert isinstance(risks, (list, dict))
