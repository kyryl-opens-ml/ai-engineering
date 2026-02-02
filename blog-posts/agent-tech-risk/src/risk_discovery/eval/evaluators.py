from dataclasses import dataclass

from pydantic_evals.evaluators import Evaluator, EvaluatorContext

from risk_finder.models import ExpectedRisk, ScanResult


@dataclass
class CategoryRecallEvaluator(Evaluator):
    """Check if agent found risks in expected categories."""

    def evaluate(self, ctx: EvaluatorContext) -> float:
        expected: list[ExpectedRisk] = ctx.expected_output
        output: ScanResult = ctx.output

        if not expected:
            return 1.0

        # Get unique expected categories
        expected_categories = set(exp.category for exp in expected)
        found_categories = set(f.category for f in output.findings)

        matched = len(expected_categories & found_categories)
        return matched / len(expected_categories)


@dataclass
class RiskCountEvaluator(Evaluator):
    """Check ratio of found risks to expected risks."""

    def evaluate(self, ctx: EvaluatorContext) -> float:
        expected: list[ExpectedRisk] = ctx.expected_output
        output: ScanResult = ctx.output

        if not expected:
            return 1.0 if not output.findings else 0.0

        # Return ratio (capped at 1.0)
        return min(1.0, len(output.findings) / len(expected))
