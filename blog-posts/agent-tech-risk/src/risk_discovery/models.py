from typing import Literal
from pydantic import BaseModel


class RiskFinding(BaseModel):
    category: str
    resource_arn: str
    severity: Literal["critical", "high", "medium", "low"]
    title: str
    description: str


class ScanResult(BaseModel):
    findings: list[RiskFinding]
    resources_scanned: int


class ExpectedRisk(BaseModel):
    category: str
    resource: str
    issue: str
    severity: str
