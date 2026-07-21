from __future__ import annotations

from typing import Any, TypedDict

import pandas as pd

from boardroomiq.analytics.profiler import DatasetProfile
from boardroomiq.core.models import AgentFinding, DebateChallenge, VerificationResult


class BoardroomGraphState(TypedDict, total=False):
    question: str
    data: dict[str, pd.DataFrame]
    mode: str
    profiles: list[DatasetProfile]
    timeline: list[str]
    findings: list[AgentFinding]
    debate: list[DebateChallenge]
    verification: list[VerificationResult]
    evidence_gaps: list[str]
    ranked_causes: list[AgentFinding]
    confidence_review: dict[str, Any]
    forecast: AgentFinding
    ceo_summary: str
    metadata: dict[str, Any]
