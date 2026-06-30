from __future__ import annotations

import pandas as pd

from boardroomiq.analytics.common import pct_change, safe_divide
from boardroomiq.analytics.profiler import DatasetProfile
from boardroomiq.core.models import AgentFinding


def _first_existing(frame: pd.DataFrame, candidates: list[str]) -> str | None:
    for column in candidates:
        if column in frame.columns:
            return column
    return None


def _truthy_rate(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    if pd.api.types.is_bool_dtype(series):
        return float(series.mean())
    if pd.api.types.is_numeric_dtype(series):
        return safe_divide(float((series > 0).sum()), float(len(series)))
    normalized = series.astype(str).str.strip().str.lower()
    positive = normalized.isin({"yes", "y", "true", "1", "converted", "paid", "completed", "done", "won", "booked"})
    return safe_divide(float(positive.sum()), float(len(series)))


def _status_breakdown(series: pd.Series) -> dict[str, int]:
    return {str(key): int(value) for key, value in series.astype(str).str.strip().value_counts().head(8).items()}


class CustomerOnboardingAgent:
    name = "Customer / Onboarding Agent"

    def run(self, frame: pd.DataFrame, profile: DatasetProfile) -> AgentFinding:
        status_col = _first_existing(frame, profile.possible_status_columns)
        conversion_col = _first_existing(frame, profile.possible_conversion_columns)
        booking_col = _first_existing(frame, profile.possible_booking_columns + profile.date_columns)
        source_col = _first_existing(frame, profile.possible_source_columns)
        location_col = _first_existing(frame, profile.possible_location_columns)

        total_records = int(len(frame))
        conversion_rate = _truthy_rate(frame[conversion_col]) if conversion_col else 0.0
        booked_count = total_records
        not_converted = int(round(total_records * (1 - conversion_rate))) if conversion_col else 0

        evidence = [f"Detected {total_records} customer/onboarding record(s)."]
        if booking_col:
            evidence.append(f"Booking or timeline signal found in `{booking_col}`.")
        if conversion_col:
            evidence.append(f"Conversion rate is {conversion_rate * 100:.1f}%; estimated not converted count is {not_converted}.")
        else:
            evidence.append("Conversion rate cannot be calculated because no clear conversion column was found.")
        if status_col:
            breakdown = _status_breakdown(frame[status_col])
            evidence.append(f"Top status breakdown: {breakdown}.")
        if source_col:
            weakest_source = frame.groupby(source_col).size().sort_values().index[0]
            evidence.append(f"Lowest-volume source/channel is `{weakest_source}`.")
        if location_col:
            evidence.append(f"Location segmentation is available through `{location_col}`.")

        confidence = 84 if conversion_col or status_col else 62
        return AgentFinding(
            agent=self.name,
            claim="Uploaded data supports customer booking, onboarding, and conversion analysis.",
            evidence=evidence,
            confidence=confidence,
            metrics={
                "total_records": total_records,
                "booked_count": booked_count,
                "conversion_rate_pct": conversion_rate * 100,
                "not_converted_count": not_converted,
                "status_column": status_col,
                "conversion_column": conversion_col,
                "source_column": source_col,
                "location_column": location_col,
            },
            recommendation="Focus on the largest booked-but-not-converted segment and inspect follow-up/status reasons.",
            risk="High" if conversion_col and conversion_rate < 0.45 else "Medium",
        )


class FlexibleFinanceAgent:
    name = "Flexible Finance Agent"

    def run(self, frame: pd.DataFrame, profile: DatasetProfile) -> AgentFinding:
        revenue_col = _first_existing(frame, profile.possible_revenue_columns)
        if not revenue_col:
            return AgentFinding(
                agent=self.name,
                claim="Revenue/payment analysis is not available from this upload.",
                evidence=["No amount, revenue, paid, price, sales, or value column was found."],
                confidence=35,
                metrics={},
                recommendation="Add an amount_paid, revenue, plan_value, or payment column to enable finance analysis.",
                risk="Medium",
            )

        values = pd.to_numeric(frame[revenue_col], errors="coerce").fillna(0)
        total = float(values.sum())
        average = float(values.mean()) if len(values) else 0.0
        evidence = [
            f"Detected revenue/payment column `{revenue_col}`.",
            f"Total value is {total:,.0f}.",
            f"Average value per record is {average:,.0f}.",
        ]

        date_col = _first_existing(frame, profile.date_columns)
        change = 0.0
        if date_col:
            dated = frame.copy()
            dated[date_col] = pd.to_datetime(dated[date_col], errors="coerce")
            dated = dated.dropna(subset=[date_col]).sort_values(date_col)
            if len(dated) >= 4:
                midpoint = dated[date_col].min() + (dated[date_col].max() - dated[date_col].min()) / 2
                previous = pd.to_numeric(dated[dated[date_col] <= midpoint][revenue_col], errors="coerce").fillna(0).sum()
                current = pd.to_numeric(dated[dated[date_col] > midpoint][revenue_col], errors="coerce").fillna(0).sum()
                change = pct_change(float(previous), float(current))
                evidence.append(f"Value changed by {change:.1f}% across the detected timeline.")

        return AgentFinding(
            agent=self.name,
            claim="Payment or revenue signals were found and summarized from the uploaded data.",
            evidence=evidence,
            confidence=78 if total > 0 else 55,
            metrics={"revenue_column": revenue_col, "total_value": total, "average_value": average, "period_change_pct": change},
            recommendation="Compare value trend with conversion and source segments to identify the strongest revenue driver.",
            risk="High" if change < -10 else "Medium",
        )


class FlexibleMarketingAgent:
    name = "Flexible Marketing Agent"

    def run(self, frame: pd.DataFrame, profile: DatasetProfile) -> AgentFinding:
        spend_col = _first_existing(frame, profile.possible_spend_columns)
        conversion_col = _first_existing(frame, profile.possible_conversion_columns)
        source_col = _first_existing(frame, profile.possible_source_columns)

        evidence = []
        metrics = {"spend_column": spend_col, "conversion_column": conversion_col, "source_column": source_col}
        if source_col:
            source_counts = {str(key): int(value) for key, value in frame[source_col].astype(str).value_counts().head(5).items()}
            evidence.append(f"Source/channel breakdown is available: {source_counts}.")
        else:
            evidence.append("No source, campaign, channel, or medium column was found.")

        if spend_col and conversion_col:
            spend = float(pd.to_numeric(frame[spend_col], errors="coerce").fillna(0).sum())
            conversions = _truthy_rate(frame[conversion_col]) * len(frame)
            cac = safe_divide(spend, float(conversions))
            evidence.append(f"CAC is {cac:,.0f} using `{spend_col}` divided by converted records from `{conversion_col}`.")
            metrics.update({"total_spend": spend, "estimated_conversions": conversions, "cac": cac})
            confidence = 82
            claim = "CAC and source-level marketing analysis are supported by the uploaded data."
            recommendation = "Prioritize channels with strong conversion and low CAC; pause weak sources for review."
        elif conversion_col:
            evidence.append(f"Conversion signal found in `{conversion_col}`, but CAC cannot be calculated without spend.")
            confidence = 68
            claim = "Conversion analysis is possible, but CAC is unavailable because spend is missing."
            recommendation = "Add campaign spend or acquisition cost to calculate CAC."
        else:
            evidence.append("CAC cannot be calculated because conversion and spend columns are incomplete.")
            confidence = 45
            claim = "Marketing attribution is limited from this upload."
            recommendation = "Add lead_source/campaign, converted, and spend columns for marketing analysis."

        return AgentFinding(
            agent=self.name,
            claim=claim,
            evidence=evidence,
            confidence=confidence,
            metrics=metrics,
            recommendation=recommendation,
            risk="Medium",
        )


class FlexibleTrendAgent:
    name = "Flexible Trend Agent"

    def run(self, frame: pd.DataFrame, profile: DatasetProfile) -> AgentFinding:
        date_col = _first_existing(frame, profile.date_columns)
        if not date_col:
            return AgentFinding(
                agent=self.name,
                claim="Trend analysis is not available because no usable date column was found.",
                evidence=["Add booking_date, created_at, signup_date, or another date column to analyze dips over time."],
                confidence=40,
                metrics={},
                recommendation="Add a date column so BoardroomIQ can compare current and previous periods.",
                risk="Medium",
            )

        dated = frame.copy()
        dated[date_col] = pd.to_datetime(dated[date_col], errors="coerce")
        dated = dated.dropna(subset=[date_col]).sort_values(date_col)
        midpoint = dated[date_col].min() + (dated[date_col].max() - dated[date_col].min()) / 2
        previous_count = int((dated[date_col] <= midpoint).sum())
        current_count = int((dated[date_col] > midpoint).sum())
        count_change = pct_change(previous_count, current_count)

        evidence = [
            f"Trend column `{date_col}` was used.",
            f"Previous-period records: {previous_count}.",
            f"Current-period records: {current_count}.",
            f"Record volume changed by {count_change:.1f}%.",
        ]

        return AgentFinding(
            agent=self.name,
            claim="The uploaded data supports timeline-based dip detection.",
            evidence=evidence,
            confidence=76 if len(dated) >= 6 else 58,
            metrics={"date_column": date_col, "previous_count": previous_count, "current_count": current_count, "count_change_pct": count_change},
            recommendation="Investigate the period where volume declined and compare it with source, status, and follow-up changes.",
            risk="High" if count_change < -10 else "Medium",
        )
