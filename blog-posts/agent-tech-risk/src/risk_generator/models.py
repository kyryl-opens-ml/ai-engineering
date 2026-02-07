from typing import Literal
from pydantic import BaseModel


class CompanyProfile(BaseModel):
    name: str
    domain: Literal["fintech", "healthtech", "saas", "ecommerce", "devtools"]
    size: Literal["small", "medium", "large"]
    aws_accounts: int
    has_kubernetes: bool


# 10 diverse profiles for PE due diligence scenarios
PROFILE_PRESETS: dict[str, CompanyProfile] = {
    "payflow": CompanyProfile(
        name="PayFlow",
        domain="fintech",
        size="small",
        aws_accounts=3,
        has_kubernetes=False,
    ),
    "shipfast": CompanyProfile(
        name="ShipFast",
        domain="ecommerce",
        size="small",
        aws_accounts=2,
        has_kubernetes=False,
    ),
    "devpipe": CompanyProfile(
        name="DevPipe",
        domain="devtools",
        size="small",
        aws_accounts=2,
        has_kubernetes=False,
    ),
    "cloudsync": CompanyProfile(
        name="CloudSync",
        domain="saas",
        size="medium",
        aws_accounts=8,
        has_kubernetes=True,
    ),
    "insurenet": CompanyProfile(
        name="InsureNet",
        domain="fintech",
        size="medium",
        aws_accounts=6,
        has_kubernetes=False,
    ),
    "healthbridge": CompanyProfile(
        name="HealthBridge",
        domain="healthtech",
        size="medium",
        aws_accounts=5,
        has_kubernetes=False,
    ),
    "datavault": CompanyProfile(
        name="DataVault",
        domain="saas",
        size="medium",
        aws_accounts=7,
        has_kubernetes=True,
    ),
    "meddata": CompanyProfile(
        name="MedData",
        domain="healthtech",
        size="large",
        aws_accounts=15,
        has_kubernetes=True,
    ),
    "quickcart": CompanyProfile(
        name="QuickCart",
        domain="ecommerce",
        size="large",
        aws_accounts=12,
        has_kubernetes=True,
    ),
    "codeforge": CompanyProfile(
        name="CodeForge",
        domain="devtools",
        size="large",
        aws_accounts=10,
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
