
import { useEffect, useState } from "react";

import {
  Activity,
  MessageSquare,
  ThumbsDown,
  Users,
  RefreshCw,
  Search,
  Sparkles,
  AlertCircle,
  Star,
} from "lucide-react";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

import {
  getAnalyticsOverview,
  analyzeVOC,
} from "./services/api";

import "./App.css";

const COLORS = ["#16a34a", "#ef4444", "#94a3b8"];

// ==========================================
// REUSABLE KPI CARD
// ==========================================

function StatCard({ title, value, subtitle, icon: Icon }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{title}</span>
        <Icon size={21} />
      </div>

      <h2>{value}</h2>
      <p>{subtitle}</p>
    </div>
  );
}

// ==========================================
// MAIN APPLICATION
// ==========================================

function App() {
  // Overview state
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // AI analysis state
  const [query, setQuery] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  // ==========================================
  // FETCH OVERVIEW ANALYTICS
  // ==========================================

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getAnalyticsOverview();

      setAnalytics(data);
    } catch (err) {
      console.error("Analytics API error:", err);

      setError(
        "Unable to load analytics. Please check whether the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  // ==========================================
  // NATURAL LANGUAGE ANALYSIS
  // ==========================================

  const handleAnalysis = async () => {
    if (!query.trim()) {
      setAnalysisError("Please enter a question to analyse.");
      return;
    }

    try {
      setAnalysisLoading(true);
      setAnalysisError("");
      setAnalysis(null);

      const result = await analyzeVOC(query.trim());

      setAnalysis(result);
    } catch (err) {
      console.error("VOC analysis API error:", err);

      setAnalysisError(
        err.response?.data?.detail ||
          "Unable to complete the analysis. Please try again."
      );
    } finally {
      setAnalysisLoading(false);
    }
  };

  // ==========================================
  // LOADING AND ERROR SCREENS
  // ==========================================

  if (loading) {
    return (
      <div className="status-screen">
        Loading VOC Intelligence 360...
      </div>
    );
  }

  if (error) {
    return (
      <div className="status-screen">
        <p>{error}</p>
        <button onClick={fetchAnalytics}>Try again</button>
      </div>
    );
  }

  if (!analytics) return null;

  // ==========================================
  // OVERVIEW DATA
  // ==========================================

  const sentimentData = analytics.sentiment_distribution || [];
  const sourceData = analytics.source_distribution || [];

  // ==========================================
  // DYNAMIC SQL RESULT PROCESSING
  // ==========================================

  const sqlRows = Array.isArray(analysis?.sql_results)
    ? analysis.sql_results
    : [];

  const sqlColumns =
    sqlRows.length > 0
      ? Object.keys(sqlRows[0])
      : [];

  // Identify a suitable category column
  const labelKey =
    [
      "sentiment",
      "subtheme",
      "explanation",
      "retailer_name",
      "brand_name",
      "product_name",
      "data_source_type",
    ].find((key) => sqlColumns.includes(key)) ||
    sqlColumns.find(
      (key) => typeof sqlRows[0]?.[key] === "string"
    );

  // Identify a numeric column for chart values
  const valueKey = sqlColumns.find(
    (key) => typeof sqlRows[0]?.[key] === "number"
  );

  // Build chart data dynamically
  const chartData =
    labelKey && valueKey
      ? sqlRows.map((item) => ({
          label: String(item[labelKey] ?? "Other"),
          value: item[valueKey],
        }))
      : [];

  // ==========================================
  // SOURCE DISTRIBUTION DATA
  // ==========================================

  const analysisSourceData = (
    analysis?.source_distribution || []
  ).map((item) => ({
    ...item,
    source: item.source,
    count: item.unique_interactions,
  }));

  // ==========================================
  // DASHBOARD UI
  // ==========================================

  return (
    <div className="dashboard">

      {/* NAVBAR */}

      <header className="navbar">
        <div>
          <h1>VOC Intelligence 360</h1>
          <p>Voice of Customer Intelligence Platform</p>
        </div>

        <button
          className="refresh-btn"
          onClick={fetchAnalytics}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </header>

      <main className="dashboard-content">

        {/* ==================================
            CUSTOMER FEEDBACK OVERVIEW
        ================================== */}

        <section className="welcome-section">
          <div>
            <h2>Customer Feedback Overview</h2>

            <p>
              Understand customer sentiment, feedback trends, and
              distribution across sources.
            </p>
          </div>

          <div className="period">
            <span>Analysis Period</span>

            <strong>
              {new Date(
                analytics.analysis_period.start
              ).toLocaleDateString()}

              {" – "}

              {new Date(
                analytics.analysis_period.end
              ).toLocaleDateString()}
            </strong>
          </div>
        </section>

        {/* KPI CARDS */}

        <section className="stats-grid">
          <StatCard
            title="Total Feedback"
            value={analytics.total_feedback.toLocaleString()}
            subtitle="Total feedback records"
            icon={MessageSquare}
          />

          <StatCard
            title="Unique Reviews"
            value={analytics.unique_reviews.toLocaleString()}
            subtitle="Distinct customer review IDs"
            icon={Users}
          />

          <StatCard
            title="Negative Feedback"
            value={analytics.negative_feedback.toLocaleString()}
            subtitle="Records with negative sentiment"
            icon={ThumbsDown}
          />

          <StatCard
            title="Negative Sentiment"
            value={`${analytics.negative_sentiment_percentage}%`}
            subtitle="Share of all feedback records"
            icon={Activity}
          />
        </section>

        {/* ==================================
            OVERVIEW CHARTS
        ================================== */}

        <section className="charts-grid">

          {/* SENTIMENT DISTRIBUTION */}

          <div className="chart-card">
            <div className="chart-heading">
              <h3>Sentiment Distribution</h3>
              <p>
                Breakdown of customer feedback by sentiment
              </p>
            </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentData}
                    dataKey="count"
                    nameKey="sentiment"
                    cx="50%"
                    cy="50%"
                    outerRadius={110}
                    innerRadius={65}
                    paddingAngle={3}
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(1)}%`
                    }
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell
                        key={entry.sentiment}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>

                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* FEEDBACK BY SOURCE */}

          <div className="chart-card">
            <div className="chart-heading">
              <h3>Feedback by Source</h3>
              <p>
                Number of feedback records from each source
              </p>
            </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sourceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="source" />
                  <YAxis />
                  <Tooltip />

                  <Bar
                    dataKey="count"
                    fill="#6366f1"
                    radius={[6, 6, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </section>

        {/* SENTIMENT SUMMARY TABLE */}

        <section className="table-card">
          <h3>Sentiment Summary</h3>

          <table>
            <thead>
              <tr>
                <th>Sentiment</th>
                <th>Feedback Count</th>
                <th>Percentage</th>
              </tr>
            </thead>

            <tbody>
              {sentimentData.map((item) => (
                <tr key={item.sentiment}>
                  <td>{item.sentiment}</td>
                  <td>{item.count.toLocaleString()}</td>
                  <td>{item.percentage}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* ==================================
            AI-POWERED ANALYSIS
        ================================== */}

        <section className="ai-section">

          <div className="ai-heading">
            <div>
              <span className="ai-eyebrow">
                <Sparkles size={15} />
                AI-POWERED INTELLIGENCE
              </span>

              <h2>Ask Your Customer Data</h2>

              <p>
                Ask questions in natural language and let our AI agents
                uncover customer insights.
              </p>
            </div>
          </div>

          {/* QUERY INPUT */}

          <div className="query-box">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Example: Why are customers complaining about Microsoft Surface battery life?"
              rows={3}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleAnalysis();
                }
              }}
            />

            <div className="query-actions">
              <span>
                Press Enter to analyse · Shift + Enter for a new line
              </span>

              <button
                className="analyze-btn"
                onClick={handleAnalysis}
                disabled={analysisLoading}
              >
                {analysisLoading ? (
                  <>
                    <RefreshCw size={16} className="spin" />
                    Analysing...
                  </>
                ) : (
                  <>
                    <Search size={16} />
                    Analyse
                  </>
                )}
              </button>
            </div>
          </div>

          {/* SUGGESTED QUESTIONS */}

          <div className="suggested-queries">
            <span>Try asking:</span>

            {[
              "Why are customers complaining about Microsoft Surface battery life?",
              "Compare Microsoft Surface complaints across Best Buy, Amazon and Currys.",
              "What do customers think about Copilot AI?",
            ].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setQuery(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>

          {/* ANALYSIS ERROR */}

          {analysisError && (
            <div className="analysis-error">
              <AlertCircle size={18} />
              {analysisError}
            </div>
          )}

          {/* ANALYSIS LOADING */}

          {analysisLoading && (
            <div className="analysis-loading">
              <div className="loader"></div>

              <h3>Analysing customer feedback...</h3>

              <p>
                Our AI agents are querying the database, extracting
                customer voices and generating insights.
              </p>
            </div>
          )}

          {/* ==================================
              ANALYSIS RESULTS
          ================================== */}

          {analysis && (
            <div className="analysis-results">
              {analysis.intent === "greeting" ? (
                <div className="result-card executive-card">
                  <h3>
                    <Sparkles size={19} />
                    VOC Intelligence 360
                  </h3>

                  <p>
                    {analysis.final_answer ||
                      "Hello! Welcome to VOC Intelligence 360. How can I help you?"}
                  </p>
                </div>
              ) : (
                <>
                  <div className="results-title">
                <div>
                  <span className="ai-eyebrow">
                    ANALYSIS RESULTS
                  </span>

                  <h2>Your VOC Intelligence Report</h2>

                  <p>{analysis.query}</p>
                </div>
              </div>

              {/* SYNTHESIS ERROR */}

              {analysis.errors?.synthesis && (
                <div className="analysis-error">
                
                  <AlertCircle size={18} />
                  Executive synthesis unavailable. Other analysis
                  results are shown below.
                </div>
              )}

              {/* EXECUTIVE SUMMARY */}

              <div className="result-card executive-card">
                <h3>
                  <Sparkles size={19} />
                  Executive Summary
                </h3>

                <p>
                  {analysis.executive_summary ||
                    "No executive summary available."}
                </p>
              </div>

              {/* FINDINGS AND RECOMMENDATIONS */}

              <div className="insights-grid">

                <div className="result-card">
                  <h3>Key Findings</h3>

                  {analysis.key_findings?.length > 0 ? (
                    <ul className="insight-list">
                      {analysis.key_findings.map(
                        (finding, index) => (
                          <li key={index}>{finding}</li>
                        )
                      )}
                    </ul>
                  ) : (
                    <p className="empty-text">
                      No key findings available.
                    </p>
                  )}
                </div>

                <div className="result-card">
                  <h3>Recommendations</h3>

                  {analysis.recommendations?.length > 0 ? (
                    <ul className="insight-list recommendations">
                      {analysis.recommendations.map(
                        (item, index) => (
                          <li key={index}>{item}</li>
                        )
                      )}
                    </ul>
                  ) : (
                    <p className="empty-text">
                      No recommendations available.
                    </p>
                  )}
                </div>

              </div>

              {/* ==================================
                  DYNAMIC SQL ANALYSIS BREAKDOWN
              ================================== */}

              <div className="result-card">
                <h3>Analysis Breakdown</h3>

                {sqlRows.length > 0 ? (
                  <>

                    {/* DYNAMIC CHART */}

                    {chartData.length > 0 && (
                      <div className="analysis-chart">
                        <ResponsiveContainer
                          width="100%"
                          height="100%"
                        >
                          <BarChart
                            data={chartData}
                            layout="vertical"
                            margin={{
                              left: 20,
                              right: 25,
                            }}
                          >
                            <CartesianGrid
                              strokeDasharray="3 3"
                            />

                            <XAxis type="number" />

                            <YAxis
                              type="category"
                              dataKey="label"
                              width={170}
                              tick={{ fontSize: 11 }}
                            />

                            <Tooltip />

                            <Bar
                              dataKey="value"
                              name={valueKey}
                              fill="#6366f1"
                              radius={[0, 5, 5, 0]}
                            />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    {/* DYNAMIC SQL RESULTS TABLE */}

                    <div className="table-scroll">
                      <table>
                        <thead>
                          <tr>
                            {sqlColumns.map((column) => (
                              <th key={column}>
                                {column.replaceAll("_", " ")}
                              </th>
                            ))}
                          </tr>
                        </thead>

                        <tbody>
                          {sqlRows.map((item, index) => (
                            <tr key={index}>
                              {sqlColumns.map((column) => (
                                <td key={column}>
                                  {String(item[column] ?? "—")}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                  </>
                ) : (
                  <p className="empty-text">
                    No SQL analysis results available.
                  </p>
                )}
              </div>

              {/* ==================================
                  CUSTOMER QUOTES
              ================================== */}

              <div className="result-card">
                <h3>Customer Voice</h3>

                {analysis.customer_quotes?.length > 0 ? (
                  <div className="quotes-grid">

                    {analysis.customer_quotes.map(
                      (quote, index) => (
                        <div
                          className="quote-card"
                          key={quote.uuid || index}
                        >
                          <div className="quote-top">

                            <span className="source-tag">
                              {quote.data_source_type || "Unknown source"}
                            </span>

                            <span className="rating">
                              <Star
                                size={14}
                                fill="#f59e0b"
                                color="#f59e0b"
                              />

                              {quote.customer_rating ?? "N/A"}
                            </span>

                          </div>

                          <p className="quote-text">
                            "{quote.customer_voice}"
                          </p>

                          <div className="quote-footer">
                            <strong>
                              {quote.retailer_name || "Unknown source"}
                            </strong>

                            <span>
                              {quote.product_name}
                            </span>
                          </div>
                        </div>
                      )
                    )}

                  </div>
                ) : (
                  <p className="empty-text">
                    No customer quotes available.
                  </p>
                )}
              </div>

              {/* ==================================
                  SOURCE DISTRIBUTION
              ================================== */}

              <div className="result-card">
                <h3>Analysis Source Distribution</h3>

                {analysisSourceData.length > 0 ? (
                  <>

                    {/* SOURCE CHART */}

                    <div className="analysis-chart">
                      <ResponsiveContainer
                        width="100%"
                        height="100%"
                      >
                        <BarChart data={analysisSourceData}>
                          <CartesianGrid
                            strokeDasharray="3 3"
                          />

                          <XAxis dataKey="source" />
                          <YAxis />
                          <Tooltip />

                          <Bar
                            dataKey="count"
                            name="Unique interactions"
                            fill="#0d9488"
                            radius={[5, 5, 0, 0]}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {/* SOURCE TABLE */}

                    <div className="table-scroll">
                      <table>
                        <thead>
                          <tr>
                            <th>Source</th>
                            <th>Unique Interactions</th>
                            <th>Percentage</th>
                          </tr>
                        </thead>

                        <tbody>
                          {analysisSourceData.map((item) => (
                            <tr key={item.source}>
                              <td>{item.source}</td>

                              <td>
                                {item.unique_interactions}
                              </td>

                              <td>{item.percentage}%</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                  </>
                ) : (
                  <p className="empty-text">
                    No source distribution available.
                  </p>
                )}
                  </div>
                </>
              )}
            </div>
          )}

        </section>
      </main>
    </div>
  );
}

export default App;
