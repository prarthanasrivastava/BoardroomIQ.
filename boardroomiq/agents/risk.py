from __future__ import annotations

import pandas as pd

from boardroomiq.analytics.common import safe_divide
from boardroomiq.core.models import AgentFinding


class RiskAgent:
    name = "Risk Agent"

    def run(self, customers: pd.DataFrame, sales: pd.DataFrame) -> AgentFinding:
        repeat_rate = safe_divide(float(customers["repeat_customer"].sum()), float(len(customers)))

        latest_purchase = customers["last_purchase_date"].max()
        churn_cutoff = latest_purchase - pd.Timedelta(days=60)
        churned = customers[customers["last_purchase_date"] < churn_cutoff]
        churn_rate = safe_divide(float(len(churned)), float(len(customers)))

        product_share = sales.groupby("product")["revenue"].sum().sort_values(ascending=False)
        top_two_share = safe_divide(float(product_share.head(2).sum()), float(product_share.sum()))

        confidence = min(86, max(45, int(churn_rate * 70 + top_two_share * 45)))

        return AgentFinding(
            agent=self.name,
            claim="Customer churn and product concentration create downside risk.",
            evidence=[
                f"Repeat customer rate is {repeat_rate * 100:.1f}%.",
                f"Estimated churn rate is {churn_rate * 100:.1f}%.",
                f"Top two products contribute {top_two_share * 100:.1f}% of revenue.",
            ],
            confidence=confidence,
            metrics={
                "repeat_rate_pct": repeat_rate * 100,
                "churn_rate_pct": churn_rate * 100,
                "top_two_product_revenue_share_pct": top_two_share * 100,
            },
            recommendation="Reduce dependency risk with retention campaigns and broader product demand generation.",
            risk="High" if churn_rate > 0.25 or top_two_share > 0.55 else "Medium",
        )
