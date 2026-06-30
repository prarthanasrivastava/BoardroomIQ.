from __future__ import annotations

from boardroomiq.core.models import AgentFinding, DebateChallenge


class DebateAgent:
    name = "Debate Agent"

    def run(self, findings: list[AgentFinding]) -> list[DebateChallenge]:
        challenges = []
        for finding in findings:
            challenge = "Can this claim independently explain the business decline?"
            response = "The claim is useful, but should be evaluated with cross-functional evidence."

            if finding.agent == "Finance Agent":
                challenge = "Can margin decline alone explain the revenue drop?"
                response = "Finance evidence explains profitability pressure, but revenue causality needs sales, marketing, and operations support."
            elif finding.agent == "Marketing Agent":
                challenge = "Did conversion weakness appear across the business or only in specific regions?"
                response = "Marketing evidence should be treated as strongest where regional conversion and CAC both deteriorated."
            elif finding.agent == "Operations Agent":
                challenge = "Can stockouts explain every product category, or only constrained products?"
                response = "Operations evidence is strongest when stockouts overlap with high-revenue products and demand gaps."
            elif finding.agent == "Risk Agent":
                challenge = "Are risk signals primary causes or supporting warnings?"
                response = "Risk evidence is better treated as a compounding factor unless directly tied to period revenue loss."

            challenges.append(
                DebateChallenge(
                    target_agent=finding.agent,
                    challenge=challenge,
                    response=response,
                )
            )
        return challenges
