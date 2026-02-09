"""Data models for risk discovery."""

from typing import Literal

from pydantic import BaseModel


class RiskFinding(BaseModel):
    category: str  # e.g. tr1, tr3, tr4
    resource: str  # resource name (policy name, bucket name, sg name, etc.)
    issue: str  # what's wrong
    severity: Literal["critical", "high", "medium", "low"]


class ScanResult(BaseModel):
    findings: list[RiskFinding]
