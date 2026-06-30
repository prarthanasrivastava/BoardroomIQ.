from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from boardroomiq.core.pipeline import run_boardroom_analysis
from boardroomiq.utils.data_loader import normalize_uploads, read_sample_data


st.set_page_config(
    page_title="BoardroomIQ",
    page_icon="BI",
    layout="wide",
)


def metric_card(label: str, value: str) -> None:
    st.markdown(f"**{label}**")
    st.markdown(f"<div class='metric-card'>{value}</div>", unsafe_allow_html=True)


def render_finding(finding) -> None:
    with st.container(border=True):
        top = st.columns([3, 1, 1])
        top[0].subheader(finding.agent)
        top[1].metric("Confidence", f"{finding.confidence}%")
        top[2].metric("Risk", finding.risk)
        st.write(finding.claim)
        st.markdown("**Evidence**")
        for item in finding.evidence:
            st.markdown(f"- {item}")
        if finding.recommendation:
            st.markdown("**Recommendation**")
            st.write(finding.recommendation)


def render_charts(data: dict[str, pd.DataFrame]) -> None:
    sales = data["sales"].copy()
    inventory = data["inventory"].copy()
    marketing = data["marketing"].copy()

    sales["month"] = sales["date"].dt.to_period("M").astype(str)
    monthly_revenue = sales.groupby("month", as_index=False)["revenue"].sum()
    revenue_chart = px.line(
        monthly_revenue,
        x="month",
        y="revenue",
        markers=True,
        title="Monthly Revenue",
    )
    st.plotly_chart(revenue_chart, use_container_width=True)

    chart_cols = st.columns(2)
    with chart_cols[0]:
        product_revenue = sales.groupby("product", as_index=False)["revenue"].sum()
        st.plotly_chart(
            px.bar(product_revenue, x="product", y="revenue", title="Revenue by Product"),
            use_container_width=True,
        )

    with chart_cols[1]:
        stockouts = inventory.groupby("product", as_index=False)["stockout"].sum()
        st.plotly_chart(
            px.bar(stockouts, x="product", y="stockout", title="Stockouts by Product"),
            use_container_width=True,
        )

    marketing["conversion_rate"] = marketing["conversions"] / marketing["clicks"]
    region_conversion = marketing.groupby("region", as_index=False)["conversion_rate"].mean()
    st.plotly_chart(
        px.bar(
            region_conversion,
            x="region",
            y="conversion_rate",
            title="Average Conversion Rate by Region",
        ),
        use_container_width=True,
    )


st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 2rem;
            max-width: 1280px;
        }
        .metric-card {
            border: 1px solid #d8dee9;
            border-radius: 8px;
            padding: 12px 14px;
            background: #f8fafc;
            font-size: 1.05rem;
            min-height: 48px;
        }
        .timeline-step {
            border-left: 3px solid #2563eb;
            padding: 4px 0 12px 14px;
            margin-left: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("BoardroomIQ")
st.caption("Autonomous multi-agent business intelligence with debate, verification, and evidence-based recommendations.")

with st.sidebar:
    st.header("Data Room")
    use_sample = st.toggle("Use sample business data", value=True)
    uploaded = {}
    if not use_sample:
        uploaded["sales"] = st.file_uploader("sales.csv", type=["csv"])
        uploaded["customers"] = st.file_uploader("customers.csv", type=["csv"])
        uploaded["inventory"] = st.file_uploader("inventory.csv", type=["csv"])
        uploaded["marketing"] = st.file_uploader("marketing.csv", type=["csv"])

    st.divider()
    st.write("Agents")
    st.caption("Planner, Finance, Marketing, Operations, Risk, Debate, Verification, Judge, Forecast, CEO")

question = st.text_input(
    "Board question",
    value="Why did revenue drop this quarter and what should we do?",
)

if use_sample:
    data = read_sample_data()
else:
    data = normalize_uploads(uploaded)

ready = {"sales", "customers", "inventory", "marketing"}.issubset(data.keys())

if not ready:
    st.info("Upload all four datasets to start the board meeting.")
    st.stop()

if st.button("Run Board Meeting", type="primary", use_container_width=True):
    report = run_boardroom_analysis(question, data)
    st.session_state["report"] = report
    st.session_state["data"] = data

if "report" not in st.session_state:
    st.info("Run the board meeting to generate agent findings and executive recommendations.")
    st.stop()

report = st.session_state["report"]
data = st.session_state["data"]

st.success("Board meeting completed.")

summary_cols = st.columns(3)
primary = report.ranked_causes[0]
forecast = report.forecast
with summary_cols[0]:
    metric_card("Top Cause", primary.agent)
with summary_cols[1]:
    metric_card("Top Confidence", f"{primary.confidence}%")
with summary_cols[2]:
    metric_card("Forecast Risk", forecast.risk)

tabs = st.tabs(["CEO Summary", "Timeline", "Agents", "Debate & Verification", "Forecast", "Evidence Charts"])

with tabs[0]:
    st.header("CEO Summary")
    st.write(report.ceo_summary)
    st.subheader("Ranked Causes")
    for index, finding in enumerate(report.ranked_causes, start=1):
        st.markdown(f"**{index}. {finding.agent}** — {finding.confidence}% confidence")
        st.write(finding.claim)

with tabs[1]:
    st.header("Board Meeting Timeline")
    for step in report.timeline:
        st.markdown(f"<div class='timeline-step'>{step}</div>", unsafe_allow_html=True)

with tabs[2]:
    st.header("Specialist Agent Findings")
    for finding in report.findings:
        render_finding(finding)

with tabs[3]:
    debate_col, verification_col = st.columns(2)
    with debate_col:
        st.header("Debate")
        for item in report.debate:
            with st.container(border=True):
                st.subheader(item.target_agent)
                st.markdown(f"**Challenge:** {item.challenge}")
                st.markdown(f"**Response:** {item.response}")
    with verification_col:
        st.header("Verification")
        for item in report.verification:
            with st.container(border=True):
                st.subheader(item.agent)
                st.metric("Status", item.status)
                st.write(item.rationale)

with tabs[4]:
    st.header("Forecast Agent")
    render_finding(report.forecast)

with tabs[5]:
    st.header("Evidence Charts")
    render_charts(data)
