from databricks_officeqa_benchmark.metrics import (
    exact_match,
    f1_score,
    normalize_answer,
)


def test_normalize_answer() -> None:
    assert normalize_answer(" The U.S. Treasury, ") == "us treasury"


def test_exact_match() -> None:
    assert exact_match("The answer is 10.", "answer is 10") == 1.0
    assert exact_match("10", "11") == 0.0


def test_f1_score() -> None:
    assert f1_score("x y z", "x y z") == 1.0
    assert f1_score("x y z", "x y") == 2 * (2 / 2) * (2 / 3) / ((2 / 2) + (2 / 3))
    assert f1_score("x y z", "") == 0.0
