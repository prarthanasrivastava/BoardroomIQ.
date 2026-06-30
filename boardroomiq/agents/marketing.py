from __future__ import annotations

import pandas as pd

from boardroomiq.analytics.common import pct_change, safe_divide, split_half_by_date
from boardroomiq.core.models import AgentFinding


class MarketingAgent:
    name = "Marketing Agent"

    def run(self, marketing: pd.DataFrame) -> AgentFinding:
        previous, current = split_half_by_date(marketing)

        prev_clicks = float(previous["clicks"].sum())
        curr_clicks = float(current["clicks"].sum())
        prev_conversions = float(previous["conversions"].sum())
        curr_conversions = float(current["conversions"].sum())
        prev_spend = float(previous["spend"].sum())
        curr_spend = float(current["spend"].sum())

        prev_conversion_rate = safe_divide(prev_conversions, prev_clicks)
        curr_conversion_rate = safe_divide(curr_conversions, curr_clicks)
        prev_cac = safe_divide(prev_spend, prev_conversions)
        curr_cac = safe_divide(curr_spend, curr_conversions)
        conversion_change = pct_change(prev_conversion_rate, curr_conversion_rate)
        cac_change = pct_change(prev_cac, curr_cac)

        regional = current.groupby("region")["conversions"].sum().sort_values()
        weakest_region = str(regional.index[0]) if not regional.empty else "unknown"
        confidence = min(88, max(40, int(abs(conversion_change) * 1.3 + max(cac_change, 0) * 0.7)))

        return AgentFinding(
            agent=self.name,
            claim="Marketing efficiency declined due to weaker conversion and higher acquisition cost.",
            evidence=[
                f"Conversion rate moved from {prev_conversion_rate * 100:.1f}% to {curr_conversion_rate * 100:.1f}%.",
                f"CAC moved from {prev_cac:.0f} to {curr_cac:.0f}.",
                f"Weakest current conversion region is {weakest_region}.",
            ],
            confidence=confidence,
            metrics={
                "previous_conversion_rate_pct": prev_conversion_rate * 100,
                "current_conversion_rate_pct": curr_conversion_rate * 100,
                "conversion_change_pct": conversion_change,
                "previous_cac": prev_cac,
                "current_cac": curr_cac,
                "cac_change_pct": cac_change,
            },
            recommendation=f"Audit campaign targeting and landing flow in {weakest_region} before scaling budget.",
            risk="Medium" if cac_change < 40 else "High",
        )
