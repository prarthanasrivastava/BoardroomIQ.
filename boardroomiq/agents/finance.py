from __future__ import annotations

import pandas as pd

from boardroomiq.analytics.common import pct_change, safe_divide, split_half_by_date
from boardroomiq.core.models import AgentFinding


class FinanceAgent:
    name = "Finance Agent"

    def run(self, sales: pd.DataFrame) -> AgentFinding:
        previous, current = split_half_by_date(sales)

        prev_revenue = float(previous["revenue"].sum())
        curr_revenue = float(current["revenue"].sum())
        prev_cost = float(previous["cost"].sum())
        curr_cost = float(current["cost"].sum())

        prev_margin = safe_divide(prev_revenue - prev_cost, prev_revenue)
        curr_margin = safe_divide(curr_revenue - curr_cost, curr_revenue)
        revenue_change = pct_change(prev_revenue, curr_revenue)
        margin_change = (curr_margin - prev_margin) * 100

        confidence = min(90, max(45, int(abs(revenue_change) * 2 + abs(margin_change) * 4)))
        claim = "Revenue pressure is linked to declining revenue and margin movement."
        if revenue_change < -5 and margin_change < -2:
            claim = "Revenue dropped while margins compressed, creating both growth and profitability pressure."
        elif revenue_change < -5:
            claim = "Revenue declined, but margin movement is not the only explanation."

        return AgentFinding(
            agent=self.name,
            claim=claim,
            evidence=[
                f"Revenue changed by {revenue_change:.1f}% between the two periods.",
                f"Gross margin moved from {prev_margin * 100:.1f}% to {curr_margin * 100:.1f}%.",
                f"Current-period revenue is {curr_revenue:,.0f}.",
            ],
            confidence=confidence,
            metrics={
                "previous_revenue": prev_revenue,
                "current_revenue": curr_revenue,
                "revenue_change_pct": revenue_change,
                "previous_margin_pct": prev_margin * 100,
                "current_margin_pct": curr_margin * 100,
            },
            recommendation="Review pricing, discounting, and high-cost product lines before increasing spend.",
            risk="Medium" if revenue_change > -15 else "High",
        )
