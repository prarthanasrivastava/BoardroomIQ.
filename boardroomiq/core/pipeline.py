from __future__ import annotations

import pandas as pd

from boardroomiq.agents.ceo import CEOAgent
from boardroomiq.agents.data_profiler import DataProfilerAgent
from boardroomiq.agents.debate import DebateAgent
from boardroomiq.agents.flexible import (
    CustomerOnboardingAgent,
    FlexibleFinanceAgent,
    FlexibleMarketingAgent,
    FlexibleTrendAgent,
)
from boardroomiq.agents.finance import FinanceAgent
from boardroomiq.agents.forecast import ForecastAgent
from boardroomiq.agents.judge import JudgeAgent
from boardroomiq.agents.marketing import MarketingAgent
from boardroomiq.agents.operations import OperationsAgent
from boardroomiq.agents.planner import PlannerAgent
from boardroomiq.agents.risk import RiskAgent
from boardroomiq.agents.verification import VerificationAgent
from boardroomiq.analytics.profiler import profile_datasets, profile_to_dict
from boardroomiq.core.models import BoardroomReport


def run_boardroom_analysis(question: str, data: dict[str, pd.DataFrame]) -> BoardroomReport:
    required = {"sales", "customers", "inventory", "marketing"}
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"Missing required datasets: {', '.join(missing)}")

    timeline = PlannerAgent().run(question, sorted(data.keys()))

    findings = [
        FinanceAgent().run(data["sales"]),
        MarketingAgent().run(data["marketing"]),
        OperationsAgent().run(data["inventory"], data["sales"]),
        RiskAgent().run(data["customers"], data["sales"]),
    ]
    timeline.extend([f"{finding.agent} completed analysis." for finding in findings])

    debate = DebateAgent().run(findings)
    timeline.append("Debate Agent challenged each specialist claim.")

    verification = VerificationAgent().run(findings)
    timeline.append("Verification Agent checked whether claims were backed by computed evidence.")

    ranked_causes = JudgeAgent().run(findings, verification)
    timeline.append("Judge Agent ranked the strongest explanations by adjusted confidence.")

    forecast = ForecastAgent().run(data["sales"], data["inventory"])
    timeline.append("Forecast Agent projected revenue and stockout direction.")

    ceo_summary = CEOAgent().run(ranked_causes, forecast)
    timeline.append("CEO Agent produced an executive recommendation.")

    return BoardroomReport(
        question=question,
        timeline=timeline,
        findings=findings,
        debate=debate,
        verification=verification,
        ranked_causes=ranked_causes,
        forecast=forecast,
        ceo_summary=ceo_summary,
        metadata={"mode": "sample", "profiles": [profile_to_dict(profile) for profile in profile_datasets(data)]},
    )


def run_flexible_boardroom_analysis(question: str, data: dict[str, pd.DataFrame]) -> BoardroomReport:
    if not data:
        raise ValueError("At least one dataset is required.")

    profiles = profile_datasets(data)
    timeline = [
        f"Received strategic question: {question}",
        f"Uploaded {len(data)} dataset(s): {', '.join(data.keys())}.",
        "Data Profiler Agent inspected columns, row counts, metric signals, and missing evidence.",
    ]

    findings = [DataProfilerAgent().run(profiles)]
    customer_agent = CustomerOnboardingAgent()
    finance_agent = FlexibleFinanceAgent()
    marketing_agent = FlexibleMarketingAgent()
    trend_agent = FlexibleTrendAgent()

    for profile in profiles:
        frame = data[profile.name]
        supports_customer = bool(
            profile.possible_status_columns
            or profile.possible_conversion_columns
            or profile.possible_booking_columns
        )
        if supports_customer:
            findings.append(customer_agent.run(frame, profile))
            timeline.append(f"Customer / Onboarding Agent analyzed `{profile.name}`.")

        if profile.possible_revenue_columns:
            findings.append(finance_agent.run(frame, profile))
            timeline.append(f"Flexible Finance Agent analyzed `{profile.name}`.")

        if profile.possible_source_columns or profile.possible_spend_columns or profile.possible_conversion_columns:
            findings.append(marketing_agent.run(frame, profile))
            timeline.append(f"Flexible Marketing Agent analyzed `{profile.name}`.")

        if profile.date_columns:
            findings.append(trend_agent.run(frame, profile))
            timeline.append(f"Flexible Trend Agent analyzed `{profile.name}`.")

    if len(findings) == 1:
        findings.append(
            trend_agent.run(next(iter(data.values())), profiles[0])
        )
        timeline.append("No specialist agent had enough signals, so BoardroomIQ produced basic profiling guidance.")

    debate = DebateAgent().run(findings)
    timeline.append("Debate Agent challenged supported and unsupported claims.")

    verification = VerificationAgent().run(findings)
    timeline.append("Verification Agent marked which answers are supported by actual columns.")

    rankable_findings = [finding for finding in findings if finding.agent != "Data Profiler Agent"]
    ranked_causes = JudgeAgent().run(rankable_findings or findings, verification)
    timeline.append("Judge Agent ranked the strongest available insights.")

    forecast_candidates = [finding for finding in findings if finding.agent == "Flexible Trend Agent"]
    forecast = forecast_candidates[0] if forecast_candidates else findings[0]
    timeline.append("Forecast view used the best available time-based signal.")

    ceo_summary = CEOAgent().run(ranked_causes, forecast)
    timeline.append("CEO Agent produced an executive recommendation with data limitations.")

    return BoardroomReport(
        question=question,
        timeline=timeline,
        findings=findings,
        debate=debate,
        verification=verification,
        ranked_causes=ranked_causes,
        forecast=forecast,
        ceo_summary=ceo_summary,
        metadata={"mode": "flexible_upload", "profiles": [profile_to_dict(profile) for profile in profiles]},
    )
