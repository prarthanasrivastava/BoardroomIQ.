from __future__ import annotations

from boardroomiq.analytics.profiler import DatasetProfile
from boardroomiq.core.models import AgentFinding


class DataProfilerAgent:
    name = "Data Profiler Agent"

    def run(self, profiles: list[DatasetProfile]) -> AgentFinding:
        total_rows = sum(profile.rows for profile in profiles)
        dataset_names = ", ".join(profile.name for profile in profiles)
        evidence = [
            f"Detected {len(profiles)} dataset(s): {dataset_names}.",
            f"Total available rows: {total_rows}.",
        ]

        for profile in profiles:
            signals = []
            if profile.date_columns:
                signals.append("time trends")
            if profile.possible_conversion_columns or profile.possible_status_columns:
                signals.append("conversion/status analysis")
            if profile.possible_revenue_columns:
                signals.append("revenue/payment analysis")
            if profile.possible_spend_columns:
                signals.append("CAC analysis")
            evidence.append(f"{profile.name}: {profile.rows} rows, {len(profile.columns)} columns, supports {', '.join(signals) or 'basic profiling'}.")

        return AgentFinding(
            agent=self.name,
            claim="Available data was profiled and the analysis plan was adapted to the uploaded columns.",
            evidence=evidence,
            confidence=92,
            metrics={"datasets": len(profiles), "total_rows": total_rows},
            recommendation="Run only the agents supported by the uploaded data and mark unsupported metrics as unavailable.",
            risk="Low",
        )
