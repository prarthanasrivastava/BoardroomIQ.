from __future__ import annotations

import pandas as pd

from boardroomiq.analytics.common import pct_change, safe_divide, split_half_by_date
from boardroomiq.core.models import AgentFinding


class OperationsAgent:
    name = "Operations Agent"

    def run(self, inventory: pd.DataFrame, sales: pd.DataFrame) -> AgentFinding:
        previous, current = split_half_by_date(inventory)
        prev_stockouts = int(previous["stockout"].sum())
        curr_stockouts = int(current["stockout"].sum())
        stockout_change = pct_change(prev_stockouts, curr_stockouts)

        product_stockouts = current.groupby("product")["stockout"].sum().sort_values(ascending=False)
        top_stockout_product = str(product_stockouts.index[0]) if not product_stockouts.empty else "unknown"

        product_revenue = sales.groupby("product")["revenue"].sum().sort_values(ascending=False)
        top_revenue_product = str(product_revenue.index[0]) if not product_revenue.empty else "unknown"

        daily_stockouts = inventory.groupby("date")["stockout"].sum()
        daily_sales = sales.groupby("date")["revenue"].sum()
        aligned = pd.concat([daily_stockouts, daily_sales], axis=1).fillna(0)
        correlation = 0.0
        if len(aligned) > 2 and aligned["stockout"].std() > 0 and aligned["revenue"].std() > 0:
            correlation = float(aligned["stockout"].corr(aligned["revenue"]))

        demand_gap = safe_divide(
            float(current["demand"].sum() - current["stock_level"].sum()),
            float(current["demand"].sum()),
        )
        confidence = min(94, max(50, int(abs(stockout_change) * 0.9 + abs(correlation) * 35 + demand_gap * 60)))

        return AgentFinding(
            agent=self.name,
            claim="Inventory constraints are a strong candidate cause for revenue loss.",
            evidence=[
                f"Stockouts changed by {stockout_change:.1f}% between periods.",
                f"Most affected product is {top_stockout_product}.",
                f"Top revenue product is {top_revenue_product}.",
                f"Stockout-to-revenue correlation is {correlation:.2f}.",
            ],
            confidence=confidence,
            metrics={
                "previous_stockouts": prev_stockouts,
                "current_stockouts": curr_stockouts,
                "stockout_change_pct": stockout_change,
                "top_stockout_product": top_stockout_product,
                "top_revenue_product": top_revenue_product,
                "stockout_revenue_correlation": correlation,
                "demand_gap_pct": demand_gap * 100,
            },
            recommendation=f"Increase availability and replenishment priority for {top_stockout_product}.",
            risk="High" if curr_stockouts > prev_stockouts else "Medium",
        )
