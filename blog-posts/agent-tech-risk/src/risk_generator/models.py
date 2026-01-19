from typing import Literal
from pydantic import BaseModel


class CompanyProfile(BaseModel):
    name: str
    domain: Literal["fintech", "healthtech", "saas", "ecommerce", "devtools"]
    size: Literal["small", "medium", "large"]
    aws_accounts: int
    has_kubernetes: bool


PROFILE_PRESETS: dict[str, CompanyProfile] = {
    "small_fintech": CompanyProfile(
        name="PayFlow",
        domain="fintech",
        size="small",
        aws_accounts=3,
        has_kubernetes=False,
    ),
    "medium_saas": CompanyProfile(
        name="CloudSync",
        domain="saas",
        size="medium",
        aws_accounts=8,
        has_kubernetes=True,
    ),
    "large_healthtech": CompanyProfile(
        name="MedData",
        domain="healthtech",
        size="large",
        aws_accounts=15,
        has_kubernetes=True,
    ),
}


class RiskItem(BaseModel):
    category: str
    resource: str
    issue: str
    severity: Literal["low", "medium", "high", "critical"]
    why: str


class CaseMetadata(BaseModel):
    case_id: str
    profile: CompanyProfile
    risk_categories: list[str]
    risks: list[RiskItem]
