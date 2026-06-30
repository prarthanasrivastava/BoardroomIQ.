import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Brain,
  CheckCircle2,
  ChevronRight,
  LineChart,
  MessageSquareQuote,
  ShieldCheck,
  Sparkles,
  Upload,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart as ReLineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./styles.css";

const API_URL = "http://localhost:8000/api/analyze/sample";
const UPLOAD_API_URL = "http://localhost:8000/api/analyze/upload";

const agentIcons = {
  "Data Profiler Agent": Sparkles,
  "Customer / Onboarding Agent": Upload,
  "Flexible Finance Agent": BarChart3,
  "Flexible Marketing Agent": Activity,
  "Flexible Trend Agent": LineChart,
  "Finance Agent": BarChart3,
  "Marketing Agent": Activity,
  "Operations Agent": ShieldCheck,
  "Risk Agent": AlertTriangle,
  "Forecast Agent": LineChart,
};

const chartColors = ["#1f6feb", "#0f766e", "#b45309", "#be123c"];

function MetricPill({ label, value, tone = "neutral" }) {
  return (
    <div className={`metric-pill ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ConfidenceBar({ value }) {
  return (
    <div className="confidence-wrap" aria-label={`Confidence ${value}%`}>
      <div className="confidence-track">
        <div className="confidence-fill" style={{ width: `${value}%` }} />
      </div>
      <span>{value}%</span>
    </div>
  );
}

function FindingCard({ finding, rank }) {
  const Icon = agentIcons[finding.agent] || Brain;
  return (
    <article className="finding-card">
      <div className="finding-head">
        <div className="agent-title">
          <div className="agent-icon">
            <Icon size={19} />
          </div>
          <div>
            <span className="rank-label">Rank {rank}</span>
            <h3>{finding.agent}</h3>
          </div>
        </div>
        <MetricPill label="Risk" value={finding.risk} tone={finding.risk === "High" ? "risk" : "neutral"} />
      </div>
      <p className="claim">{finding.claim}</p>
      <ConfidenceBar value={finding.confidence} />
      <div className="evidence-list">
        {finding.evidence.map((item) => (
          <div className="evidence-item" key={item}>
            <CheckCircle2 size={16} />
            <span>{item}</span>
          </div>
        ))}
      </div>
      <div className="recommendation">
        <span>Recommendation</span>
        <p>{finding.recommendation}</p>
      </div>
    </article>
  );
}

function Timeline({ steps }) {
  return (
    <section className="panel timeline-panel">
      <div className="section-title">
        <Sparkles size={18} />
        <h2>Board Meeting Timeline</h2>
      </div>
      <div className="timeline">
        {steps.map((step, index) => (
          <div className="timeline-row" key={`${step}-${index}`}>
            <div className="timeline-index">{String(index + 1).padStart(2, "0")}</div>
            <div className="timeline-copy">{step}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function DebateVerification({ report }) {
  return (
    <section className="split-grid">
      <div className="panel">
        <div className="section-title">
          <MessageSquareQuote size={18} />
          <h2>Debate</h2>
        </div>
        {report.debate.map((item) => (
          <div className="debate-item" key={item.target_agent}>
            <strong>{item.target_agent}</strong>
            <p>{item.challenge}</p>
            <span>{item.response}</span>
          </div>
        ))}
      </div>
      <div className="panel">
        <div className="section-title">
          <ShieldCheck size={18} />
          <h2>Verification</h2>
        </div>
        {report.verification.map((item) => (
          <div className="verify-item" key={item.agent}>
            <div>
              <strong>{item.agent}</strong>
              <p>{item.rationale}</p>
            </div>
            <span>{item.status}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function Charts({ report }) {
  const rankingData = report.ranked_causes.map((item) => ({
    agent: item.agent.replace(" Agent", ""),
    confidence: item.confidence,
  }));

  const forecast = report.forecast.metrics || {};
  const hasRevenueForecast =
    Number.isFinite(forecast.current_month_revenue) &&
    Number.isFinite(forecast.projected_next_month_revenue);
  const hasVolumeTrend =
    Number.isFinite(forecast.previous_count) &&
    Number.isFinite(forecast.current_count);
  const forecastData = hasRevenueForecast
    ? [
        { label: "Current", value: Math.round(forecast.current_month_revenue) },
        { label: "Projected", value: Math.round(forecast.projected_next_month_revenue) },
      ]
    : [
        { label: "Previous", value: Math.round(forecast.previous_count || 0) },
        { label: "Current", value: Math.round(forecast.current_count || 0) },
      ];

  return (
    <section className="split-grid">
      <div className="panel chart-panel">
        <div className="section-title">
          <BarChart3 size={18} />
          <h2>Cause Ranking</h2>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={rankingData}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="agent" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Bar dataKey="confidence" radius={[6, 6, 0, 0]}>
              {rankingData.map((_, index) => (
                <Cell key={index} fill={chartColors[index % chartColors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="panel chart-panel">
        <div className="section-title">
          <LineChart size={18} />
          <h2>{hasRevenueForecast ? "Revenue Forecast" : "Volume Trend"}</h2>
        </div>
        {hasRevenueForecast || hasVolumeTrend ? (
          <ResponsiveContainer width="100%" height={260}>
            <ReLineChart data={forecastData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#0f766e" strokeWidth={3} dot={{ r: 5 }} />
            </ReLineChart>
          </ResponsiveContainer>
        ) : (
          <div className="empty-chart">Upload a file with dates to unlock timeline forecasting.</div>
        )}
      </div>
    </section>
  );
}

function DatasetProfiles({ profiles = [] }) {
  if (!profiles.length) return null;
  return (
    <section className="panel profile-panel">
      <div className="section-title">
        <Upload size={18} />
        <h2>Detected Dataset Profile</h2>
      </div>
      <div className="profile-grid">
        {profiles.map((profile) => (
          <article className="profile-card" key={profile.name}>
            <div>
              <span>{profile.name}</span>
              <strong>{profile.rows} rows</strong>
            </div>
            <p>{profile.columns.slice(0, 8).join(", ")}{profile.columns.length > 8 ? "..." : ""}</p>
            <div className="profile-tags">
              {!!profile.date_columns.length && <em>Dates</em>}
              {!!profile.possible_conversion_columns.length && <em>Conversions</em>}
              {!!profile.possible_revenue_columns.length && <em>Revenue</em>}
              {!!profile.possible_spend_columns.length && <em>CAC-ready</em>}
              {!!profile.possible_source_columns.length && <em>Sources</em>}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function DecisionBrief({ report }) {
  const primary = report.ranked_causes?.[0];
  const secondary = report.ranked_causes?.[1];
  const forecast = report.forecast;

  if (!primary) return null;

  return (
    <section className="ceo-band">
      <div className="brief-heading">
        <span>CEO Decision Brief</span>
        <h2>{primary.claim}</h2>
      </div>
      <div className="brief-grid">
        <article>
          <span>Primary Cause</span>
          <strong>{primary.agent}</strong>
          <p>{primary.confidence}% confidence</p>
        </article>
        <article>
          <span>Next Move</span>
          <strong>{primary.recommendation}</strong>
        </article>
        <article>
          <span>Watch Signal</span>
          <strong>{secondary?.agent || forecast?.agent || "Forecast"}</strong>
          <p>{forecast?.risk || primary.risk} risk</p>
        </article>
      </div>
      <details className="full-summary">
        <summary>View full executive summary</summary>
        <p>{report.ceo_summary}</p>
      </details>
    </section>
  );
}

function App() {
  const [question, setQuestion] = useState("Why did revenue drop this quarter and what should we do?");
  const [mode, setMode] = useState("sample");
  const [files, setFiles] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runAnalysis = async () => {
    setLoading(true);
    setError("");
    try {
      let response;
      if (mode === "upload") {
        if (!files.length) {
          throw new Error("Upload at least one CSV or Excel file before running the board meeting.");
        }
        const formData = new FormData();
        formData.append("question", question);
        files.forEach((file) => formData.append("files", file));
        response = await fetch(UPLOAD_API_URL, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
        });
      }
      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail || "The board meeting API did not respond successfully.");
      }
      setReport(await response.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAnalysis();
  }, []);

  const topCause = report?.ranked_causes?.[0];
  const secondary = report?.ranked_causes?.[1];
  const forecastRisk = report?.forecast?.risk || "Pending";
  const profiles = report?.metadata?.profiles || [];

  const statCards = useMemo(
    () => [
      { label: "Top Cause", value: topCause?.agent || "Analyzing" },
      { label: "Confidence", value: topCause ? `${topCause.confidence}%` : "--" },
      { label: "Secondary Signal", value: secondary?.agent || "--" },
      { label: "Forecast Risk", value: forecastRisk },
    ],
    [topCause, secondary, forecastRisk],
  );

  return (
    <main>
      <header className="hero">
        <nav>
          <div className="brand-mark">
            <Brain size={22} />
            <span>BoardroomIQ</span>
          </div>
          <div className="nav-status">
            <span className="status-dot" />
            Agent board online
          </div>
        </nav>

        <div className="hero-grid">
          <section className="hero-copy">
            <span className="eyebrow">Agentic business intelligence</span>
            <h1>AI board meetings for business decisions.</h1>
            <p>
              Upload business data, let specialist agents analyze it, and get a verified decision brief with evidence.
            </p>
          </section>

          <section className="control-panel">
            <div className="upload-strip">
              <Upload size={18} />
              <span>{mode === "sample" ? "Sample business dataset loaded" : "Upload CSV or Excel data"}</span>
            </div>
            <div className="mode-toggle">
              <button className={mode === "sample" ? "active" : ""} onClick={() => setMode("sample")} type="button">
                Sample Demo
              </button>
              <button className={mode === "upload" ? "active" : ""} onClick={() => setMode("upload")} type="button">
                Upload Data
              </button>
            </div>
            {mode === "upload" && (
              <div className="file-drop">
                <input
                  id="business-files"
                  type="file"
                  multiple
                  accept=".csv,.xlsx,.xls"
                  onChange={(event) => setFiles(Array.from(event.target.files || []))}
                />
                <label htmlFor="business-files">Choose CSV or Excel files</label>
                <p>{files.length ? files.map((file) => file.name).join(", ") : "No files selected yet."}</p>
              </div>
            )}
            <label htmlFor="question">Board question</label>
            <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} />
            <button onClick={runAnalysis} disabled={loading}>
              {loading ? "Board meeting running..." : "Run Board Meeting"}
              <ChevronRight size={18} />
            </button>
            {error && <p className="error">{error}</p>}
          </section>
        </div>
      </header>

      <section className="stats-grid">
        {statCards.map((card) => (
          <div className="stat-card" key={card.label}>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
          </div>
        ))}
      </section>

      {report && (
        <>
          <DecisionBrief report={report} />

          <DatasetProfiles profiles={profiles} />

          <section className="findings-grid">
            {report.ranked_causes.map((finding, index) => (
              <FindingCard finding={finding} rank={index + 1} key={finding.agent} />
            ))}
          </section>

          <Timeline steps={report.timeline} />
          <DebateVerification report={report} />

          <section className="panel forecast-panel">
            <div className="section-title">
              <LineChart size={18} />
              <h2>Forecast Agent</h2>
            </div>
            <FindingCard finding={report.forecast} rank="F" />
          </section>

          <Charts report={report} />
        </>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
