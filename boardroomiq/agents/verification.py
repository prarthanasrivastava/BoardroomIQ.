from __future__ import annotations

from boardroomiq.core.models import AgentFinding, VerificationResult


class VerificationAgent:
    name = "Verification Agent"

    def run(self, findings: list[AgentFinding]) -> list[VerificationResult]:
        results = []
        for finding in findings:
            evidence_count = len([item for item in finding.evidence if item])
            has_metrics = bool(finding.metrics)

            if evidence_count >= 3 and has_metrics and finding.confidence >= 75:
                status = "Strong evidence"
                adjustment = 3
                rationale = "Claim is supported by multiple computed metrics and a high confidence score."
            elif evidence_count >= 2 and has_metrics:
                status = "Partially valid"
                adjustment = 0
                rationale = "Claim is supported by computed metrics but may not fully explain the outcome alone."
            else:
                status = "Weak evidence"
                adjustment = -10
                rationale = "Claim needs more measurable support before it should drive strategy."

            results.append(
                VerificationResult(
                    agent=finding.agent,
                    status=status,
                    rationale=rationale,
                    confidence_adjustment=adjustment,
                )
            )
        return results
