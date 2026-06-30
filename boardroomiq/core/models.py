from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentFinding:
    agent: str
    claim: str
    evidence: list[str]
    confidence: int
    metrics: dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""
    risk: str = "Medium"


@dataclass
class DebateChallenge:
    target_agent: str
    challenge: str
    response: str


@dataclass
class VerificationResult:
    agent: str
    status: str
    rationale: str
    confidence_adjustment: int


@dataclass
class BoardroomReport:
    question: str
    timeline: list[str]
    findings: list[AgentFinding]
    debate: list[DebateChallenge]
    verification: list[VerificationResult]
    ranked_causes: list[AgentFinding]
    forecast: AgentFinding
    ceo_summary: str
    metadata: dict[str, Any] = field(default_factory=dict)
