from __future__ import annotations

import pandas as pd

from boardroomiq.analytics.common import pct_change
from boardroomiq.core.models import AgentFinding


class ForecastAgent:
    name = "Forecast Agent"

    def run(self, sales: pd.DataFrame, inventory: pd.DataFrame) -> AgentFinding:
        monthly_revenue = sales.set_index("date")["revenue"].resample("ME").sum()
        current_revenue = float(monthly_revenue.iloc[-1]) if len(monthly_revenue) else 0.0
        previous_revenue = float(monthly_revenue.iloc[-2]) if len(monthly_revenue) > 1 else current_revenue
        revenue_trend = pct_change(previous_revenue, current_revenue)
        next_revenue = current_revenue * (1 + revenue_trend / 100)

        monthly_stockouts = inventory.set_index("date")["stockout"].resample("ME").sum()
        current_stockouts = float(monthly_stockouts.iloc[-1]) if len(monthly_stockouts) else 0.0
        previous_stockouts = float(monthly_stockouts.iloc[-2]) if len(monthly_stockouts) > 1 else current_stockouts
        stockout_trend = pct_change(previous_stockouts, current_stockouts)
        next_stockouts = max(0.0, current_stockouts * (1 + stockout_trend / 100))

        risk = "High" if revenue_trend < -5 or stockout_trend > 10 else "Medium"
        confidence = 72 if len(monthly_revenue) >= 3 else 55

        return AgentFinding(
            agent=self.name,
            claim="Near-term outlook depends on whether current revenue and stockout trends continue.",
            evidence=[
                f"Latest monthly revenue is {current_revenue:,.0f}.",
                f"Revenue month-over-month trend is {revenue_trend:.1f}%.",
                f"Projected next-month revenue is {next_revenue:,.0f}.",
                f"Projected next-month stockouts are {next_stockouts:.0f}.",
            ],
            confidence=confidence,
            metrics={
                "current_month_revenue": current_revenue,
                "revenue_trend_pct": revenue_trend,
                "projected_next_month_revenue": next_revenue,
                "stockout_trend_pct": stockout_trend,
                "projected_next_month_stockouts": next_stockouts,
            },
            recommendation="Stabilize constrained inventory before scaling demand generation.",
            risk=risk,
        )
