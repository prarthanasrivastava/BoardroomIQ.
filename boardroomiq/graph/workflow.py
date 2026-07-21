from __future__ import annotations

import pandas as pd
from langgraph.graph import END, StateGraph

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
from boardroomiq.graph.state import BoardroomGraphState


def _profile_data(state: BoardroomGraphState) -> BoardroomGraphState:
    data = state["data"]
    profiles = profile_datasets(data)
    mode = state.get("mode", "sample")
    timeline = [
        f"Received strategic question: {state['question']}",
        f"LangGraph workflow started in `{mode}` mode.",
        f"Detected {len(data)} dataset(s): {', '.join(data.keys())}.",
    ]
    if mode == "flexible_upload":
        timeline.append("Data Profiler Agent inspected uploaded fields and metric signals.")
    return {**state, "profiles": profiles, "timeline": timeline}


def _plan_analysis(state: BoardroomGraphState) -> BoardroomGraphState:
    planner_steps = PlannerAgent().run(state["question"], sorted(state["data"].keys()))
    timeline = state["timeline"] + ["Planner Agent created the board meeting agenda."] + planner_steps[2:]
    return {**state, "timeline": timeline}


def _run_specialists(state: BoardroomGraphState) -> BoardroomGraphState:
    data = state["data"]
    mode = state.get("mode", "sample")
    findings: list = []
    timeline = list(state["timeline"])

    if mode == "sample":
        findings = [
            FinanceAgent().run(data["sales"]),
            MarketingAgent().run(data["marketing"]),
            OperationsAgent().run(data["inventory"], data["sales"]),
            RiskAgent().run(data["customers"], data["sales"]),
        ]
        timeline.extend([f"{finding.agent} completed analysis." for finding in findings])
        return {**state, "findings": findings, "timeline": timeline}

    profiles = state["profiles"]
    findings.append(DataProfilerAgent().run(profiles))
    customer_agent = CustomerOnboardingAgent()
    finance_agent = FlexibleFinanceAgent()
    marketing_agent = FlexibleMarketingAgent()
    trend_agent = FlexibleTrendAgent()

    for profile in profiles:
        frame = data[profile.name]
        if profile.possible_status_columns or profile.possible_conversion_columns or profile.possible_booking_columns:
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
        findings.append(trend_agent.run(next(iter(data.values())), profiles[0]))
        timeline.append("No specialist agent had enough signals, so BoardroomIQ produced basic profiling guidance.")

    return {**state, "findings": findings, "timeline": timeline}


def _run_debate(state: BoardroomGraphState) -> BoardroomGraphState:
    debate = DebateAgent().run(state["findings"])
    return {
        **state,
        "debate": debate,
        "timeline": state["timeline"] + ["Debate Agent challenged each specialist claim."],
    }


def _run_verification(state: BoardroomGraphState) -> BoardroomGraphState:
    verification = VerificationAgent().run(state["findings"])
    return {
        **state,
        "verification": verification,
        "timeline": state["timeline"] + ["Verification Agent checked claims against computed evidence."],
    }


def _run_judge(state: BoardroomGraphState) -> BoardroomGraphState:
    mode = state.get("mode", "sample")
    findings = state["findings"]
    if mode == "flexible_upload":
        findings = [finding for finding in findings if finding.agent != "Data Profiler Agent"] or findings
    ranked_causes = JudgeAgent().run(findings, state["verification"])
    return {
        **state,
        "ranked_causes": ranked_causes,
        "timeline": state["timeline"] + ["Judge Agent ranked the strongest explanations."],
    }


def _run_forecast(state: BoardroomGraphState) -> BoardroomGraphState:
    mode = state.get("mode", "sample")
    data = state["data"]
    if mode == "sample":
        forecast = ForecastAgent().run(data["sales"], data["inventory"])
        timeline_step = "Forecast Agent projected revenue and stockout direction."
    else:
        candidates = [finding for finding in state["findings"] if finding.agent == "Flexible Trend Agent"]
        forecast = candidates[0] if candidates else state["findings"][0]
        timeline_step = "Forecast view used the best available time-based signal."
    return {**state, "forecast": forecast, "timeline": state["timeline"] + [timeline_step]}


def _run_ceo(state: BoardroomGraphState) -> BoardroomGraphState:
    ceo_summary = CEOAgent().run(state["ranked_causes"], state["forecast"])
    profiles = [profile_to_dict(profile) for profile in state["profiles"]]
    metadata = {
        "mode": state.get("mode", "sample"),
        "profiles": profiles,
        "workflow": "langgraph",
        "graph_nodes": [
            "profile_data",
            "plan_analysis",
            "run_specialists",
            "run_debate",
            "run_verification",
            "run_judge",
            "run_forecast",
            "run_ceo",
        ],
    }
    return {
        **state,
        "ceo_summary": ceo_summary,
        "metadata": metadata,
        "timeline": state["timeline"] + ["CEO Agent produced an executive decision brief."],
    }


def build_boardroom_graph():
    graph = StateGraph(BoardroomGraphState)
    graph.add_node("profile_data", _profile_data)
    graph.add_node("plan_analysis", _plan_analysis)
    graph.add_node("run_specialists", _run_specialists)
    graph.add_node("run_debate", _run_debate)
    graph.add_node("run_verification", _run_verification)
    graph.add_node("run_judge", _run_judge)
    graph.add_node("run_forecast", _run_forecast)
    graph.add_node("run_ceo", _run_ceo)

    graph.set_entry_point("profile_data")
    graph.add_edge("profile_data", "plan_analysis")
    graph.add_edge("plan_analysis", "run_specialists")
    graph.add_edge("run_specialists", "run_debate")
    graph.add_edge("run_debate", "run_verification")
    graph.add_edge("run_verification", "run_judge")
    graph.add_edge("run_judge", "run_forecast")
    graph.add_edge("run_forecast", "run_ceo")
    graph.add_edge("run_ceo", END)
    return graph.compile()


def run_boardroom_graph(
    question: str,
    data: dict[str, pd.DataFrame],
    mode: str = "sample",
) -> BoardroomReport:
    if mode == "sample":
        required = {"sales", "customers", "inventory", "marketing"}
        missing = sorted(required - set(data))
        if missing:
            raise ValueError(f"Missing required datasets: {', '.join(missing)}")
    elif not data:
        raise ValueError("At least one dataset is required.")

    app = build_boardroom_graph()
    state = app.invoke({"question": question, "data": data, "mode": mode})
    return BoardroomReport(
        question=question,
        timeline=state["timeline"],
        findings=state["findings"],
        debate=state["debate"],
        verification=state["verification"],
        ranked_causes=state["ranked_causes"],
        forecast=state["forecast"],
        ceo_summary=state["ceo_summary"],
        metadata=state["metadata"],
    )
