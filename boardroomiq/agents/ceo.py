from __future__ import annotations

from boardroomiq.core.models import AgentFinding


class CEOAgent:
    name = "CEO Agent"

    def run(self, ranked_causes: list[AgentFinding], forecast: AgentFinding) -> str:
        primary = ranked_causes[0]
        secondary = ranked_causes[1] if len(ranked_causes) > 1 else None

        summary = (
            f"The strongest explanation is: {primary.claim} "
            f"({primary.confidence}% confidence). Recommended action: {primary.recommendation}"
        )
        if secondary:
            summary += (
                f" A secondary factor is: {secondary.claim} "
                f"({secondary.confidence}% confidence), so leadership should also act on: {secondary.recommendation}"
            )
        summary += f" Forecast view: {forecast.claim} {forecast.recommendation}"
        return summary
