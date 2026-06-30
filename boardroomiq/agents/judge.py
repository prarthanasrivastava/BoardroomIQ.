from __future__ import annotations

from boardroomiq.core.models import AgentFinding, VerificationResult


class JudgeAgent:
    name = "Judge Agent"

    def run(
        self,
        findings: list[AgentFinding],
        verification: list[VerificationResult],
    ) -> list[AgentFinding]:
        adjustments = {item.agent: item.confidence_adjustment for item in verification}
        ranked = []

        for finding in findings:
            adjusted = max(0, min(100, finding.confidence + adjustments.get(finding.agent, 0)))
            ranked.append(
                AgentFinding(
                    agent=finding.agent,
                    claim=finding.claim,
                    evidence=finding.evidence,
                    confidence=adjusted,
                    metrics=finding.metrics,
                    recommendation=finding.recommendation,
                    risk=finding.risk,
                )
            )

        return sorted(ranked, key=lambda item: item.confidence, reverse=True)
