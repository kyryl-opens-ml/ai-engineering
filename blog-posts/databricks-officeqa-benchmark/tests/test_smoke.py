from databricks_officeqa_benchmark import hello


def test_hello() -> None:
    assert hello() == "Hello from databricks-officeqa-benchmark!"
