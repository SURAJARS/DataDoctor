import React, { useState } from "react";
import InfoGuide from "./InfoGuide";
import DatasetHealthRadar from "./DatasetHealthRadar";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  HeatMap,
} from "recharts";

// API Base URL - auto-detects production vs development
const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "https://datadoctor.onrender.com/api"
    : "http://localhost:8000/api";

interface HealthScore {
  dataset_health_score: number;
  overall_status: string;
  critical_issues: any[];
  warnings: any[];
  recommendation: string;
}

interface DashboardProps {
  report: any;
}

interface Notification {
  id: string;
  message: string;
  type: "success" | "error" | "info" | "warning";
}

export const Dashboard: React.FC<DashboardProps> = ({ report }) => {
  const [activeTab, setActiveTab] = useState("overview");
  const [showInfoGuide, setShowInfoGuide] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showAutoMLModal, setShowAutoMLModal] = useState(false);
  const [autoMLResults, setAutoMLResults] = useState<any>(null);
  const [autoMLLoading, setAutoMLLoading] = useState(false);
  const [autoMLFile, setAutoMLFile] = useState<File | null>(null);
  const [autoMLTargetColumn, setAutoMLTargetColumn] = useState("");
  const [loading, setLoading] = useState<{
    [key: string]: boolean;
  }>({
    autoFix: false,
    pdf: false,
    email: false,
    riskScore: false,
    drift: false,
    pipeline: false,
  });

  // Add notification
  const addNotification = (
    message: string,
    type: "success" | "error" | "info" | "warning" = "info",
  ) => {
    const id = Date.now().toString();
    setNotifications((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 4000);
  };

  // Handle AutoML Baseline Training
  const handleAutoMLSubmit = async () => {
    try {
      if (!autoMLFile) {
        addNotification("Please select a CSV or Excel file", "error");
        return;
      }

      if (!autoMLTargetColumn.trim()) {
        addNotification("Please enter the target column name", "error");
        return;
      }

      setAutoMLLoading(true);
      addNotification(
        "Training AutoML baseline model... This may take 10-30 seconds",
        "info",
      );

      const formData = new FormData();
      formData.append("file", autoMLFile);
      formData.append("target_column", autoMLTargetColumn);

      const response = await fetch(`${API_BASE_URL}/automl-baseline`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to train model (HTTP ${response.status})`);
      }

      const data = await response.json();
      setAutoMLResults(data);
      addNotification(
        `✓ Model trained! Accuracy: ${(data.performance_metrics?.accuracy * 100 || 0).toFixed(1)}%`,
        "success",
      );
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to train model";
      addNotification(`✗ AutoML Error: ${errorMessage}`, "error");
    } finally {
      setAutoMLLoading(false);
    }
  };

  // Auto-Fix Dataset
  const handleAutoFix = async () => {
    try {
      setLoading((prev) => ({ ...prev, autoFix: true }));
      addNotification(
        "Starting auto-fix process... This may take a moment.",
        "info",
      );

      const analysisId = (report?.analysis_id as string) || "latest";

      // Call backend API
      const response = await fetch(`${API_BASE_URL}/auto-fix`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_id: analysisId }),
      });

      if (!response.ok) {
        throw new Error("Failed to auto-fix dataset");
      }

      const data = await response.json();

      // Download cleaned CSV file
      if (data?.cleaned_file) {
        addNotification(
          "✓ Dataset auto-fixed! Downloading cleaned file...",
          "success",
        );

        // Trigger file download
        const link = document.createElement("a");
        link.href = `${API_BASE_URL}/download-cleaned/${analysisId}`;
        link.download = data.cleaned_file || `cleaned_${analysisId}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        addNotification("✓ Auto-fix process completed!", "success");
      }
    } catch (error) {
      const errorMessage = String(error).includes("Failed to fetch")
        ? "Could not connect to backend. Make sure server is running on port 8000."
        : String(error);
      addNotification(`✗ Auto-fix error: ${errorMessage}`, "error");
    } finally {
      setLoading((prev) => ({ ...prev, autoFix: false }));
    }
  };

  // Download PDF Report
  const handlePDFReport = async () => {
    try {
      setLoading((prev) => ({ ...prev, pdf: true }));
      addNotification("Generating PDF report...", "info");

      const analysisId = (report?.analysis_id as string) || "latest";

      // Call backend API
      const response = await fetch(
        `${API_BASE_URL}/report/download-pdf/${analysisId}`,
      );

      if (!response.ok) throw new Error("Failed to generate PDF");

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `report_${analysisId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      addNotification("✓ PDF report downloaded successfully!", "success");
    } catch (error) {
      const errorMessage = String(error).includes("Failed to fetch")
        ? "Could not connect to backend"
        : String(error);
      addNotification(`✗ Error: ${errorMessage}`, "error");
    } finally {
      setLoading((prev) => ({ ...prev, pdf: false }));
    }
  };

  // Email Report Modal State
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailInput, setEmailInput] = useState("");
  const [includeCSV, setIncludeCSV] = useState(true);

  // Send Email Report
  const handleEmailReport = async (emailAddress?: string) => {
    try {
      setLoading((prev) => ({ ...prev, email: true }));

      const email = emailAddress || emailInput;
      if (!email) {
        addNotification("Please enter an email address", "warning");
        return;
      }

      if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        addNotification("Please enter a valid email address", "error");
        return;
      }

      addNotification(
        "📧 Sending report with PDF and cleaned dataset...",
        "info",
      );

      const analysisId = (report?.analysis_id as string) || "latest";

      // Call backend API
      const response = await fetch(
        `${API_BASE_URL}/report/send-email?email=${encodeURIComponent(email)}&analysis_id=${analysisId}&include_csv=${includeCSV}`,
        { method: "POST" },
      );

      if (!response.ok) throw new Error("Failed to send email");

      addNotification(
        `✓ Report with CSV attachment sent to ${email}!`,
        "success",
      );
      setEmailInput("");
      setShowEmailModal(false);
    } catch (error) {
      const errorMessage = String(error).includes("Failed to fetch")
        ? "Could not connect to backend"
        : String(error);
      addNotification(`✗ Email error: ${errorMessage}`, "error");
    } finally {
      setLoading((prev) => ({ ...prev, email: false }));
    }
  };

  // Risk Score Assessment
  const handleRiskScore = async () => {
    try {
      setLoading((prev) => ({ ...prev, riskScore: true }));
      addNotification("Calculating risk score...", "info");

      const analysisId = (report?.analysis_id as string) || "latest";

      // Call backend API
      const response = await fetch(`${API_BASE_URL}/risk-score/${analysisId}`);

      if (!response.ok) throw new Error("Failed to calculate risk score");

      const data = await response.json();

      // Store risk score data and show in panel
      setRiskScoreData(data);
      setShowRiskScore(true);

      addNotification(
        `✓ Risk Score: ${data?.risk_score} (${data?.risk_level})`,
        "success",
      );
    } catch (error) {
      const errorMessage = String(error).includes("Failed to fetch")
        ? "Could not connect to backend"
        : String(error);
      addNotification(`✗ Risk error: ${errorMessage}`, "error");
    } finally {
      setLoading((prev) => ({ ...prev, riskScore: false }));
    }
  };

  // Data Drift Detection
  const handleDriftCheck = async () => {
    try {
      setLoading((prev) => ({ ...prev, drift: true }));
      addNotification("Analyzing data drift...", "info");

      const analysisId = (report?.analysis_id as string) || "latest";

      // For now, send a POST request with basic analysis
      // In production, this would accept file uploads
      const response = await fetch(`${API_BASE_URL}/drift-detection`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          analysis_id: analysisId,
          use_demo: true,
        }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(
            "Drift detection not available. Upload training dataset for comparison.",
          );
        }
        throw new Error("Failed to detect drift");
      }

      const data = await response.json();

      // Store drift data and show in panel
      setDriftData(data);
      setShowDrift(true);

      addNotification("✓ Drift analysis completed!", "success");
    } catch (error) {
      const errorMessage = String(error).includes("Failed to fetch")
        ? "Could not connect to backend. Make sure the server is running."
        : String(error);
      addNotification(`✗ Drift check: ${errorMessage}`, "error");
    } finally {
      setLoading((prev) => ({ ...prev, drift: false }));
    }
  };

  // Generate ML Pipeline - Store for display on dedicated page
  const [pipelineData, setPipelineData] = useState<any>(null);
  const [showPipeline, setShowPipeline] = useState(false);

  // Drift Detection Results - Store for display on dedicated page
  const [driftData, setDriftData] = useState<any>(null);
  const [showDrift, setShowDrift] = useState(false);

  // Risk Score Results - Store for display on dedicated page
  const [riskScoreData, setRiskScoreData] = useState<any>(null);
  const [showRiskScore, setShowRiskScore] = useState(false);

  // Force re-render on state change
  React.useEffect(() => {
    // This ensures the modal renders properly
  }, [showRiskScore]);

  const handlePipeline = async () => {
    try {
      setLoading((prev) => ({ ...prev, pipeline: true }));
      addNotification("Generating ML pipeline code...", "info");

      const analysisId = (report?.analysis_id as string) || "latest";

      // Call backend API
      const response = await fetch(`${API_BASE_URL}/pipeline/${analysisId}`);

      if (!response.ok) throw new Error("Failed to generate pipeline");

      const data = await response.json();

      // Store pipeline data and show in panel
      setPipelineData(data);
      setShowPipeline(true);

      addNotification(
        "✓ Pipeline generated! View full code in the pipeline panel.",
        "success",
      );
    } catch (error) {
      const errorMessage = String(error).includes("Failed to fetch")
        ? "Could not connect to backend"
        : String(error);
      addNotification(`✗ Pipeline error: ${errorMessage}`, "error");
    } finally {
      setLoading((prev) => ({ ...prev, pipeline: false }));
    }
  };

  // Feature Importance Dry-Run Test
  const handleFeatureImportanceDryRun = async () => {
    try {
      setLoading((prev) => ({ ...prev, pipeline: true }));
      addNotification("Running feature importance dry-run...", "info");

      const analysisId = (report?.analysis_id as string) || "latest";

      // Call backend API
      const response = await fetch(
        `${API_BASE_URL}/feature-importance-dryrun`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ analysis_id: analysisId }),
        },
      );

      if (!response.ok) throw new Error("Failed to run dry-run");

      const data = await response.json();

      const features = data?.feature_importance?.top_features || [];
      const message = data?.message || "Dry-run completed";

      addNotification(
        `✓ ${message} Found ${features.length} ranked features`,
        "success",
      );
    } catch (error) {
      const errorMessage = String(error).includes("Failed to fetch")
        ? "Could not connect to backend"
        : String(error);
      addNotification(`✗ Dry-run error: ${errorMessage}`, "error");
    } finally {
      setLoading((prev) => ({ ...prev, pipeline: false }));
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 70) return "text-blue-600";
    if (score >= 60) return "text-yellow-600";
    if (score >= 50) return "text-orange-600";
    return "text-red-600";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return "bg-green-100";
    if (score >= 70) return "bg-blue-100";
    if (score >= 60) return "bg-yellow-100";
    if (score >= 50) return "bg-orange-100";
    return "bg-red-100";
  };

  const healthScore: HealthScore = report?.health_score || {};
  const mlReadiness = report?.ml_readiness || {};
  const datasetInfo = report?.dataset_info || {};
  const biasAnalysis = report?.bias_analysis || {};
  const featureEngineering = report?.feature_engineering || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Data Doctor Analysis Report
          </h1>
          <p className="text-slate-300">
            Comprehensive dataset quality assessment
          </p>
        </div>

        {/* Main Scores Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Health Score Card */}
          <div
            className={`${getScoreBgColor(healthScore.dataset_health_score)} rounded-lg p-6 shadow-lg group relative`}
          >
            <div className="flex items-start justify-between mb-2">
              <h2 className="text-slate-700 font-semibold">
                Dataset Health Score
              </h2>
              <button
                onClick={() => setShowInfoGuide(true)}
                className="text-slate-500 hover:text-blue-600 opacity-0 group-hover:opacity-100 transition"
                title="Learn about Health Score"
              >
                ⓘ
              </button>
            </div>
            <div
              className={`text-5xl font-bold ${getScoreColor(healthScore.dataset_health_score)} mb-2`}
            >
              {healthScore.dataset_health_score || 0}
            </div>
            <p className="text-slate-600">
              {healthScore.overall_status || "N/A"}
            </p>
            <div className="mt-4 w-full bg-slate-300 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${healthScore.dataset_health_score || 0}%` }}
              />
            </div>
          </div>

          {/* ML Readiness Card */}
          <div
            className={`${getScoreBgColor(mlReadiness.ml_readiness_score)} rounded-lg p-6 shadow-lg group relative`}
          >
            <div className="flex items-start justify-between mb-2">
              <h2 className="text-slate-700 font-semibold">
                ML Readiness Score
              </h2>
              <button
                onClick={() => setShowInfoGuide(true)}
                className="text-slate-500 hover:text-blue-600 opacity-0 group-hover:opacity-100 transition"
                title="Learn about ML Readiness Score"
              >
                ⓘ
              </button>
            </div>
            <div
              className={`text-5xl font-bold ${getScoreColor(mlReadiness.ml_readiness_score)} mb-2`}
            >
              {mlReadiness.ml_readiness_score || 0}
            </div>
            <p className="text-slate-600">
              {mlReadiness.readiness_status || "N/A"}
            </p>
            <div className="mt-4 w-full bg-slate-300 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${mlReadiness.ml_readiness_score || 0}%` }}
              />
            </div>
          </div>

          {/* Dataset Info Card */}
          <div className="bg-slate-700 rounded-lg p-6 shadow-lg text-white">
            <h2 className="font-semibold mb-4">Dataset Information</h2>
            <div className="space-y-2 text-sm">
              <p>
                <span className="text-slate-400">Rows:</span>{" "}
                <span className="font-semibold">
                  {datasetInfo.rows?.toLocaleString()}
                </span>
              </p>
              <p>
                <span className="text-slate-400">Columns:</span>{" "}
                <span className="font-semibold">{datasetInfo.columns}</span>
              </p>
              <p>
                <span className="text-slate-400">File Size:</span>{" "}
                <span className="font-semibold">
                  {datasetInfo.file_size_mb} MB
                </span>
              </p>
              <p>
                <span className="text-slate-400">Type:</span>{" "}
                <span className="font-semibold">
                  {datasetInfo.file_type?.toUpperCase()}
                </span>
              </p>
            </div>
          </div>
        </div>

        {/* Advanced Actions Section */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-white mb-4">
            Advanced Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <button
              onClick={handleAutoFix}
              disabled={loading.autoFix}
              className="bg-gradient-to-br from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-semibold transition shadow-lg transform hover:scale-105"
            >
              {loading.autoFix ? "Loading..." : "✨ Auto-Fix"}
            </button>
            <button
              onClick={handlePDFReport}
              disabled={loading.pdf}
              className="bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-semibold transition shadow-lg transform hover:scale-105"
            >
              {loading.pdf ? "Loading..." : "📄 PDF Report"}
            </button>
            <button
              onClick={() => setShowEmailModal(true)}
              disabled={loading.email}
              className="bg-gradient-to-br from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-semibold transition shadow-lg transform hover:scale-105"
            >
              {loading.email ? "Loading..." : "📧 Email"}
            </button>
            <button
              onClick={handleRiskScore}
              disabled={loading.riskScore}
              className="bg-gradient-to-br from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-semibold transition shadow-lg transform hover:scale-105"
            >
              {loading.riskScore ? "Loading..." : "⚠️ Risk Score"}
            </button>
            <button
              onClick={handleDriftCheck}
              disabled={loading.drift}
              className="bg-gradient-to-br from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-semibold transition shadow-lg transform hover:scale-105"
            >
              {loading.drift ? "Loading..." : "📈 Drift Check"}
            </button>
            <button
              onClick={handlePipeline}
              disabled={loading.pipeline}
              className="bg-gradient-to-br from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-semibold transition shadow-lg transform hover:scale-105"
            >
              {loading.pipeline ? "Loading..." : "🔧 Pipeline"}
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="flex border-b items-center justify-between overflow-x-auto">
            <div className="flex flex-1 overflow-x-auto scrollbar-hide">
              {[
                "Overview",
                "Issues",
                "ML Readiness",
                "Features",
                "Bias",
                "Advanced",
                "Recommendations",
                "Baseline Model",
              ].map((tab) => (
                <button
                  key={tab}
                  onClick={() =>
                    setActiveTab(tab.toLowerCase().replace(" ", "-"))
                  }
                  className={`py-3 px-3 text-center font-medium transition whitespace-nowrap text-sm md:text-base md:px-4 md:py-4 ${
                    activeTab === tab.toLowerCase().replace(" ", "-")
                      ? "bg-blue-600 text-white"
                      : "text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowInfoGuide(true)}
              className="px-3 py-3 md:px-4 md:py-4 text-blue-600 hover:bg-blue-50 font-semibold transition border-l text-sm md:text-base whitespace-nowrap"
              title="Open Information Guide"
            >
              📖 Help & Info
            </button>
          </div>

          <div className="p-8">
            {/* Overview Tab */}
            {activeTab === "overview" && (
              <div className="space-y-6">
                {/* Dataset Health Radar */}
                <div>
                  <DatasetHealthRadar
                    analysisId={(report?.analysis_id as string) || "latest"}
                  />
                </div>

                {/* Key Findings */}
                <div>
                  <h3 className="text-xl font-bold text-slate-800 mb-4">
                    Key Findings
                  </h3>
                  <div className="bg-blue-50 border-l-4 border-blue-600 p-4">
                    <p className="text-slate-700">
                      {healthScore.recommendation}
                    </p>
                  </div>
                </div>

                {/* Missing Values */}
                {report?.analysis_details?.missing_values && (
                  <div>
                    <h4 className="font-semibold text-slate-800 mb-2">
                      Missing Values
                    </h4>
                    <p className="text-slate-600">
                      Total Missing:{" "}
                      {report.analysis_details.missing_values.total_missing}{" "}
                      cells (
                      {
                        report.analysis_details.missing_values
                          .missing_percentage
                      }
                      %)
                    </p>
                  </div>
                )}

                {/* Duplicates */}
                {report?.analysis_details?.duplicates && (
                  <div>
                    <h4 className="font-semibold text-slate-800 mb-2">
                      Duplicates
                    </h4>
                    <p className="text-slate-600">
                      Duplicate Rows:{" "}
                      {report.analysis_details.duplicates.duplicate_rows}(
                      {
                        report.analysis_details.duplicates
                          .duplicate_rows_percentage
                      }
                      %)
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Issues Tab */}
            {activeTab === "issues" && (
              <div>
                <h3 className="text-xl font-bold text-slate-800 mb-4">
                  Detected Issues
                </h3>
                <div className="space-y-3">
                  {healthScore.warnings && healthScore.warnings.length > 0 ? (
                    healthScore.warnings.map((issue: any, idx: number) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-lg border-l-4 ${
                          issue.severity === "critical"
                            ? "bg-red-50 border-red-600"
                            : issue.severity === "high"
                              ? "bg-orange-50 border-orange-600"
                              : "bg-yellow-50 border-yellow-600"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-semibold text-slate-800">
                              {issue.type}
                            </h4>
                            <p className="text-slate-600 text-sm">
                              {issue.description}
                            </p>
                          </div>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              issue.severity === "critical"
                                ? "bg-red-200 text-red-800"
                                : "bg-orange-200 text-orange-800"
                            }`}
                          >
                            {issue.severity?.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500">No issues detected</p>
                  )}
                </div>
              </div>
            )}

            {/* ML Readiness Tab */}
            {activeTab === "ml-readiness" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-bold text-slate-800 mb-4">
                    ML Training Assessment
                  </h3>
                  <div
                    className={`p-4 rounded-lg ${
                      mlReadiness.readiness_status === "NOT_READY"
                        ? "bg-red-50"
                        : mlReadiness.readiness_status === "READY"
                          ? "bg-green-50"
                          : "bg-yellow-50"
                    }`}
                  >
                    <p className="text-slate-700 font-semibold mb-2">
                      Status: {mlReadiness.readiness_status}
                    </p>
                    <p className="text-slate-600">
                      Estimated Training Difficulty:{" "}
                      {
                        mlReadiness.estimated_training_difficulty
                          ?.difficulty_level
                      }
                    </p>
                  </div>
                </div>

                {mlReadiness.critical_blockers &&
                  mlReadiness.critical_blockers.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-slate-800 mb-2">
                        Critical Blockers
                      </h4>
                      {mlReadiness.critical_blockers.map(
                        (blocker: any, idx: number) => (
                          <div
                            key={idx}
                            className="bg-red-50 p-3 rounded mb-2 text-slate-700"
                          >
                            {blocker.description}
                          </div>
                        ),
                      )}
                    </div>
                  )}

                <div>
                  <h4 className="font-semibold text-slate-800 mb-2">
                    Recommendations
                  </h4>
                  {mlReadiness.recommendations &&
                    mlReadiness.recommendations.map(
                      (rec: string, idx: number) => (
                        <div key={idx} className="flex items-start mb-2">
                          <span className="text-green-600 mr-2">✓</span>
                          <span className="text-slate-600">{rec}</span>
                        </div>
                      ),
                    )}
                </div>
              </div>
            )}

            {/* Features Tab */}
            {activeTab === "features" && (
              <div>
                <h3 className="text-xl font-bold text-slate-800 mb-4">
                  Feature Analysis
                </h3>
                {report?.feature_importance?.top_features &&
                report.feature_importance.top_features.length > 0 ? (
                  <div className="space-y-3">
                    <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                      <p className="text-sm text-slate-600">
                        <b>Total Features Analyzed:</b>{" "}
                        {report?.dataset_info?.columns || "N/A"}
                      </p>
                    </div>
                    {report.feature_importance.top_features.map(
                      (feature: any, idx: number) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition"
                        >
                          <div className="flex-1">
                            <span className="font-semibold text-slate-800 block">
                              #{idx + 1}{" "}
                              {feature.feature || `Feature ${idx + 1}`}
                            </span>
                            <span className="text-xs text-slate-500">
                              Importance Score:{" "}
                              {(feature.importance || 0).toFixed(4)}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 ml-4">
                            <div className="w-48 bg-slate-200 rounded-full h-3">
                              <div
                                className="bg-gradient-to-r from-blue-400 to-blue-600 h-3 rounded-full"
                                style={{
                                  width: `${(feature.importance || 0) * 100}%`,
                                }}
                              />
                            </div>
                            <span className="text-sm font-bold text-blue-600 w-12 text-right">
                              {((feature.importance || 0) * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="p-6 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                      <p className="text-slate-700 font-semibold mb-2">
                        Feature Importance Data Not Available
                      </p>
                      <p className="text-slate-600 text-sm mb-4">
                        Run the analysis with a dataset to generate feature
                        importance rankings. This helps identify which features
                        are most valuable for your machine learning models.
                      </p>
                      <button
                        onClick={handleFeatureImportanceDryRun}
                        disabled={loading.pipeline}
                        className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded font-semibold text-sm transition"
                      >
                        {loading.pipeline
                          ? "Testing..."
                          : "🧪 Test Feature Ranking (Dry-Run)"}
                      </button>
                    </div>
                    {report?.analysis_details?.data_types?.numeric_columns && (
                      <div>
                        <h4 className="font-semibold text-slate-800 mb-2">
                          Numeric Features in Dataset
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {report.analysis_details.data_types.numeric_columns
                            .slice(0, 10)
                            .map((col: string, idx: number) => (
                              <span
                                key={idx}
                                className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                              >
                                {col}
                              </span>
                            ))}
                        </div>
                      </div>
                    )}
                    {report?.analysis_details?.data_types
                      ?.categorical_columns && (
                      <div>
                        <h4 className="font-semibold text-slate-800 mb-2">
                          Categorical Features in Dataset
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {report.analysis_details.data_types.categorical_columns
                            .slice(0, 10)
                            .map((col: string, idx: number) => (
                              <span
                                key={idx}
                                className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm"
                              >
                                {col}
                              </span>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Bias Tab */}
            {activeTab === "bias" && (
              <div>
                <h3 className="text-xl font-bold text-slate-800 mb-4">
                  Bias Detection
                </h3>
                <div className="mb-4">
                  <p className="text-slate-600">
                    Risk Level:
                    <span
                      className={`ml-2 font-semibold ${
                        biasAnalysis.bias_risk_level === "Critical"
                          ? "text-red-600"
                          : biasAnalysis.bias_risk_level === "High"
                            ? "text-orange-600"
                            : "text-green-600"
                      }`}
                    >
                      {biasAnalysis.bias_risk_level}
                    </span>
                  </p>
                </div>
                {biasAnalysis.bias_findings &&
                biasAnalysis.bias_findings.length > 0 ? (
                  <div className="space-y-3">
                    {biasAnalysis.bias_findings.map(
                      (finding: any, idx: number) => (
                        <div key={idx} className="p-4 bg-slate-50 rounded-lg">
                          <h4 className="font-semibold text-slate-800">
                            {finding.type}
                          </h4>
                          <p className="text-slate-600 text-sm mt-1">
                            {finding.description}
                          </p>
                          <p className="text-slate-500 text-sm mt-1">
                            Mitigation: {finding.mitigation}
                          </p>
                        </div>
                      ),
                    )}
                  </div>
                ) : (
                  <p className="text-slate-500">No bias findings detected</p>
                )}
              </div>
            )}

            {/* Advanced Features Tab */}
            {activeTab === "advanced" && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-slate-800 mb-4">
                  Advanced Analysis Tools
                </h3>

                {/* Auto-Fix Dataset */}
                <div className="border-l-4 border-green-500 bg-green-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-lg font-bold text-slate-800 mb-2">
                        ✨ Auto-Fix Dataset
                      </h4>
                      <p className="text-slate-600 mb-3">
                        Automatically apply recommended fixes to identified data
                        quality issues. Generates a cleaned CSV file ready for
                        ML pipelines.
                      </p>
                      <ul className="text-sm text-slate-600 space-y-1 mb-4">
                        <li>• Intelligent missing value imputation</li>
                        <li>• Outlier handling and normalization</li>
                        <li>• Duplicate row removal</li>
                        <li>• Format standardization</li>
                      </ul>
                    </div>
                    <button
                      onClick={handleAutoFix}
                      disabled={loading.autoFix}
                      className="bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-semibold transition"
                    >
                      {loading.autoFix ? "Processing..." : "Fix Now"}
                    </button>
                  </div>
                </div>

                {/* Risk Score Assessment */}
                <div className="border-l-4 border-orange-500 bg-orange-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-lg font-bold text-slate-800 mb-2">
                        ⚠️ Risk Score Assessment
                      </h4>
                      <p className="text-slate-600 mb-3">
                        Get a comprehensive risk score indicating dataset
                        quality and ML pipeline compatibility.
                      </p>
                      <ul className="text-sm text-slate-600 space-y-1 mb-4">
                        <li>• Data quality risk scoring</li>
                        <li>• ML compatibility assessment</li>
                        <li>• Critical issue flagging</li>
                        <li>• Remediation roadmap</li>
                      </ul>
                    </div>
                    <button
                      onClick={handleRiskScore}
                      disabled={loading.riskScore}
                      className="bg-orange-600 hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-semibold transition"
                    >
                      {loading.riskScore ? "Assessing..." : "Assess Risk"}
                    </button>
                  </div>
                </div>

                {/* Data Drift Detection */}
                <div className="border-l-4 border-red-500 bg-red-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-lg font-bold text-slate-800 mb-2">
                        📈 Data Drift Detection
                      </h4>
                      <p className="text-slate-600 mb-3">
                        Compare this dataset against a training dataset to
                        detect distribution shifts and data drift.
                      </p>
                      <ul className="text-sm text-slate-600 space-y-1 mb-4">
                        <li>• Distribution comparison</li>
                        <li>• Drift scoring</li>
                        <li>• Feature drift analysis</li>
                        <li>• Covariate shift detection</li>
                      </ul>
                    </div>
                    <button
                      onClick={handleDriftCheck}
                      disabled={loading.drift}
                      className="bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-semibold transition"
                    >
                      {loading.drift ? "Checking..." : "Check Drift"}
                    </button>
                  </div>
                </div>

                {/* ML Pipeline Generator */}
                <div className="border-l-4 border-indigo-500 bg-indigo-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-lg font-bold text-slate-800 mb-2">
                        🔧 ML Pipeline Generator
                      </h4>
                      <p className="text-slate-600 mb-3">
                        Auto-generate production-ready scikit-learn
                        preprocessing pipelines based on your dataset
                        characteristics.
                      </p>
                      <ul className="text-sm text-slate-600 space-y-1 mb-4">
                        <li>• Automatic pipeline generation</li>
                        <li>• Feature scaling and encoding</li>
                        <li>• Missing value handling</li>
                        <li>• Download as Python code</li>
                      </ul>
                    </div>
                    <button
                      onClick={handlePipeline}
                      disabled={loading.pipeline}
                      className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-semibold transition"
                    >
                      {loading.pipeline ? "Generating..." : "Generate"}
                    </button>
                  </div>
                </div>

                {/* Report Generation */}
                <div className="border-l-4 border-blue-500 bg-blue-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-lg font-bold text-slate-800 mb-2">
                        📄 Report Generation & Email
                      </h4>
                      <p className="text-slate-600 mb-3">
                        Generate comprehensive PDF reports of your analysis and
                        email them to stakeholders.
                      </p>
                      <ul className="text-sm text-slate-600 space-y-1 mb-4">
                        <li>• PDF report generation</li>
                        <li>• Email delivery</li>
                        <li>• Visualization included</li>
                        <li>• Audit trail maintained</li>
                      </ul>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handlePDFReport}
                        disabled={loading.pdf}
                        className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-semibold transition"
                      >
                        {loading.pdf ? "Loading..." : "📄 PDF"}
                      </button>
                      <button
                        onClick={() => setShowEmailModal(true)}
                        disabled={loading.email}
                        className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-semibold transition"
                      >
                        {loading.email ? "Loading..." : "📧 Email"}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Recommendations Tab */}
            {activeTab === "recommendations" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-bold text-slate-800 mb-4">
                    Action Items
                  </h3>
                  <div className="space-y-3">
                    {report?.cleaning_recommendations?.cleaning_steps &&
                      report.cleaning_recommendations.cleaning_steps
                        .slice(0, 5)
                        .map((step: any, idx: number) => (
                          <div
                            key={idx}
                            className="p-4 border-l-4 border-blue-600 bg-blue-50 rounded"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-semibold text-slate-800">
                                {step.action}
                              </h4>
                              <span
                                className={`text-xs px-2 py-1 rounded font-semibold ${
                                  step.priority === "Critical"
                                    ? "bg-red-200 text-red-800"
                                    : step.priority === "High"
                                      ? "bg-orange-200 text-orange-800"
                                      : "bg-yellow-200 text-yellow-800"
                                }`}
                              >
                                {step.priority}
                              </span>
                            </div>
                            <p className="text-slate-600 text-sm">
                              {step.reason}
                            </p>
                          </div>
                        ))}
                  </div>
                </div>
              </div>
            )}

            {/* Baseline Model Tab */}
            {activeTab === "baseline-model" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-bold text-slate-800 mb-4">
                    🤖 AutoML Baseline Model
                  </h3>
                  <p className="text-slate-600 mb-4">
                    Upload a dataset with a target column to train an automatic
                    baseline model and get model suggestions.
                  </p>

                  {/* Coming Soon Notice */}
                  <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg p-6">
                    <div className="flex items-start gap-4">
                      <div className="text-3xl">🔬</div>
                      <div>
                        <h4 className="font-semibold text-slate-800 mb-2">
                          AutoML Baseline Engine (Feature Preview)
                        </h4>
                        <p className="text-slate-600 text-sm mb-4">
                          This feature allows you to:
                        </p>
                        <ul className="text-slate-600 text-sm space-y-1 ml-4 list-disc">
                          <li>
                            Train automatic baseline models (RandomForest for
                            classification/regression)
                          </li>
                          <li>
                            Get intelligent model suggestions based on your
                            dataset
                          </li>
                          <li>
                            View confusion matrices for classification problems
                          </li>
                          <li>Analyze feature importance scores</li>
                          <li>
                            See performance metrics (accuracy, precision,
                            recall, F1)
                          </li>
                        </ul>
                        <button
                          onClick={() => setShowAutoMLModal(true)}
                          className="mt-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-2 px-4 rounded-lg font-semibold transition shadow-lg"
                        >
                          🚀 Try AutoML Baseline
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Model Suggestions Card */}
                  <div className="mt-6 bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="font-semibold text-slate-800 mb-4">
                      💡 Recommended Models for Your Dataset
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="border border-green-200 bg-green-50 rounded-lg p-4">
                        <h5 className="font-semibold text-green-900 mb-2">
                          ✓ RandomForest
                        </h5>
                        <p className="text-sm text-green-800">
                          Versatile ensemble method. Great for mixed feature
                          types and capturing nonlinear patterns.
                        </p>
                      </div>
                      <div className="border border-blue-200 bg-blue-50 rounded-lg p-4">
                        <h5 className="font-semibold text-blue-900 mb-2">
                          ✓ LightGBM
                        </h5>
                        <p className="text-sm text-blue-800">
                          Fast gradient boosting. Efficient with large datasets
                          and categorical features.
                        </p>
                      </div>
                      <div className="border border-purple-200 bg-purple-50 rounded-lg p-4">
                        <h5 className="font-semibold text-purple-900 mb-2">
                          ✓ XGBoost
                        </h5>
                        <p className="text-sm text-purple-800">
                          Powerful gradient boosting. Excellent accuracy but
                          slower training.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Drift Detection Results Panel */}
        {showDrift && driftData && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-red-600 to-orange-600">
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    Data Drift Analysis Results
                  </h2>
                  <p className="text-red-100 text-sm mt-1">
                    Comparing dataset distribution with baseline
                  </p>
                </div>
                <button
                  onClick={() => setShowDrift(false)}
                  className="text-white hover:bg-red-700 p-2 rounded transition"
                >
                  ✕
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-auto p-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-slate-600 mb-1">
                      Total Features Analyzed
                    </p>
                    <p className="text-3xl font-bold text-blue-600">
                      {driftData?.drift_report?.total_features_analyzed || 0}
                    </p>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <p className="text-sm text-slate-600 mb-1">
                      Features With Drift
                    </p>
                    <p className="text-3xl font-bold text-red-600">
                      {driftData?.drift_report?.features_with_drift || 0}
                    </p>
                  </div>
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <p className="text-sm text-slate-600 mb-1">
                      Overall Drift Status
                    </p>
                    <p className="text-xl font-bold text-orange-600">
                      {driftData?.drift_report?.overall_drift || "Unknown"}
                    </p>
                  </div>
                </div>

                {/* Drift Summary Details */}
                {driftData?.drift_report?.drift_summary && (
                  <div>
                    <h3 className="text-lg font-bold text-slate-800 mb-3">
                      Feature Drift Details
                    </h3>
                    <div className="space-y-2">
                      {Object.entries(driftData.drift_report.drift_summary)
                        .slice(0, 10)
                        .map(
                          ([feature, details]: [string, any], idx: number) => (
                            <div
                              key={idx}
                              className={`p-3 rounded-lg border-l-4 ${
                                details.drift_detected
                                  ? "bg-red-50 border-red-500"
                                  : "bg-green-50 border-green-500"
                              }`}
                            >
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-semibold text-slate-800">
                                    {feature}
                                  </p>
                                  <p className="text-xs text-slate-600">
                                    KS Statistic:{" "}
                                    {(details.ks_statistic || 0).toFixed(3)} |
                                    P-value: {(details.p_value || 0).toFixed(3)}
                                  </p>
                                </div>
                                <span
                                  className={`px-3 py-1 rounded-full text-sm font-bold ${
                                    details.drift_detected
                                      ? "bg-red-200 text-red-800"
                                      : "bg-green-200 text-green-800"
                                  }`}
                                >
                                  {details.drift_detected
                                    ? "⚠️ Drift"
                                    : "✓ Stable"}
                                </span>
                              </div>
                            </div>
                          ),
                        )}
                    </div>
                  </div>
                )}

                {/* Recommendation */}
                {driftData?.drift_report?.recommendation && (
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                    <p className="font-semibold text-slate-800 mb-1">
                      Recommendation
                    </p>
                    <p className="text-slate-700">
                      {driftData.drift_report.recommendation}
                    </p>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="flex gap-3 p-6 border-t bg-slate-50">
                <button
                  onClick={() => {
                    const summaryText = `Drift Analysis Results\n\nTotal Features: ${driftData?.drift_report?.total_features_analyzed}\nFeatures with Drift: ${driftData?.drift_report?.features_with_drift}\nOverall Status: ${driftData?.drift_report?.overall_drift}\n\nRecommendation: ${driftData?.drift_report?.recommendation}`;
                    navigator.clipboard.writeText(summaryText);
                    addNotification(
                      "✓ Drift analysis results copied to clipboard!",
                      "success",
                    );
                  }}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-semibold transition"
                >
                  📋 Copy Results
                </button>
                <button
                  onClick={() => setShowDrift(false)}
                  className="flex-1 bg-slate-400 hover:bg-slate-500 text-white py-2 px-4 rounded-lg font-semibold transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Risk Score Results Panel */}
        {showRiskScore && riskScoreData && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-orange-600 to-amber-600">
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    Risk Score Assessment
                  </h2>
                  <p className="text-orange-100 text-sm mt-1">
                    Dataset quality risk evaluation
                  </p>
                </div>
                <button
                  onClick={() => setShowRiskScore(false)}
                  className="text-white hover:bg-orange-700 p-2 rounded transition"
                >
                  ✕
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-auto p-6 space-y-6">
                {/* Score Summary Cards */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-orange-50 p-4 rounded-lg border-l-4 border-orange-500">
                    <p className="text-sm text-slate-600 mb-2">Risk Score</p>
                    <p className="text-4xl font-bold text-orange-600">
                      {riskScoreData?.risk_score || 50}
                    </p>
                    <p className="text-xs text-slate-500 mt-2">out of 100</p>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                    <p className="text-sm text-slate-600 mb-2">Risk Level</p>
                    <p className="text-2xl font-bold text-red-600">
                      {riskScoreData?.risk_level || "Unknown"}
                    </p>
                    <p className="text-xs text-slate-500 mt-2">Assessment</p>
                  </div>
                </div>

                {/* Risk Score Interpretation */}
                <div>
                  <h3 className="text-lg font-bold text-slate-800 mb-3">
                    Summary
                  </h3>
                  <div className="bg-slate-50 p-4 rounded-lg border-l-4 border-slate-400">
                    <p className="text-slate-700">
                      {riskScoreData?.summary || "No summary available"}
                    </p>
                  </div>
                </div>

                {/* Risk Level Breakdown */}
                <div>
                  <h3 className="text-lg font-bold text-slate-800 mb-3">
                    Risk Interpretation
                  </h3>
                  <div className="space-y-2">
                    {riskScoreData?.risk_score >= 80 && (
                      <div className="p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
                        <p className="font-semibold text-green-800">
                          ✓ Low Risk
                        </p>
                        <p className="text-sm text-green-700">
                          Dataset is healthy and suitable for ML models
                        </p>
                      </div>
                    )}
                    {riskScoreData?.risk_score >= 60 &&
                      riskScoreData?.risk_score < 80 && (
                        <div className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                          <p className="font-semibold text-blue-800">
                            ℹ Medium Risk
                          </p>
                          <p className="text-sm text-blue-700">
                            Some data quality issues exist but are manageable
                          </p>
                        </div>
                      )}
                    {riskScoreData?.risk_score >= 40 &&
                      riskScoreData?.risk_score < 60 && (
                        <div className="p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
                          <p className="font-semibold text-yellow-800">
                            ⚠ High Risk
                          </p>
                          <p className="text-sm text-yellow-700">
                            Significant data quality issues require attention
                          </p>
                        </div>
                      )}
                    {riskScoreData?.risk_score < 40 && (
                      <div className="p-3 bg-red-50 rounded-lg border-l-4 border-red-500">
                        <p className="font-semibold text-red-800">
                          🔴 Critical Risk
                        </p>
                        <p className="text-sm text-red-700">
                          Critical data quality issues must be resolved before
                          ML modeling
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Recommendations */}
                {riskScoreData?.recommendations &&
                  riskScoreData.recommendations.length > 0 && (
                    <div>
                      <h3 className="text-lg font-bold text-slate-800 mb-3">
                        Recommendations
                      </h3>
                      <ul className="space-y-2">
                        {riskScoreData.recommendations
                          .slice(0, 5)
                          .map((rec: string, idx: number) => (
                            <li
                              key={idx}
                              className="flex items-start gap-2 p-2 bg-blue-50 rounded"
                            >
                              <span className="text-blue-600 font-bold mt-0.5">
                                →
                              </span>
                              <span className="text-slate-700 text-sm">
                                {rec}
                              </span>
                            </li>
                          ))}
                      </ul>
                    </div>
                  )}
              </div>

              {/* Footer */}
              <div className="flex gap-3 p-6 border-t bg-slate-50">
                <button
                  onClick={() => {
                    const summaryText = `Risk Score Assessment\n\nRisk Score: ${riskScoreData?.risk_score}/100\nRisk Level: ${riskScoreData?.risk_level}\n\nSummary: ${riskScoreData?.summary}\n\nRecommendations:\n${(riskScoreData?.recommendations || []).join("\n")}`;
                    navigator.clipboard.writeText(summaryText);
                    addNotification(
                      "✓ Risk score details copied to clipboard!",
                      "success",
                    );
                  }}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-semibold transition"
                >
                  📋 Copy Results
                </button>
                <button
                  onClick={() => setShowRiskScore(false)}
                  className="flex-1 bg-slate-400 hover:bg-slate-500 text-white py-2 px-4 rounded-lg font-semibold transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Pipeline Code Panel */}
        {showPipeline && pipelineData && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-indigo-600 to-blue-600">
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    Generated ML Pipeline Code
                  </h2>
                  <p className="text-indigo-100 text-sm mt-1">
                    Production-ready scikit-learn preprocessing pipeline
                  </p>
                </div>
                <button
                  onClick={() => setShowPipeline(false)}
                  className="text-white hover:bg-indigo-700 p-2 rounded transition"
                >
                  ✕
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-auto p-6">
                {/* Feature Summary */}
                <div className="mb-6 grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-slate-600 mb-1">
                      Numeric Features
                    </p>
                    <p className="text-2xl font-bold text-blue-600">
                      {pipelineData?.numeric_features?.length || 0}
                    </p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-sm text-slate-600 mb-1">
                      Categorical Features
                    </p>
                    <p className="text-2xl font-bold text-purple-600">
                      {pipelineData?.categorical_features?.length || 0}
                    </p>
                  </div>
                </div>

                {/* Code Display */}
                <div className="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-sm overflow-auto max-h-96">
                  <pre>{pipelineData?.pipeline_code}</pre>
                </div>

                {/* Features Used */}
                {pipelineData?.numeric_features && (
                  <div className="mt-6">
                    <h4 className="font-semibold text-slate-800 mb-2">
                      Numeric Features
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {pipelineData.numeric_features.map(
                        (feature: string, idx: number) => (
                          <span
                            key={idx}
                            className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                          >
                            {feature}
                          </span>
                        ),
                      )}
                    </div>
                  </div>
                )}

                {pipelineData?.categorical_features && (
                  <div className="mt-4">
                    <h4 className="font-semibold text-slate-800 mb-2">
                      Categorical Features
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {pipelineData.categorical_features.map(
                        (feature: string, idx: number) => (
                          <span
                            key={idx}
                            className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm"
                          >
                            {feature}
                          </span>
                        ),
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="flex gap-3 p-6 border-t bg-slate-50">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(pipelineData?.pipeline_code);
                    addNotification(
                      "✓ Pipeline code copied to clipboard!",
                      "success",
                    );
                  }}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-semibold transition"
                >
                  📋 Copy to Clipboard
                </button>
                <button
                  onClick={() => {
                    const element = document.createElement("a");
                    element.setAttribute(
                      "href",
                      "data:text/plain;charset=utf-8," +
                        encodeURIComponent(pipelineData?.pipeline_code),
                    );
                    element.setAttribute("download", "ml_pipeline.py");
                    element.style.display = "none";
                    document.body.appendChild(element);
                    element.click();
                    document.body.removeChild(element);
                    addNotification("✓ Pipeline code downloaded!", "success");
                  }}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg font-semibold transition"
                >
                  📥 Download as .py
                </button>
                <button
                  onClick={() => setShowPipeline(false)}
                  className="flex-1 bg-slate-400 hover:bg-slate-500 text-white py-2 px-4 rounded-lg font-semibold transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Email Report Modal */}
        {showEmailModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-md overflow-hidden">
              {/* Header */}
              <div className="p-6 border-b bg-gradient-to-r from-purple-600 to-pink-600">
                <h2 className="text-2xl font-bold text-white">
                  📧 Send Report via Email
                </h2>
                <p className="text-purple-100 text-sm mt-1">
                  Enter your email to receive the analysis report
                </p>
              </div>

              {/* Content */}
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={emailInput}
                    onChange={(e) => setEmailInput(e.target.value)}
                    placeholder="your-email@example.com"
                    onKeyPress={(e) => {
                      if (e.key === "Enter") {
                        handleEmailReport(emailInput);
                      }
                    }}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-slate-50"
                  />
                </div>

                <div className="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
                  <p className="text-sm text-slate-700">
                    <b>What you'll receive:</b>
                  </p>
                  <ul className="text-sm text-slate-600 mt-2 space-y-1">
                    <li>✓ PDF report with analysis</li>
                    <li>✓ Feature importance rankings</li>
                    <li>✓ Recommendations & fixes</li>
                    <li>✓ Data quality metrics</li>
                    {includeCSV && <li>✓ Cleaned dataset CSV file</li>}
                  </ul>
                </div>

                <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <input
                    type="checkbox"
                    id="attachCSV"
                    checked={includeCSV}
                    onChange={(e) => setIncludeCSV(e.target.checked)}
                    className="w-5 h-5 cursor-pointer accent-blue-600"
                  />
                  <label htmlFor="attachCSV" className="cursor-pointer flex-1">
                    <span className="font-semibold text-slate-800">
                      📎 Attach Cleaned Dataset (CSV)
                    </span>
                    <p className="text-xs text-slate-600 mt-1">
                      Include cleaned dataset file with all rows
                    </p>
                  </label>
                </div>
              </div>

              {/* Footer */}
              <div className="flex gap-3 p-6 border-t bg-slate-50">
                <button
                  onClick={() => handleEmailReport(emailInput)}
                  disabled={loading.email || !emailInput.trim()}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg font-semibold transition"
                >
                  {loading.email ? "Sending..." : "📧 Send Report"}
                </button>
                <button
                  onClick={() => {
                    setShowEmailModal(false);
                    setEmailInput("");
                    setIncludeCSV(true);
                  }}
                  className="flex-1 bg-slate-400 hover:bg-slate-500 text-white py-2 px-4 rounded-lg font-semibold transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Notification Display */}
        <div className="fixed bottom-8 right-8 space-y-3 max-w-md z-40">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className={`p-4 rounded-lg shadow-lg text-white font-medium animate-in fade-in slide-in-from-right-4 ${
                notif.type === "success"
                  ? "bg-green-500"
                  : notif.type === "error"
                    ? "bg-red-500"
                    : notif.type === "warning"
                      ? "bg-yellow-500"
                      : "bg-blue-500"
              }`}
            >
              {notif.message}
            </div>
          ))}
        </div>

        {/* Info Guide Modal */}
        {/* AutoML Baseline Modal */}
        {showAutoMLModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-blue-600 to-cyan-600 sticky top-0">
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    🤖 AutoML Baseline Model Training
                  </h2>
                  <p className="text-blue-100 text-sm mt-1">
                    Train an automatic baseline model on your dataset
                  </p>
                </div>
                <button
                  onClick={() => {
                    setShowAutoMLModal(false);
                    setAutoMLFile(null);
                    setAutoMLTargetColumn("");
                    setAutoMLResults(null);
                  }}
                  className="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded-lg transition"
                >
                  ✕
                </button>
              </div>

              {/* Content */}
              <div className="p-6">
                {autoMLResults ? (
                  // Display Results
                  <div className="space-y-6">
                    <div className="bg-gradient-to-r from-green-50 to-cyan-50 border border-green-200 rounded-lg p-4">
                      <h3 className="font-bold text-green-900 mb-2">
                        ✓ Model Training Complete!
                      </h3>
                      <p className="text-sm text-green-800">
                        Your baseline model has been trained successfully.
                      </p>
                    </div>

                    {/* Model Type */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 border border-gray-200 rounded-lg">
                        <p className="text-sm text-gray-600">Model Type</p>
                        <p className="text-lg font-bold text-gray-900">
                          {autoMLResults?.baseline_model?.model_type || "N/A"}
                        </p>
                      </div>
                      <div className="p-4 border border-gray-200 rounded-lg">
                        <p className="text-sm text-gray-600">Problem Type</p>
                        <p className="text-lg font-bold text-gray-900">
                          {autoMLResults?.baseline_model?.problem_type ===
                          "classification"
                            ? "Classification"
                            : "Regression"}
                        </p>
                      </div>
                    </div>

                    {/* Performance Metrics */}
                    <div>
                      <h4 className="font-bold text-gray-900 mb-3">
                        📊 Performance Metrics
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {autoMLResults?.baseline_model?.problem_type ===
                        "classification" ? (
                          <>
                            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                              <p className="text-xs text-blue-600 font-semibold">
                                Accuracy
                              </p>
                              <p className="text-lg font-bold text-blue-900">
                                {(
                                  autoMLResults?.performance_metrics?.accuracy *
                                    100 || 0
                                ).toFixed(1)}
                                %
                              </p>
                            </div>
                            <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                              <p className="text-xs text-purple-600 font-semibold">
                                Precision
                              </p>
                              <p className="text-lg font-bold text-purple-900">
                                {(
                                  autoMLResults?.performance_metrics
                                    ?.precision * 100 || 0
                                ).toFixed(1)}
                                %
                              </p>
                            </div>
                            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                              <p className="text-xs text-green-600 font-semibold">
                                Recall
                              </p>
                              <p className="text-lg font-bold text-green-900">
                                {(
                                  autoMLResults?.performance_metrics?.recall *
                                    100 || 0
                                ).toFixed(1)}
                                %
                              </p>
                            </div>
                            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                              <p className="text-xs text-yellow-600 font-semibold">
                                F1 Score
                              </p>
                              <p className="text-lg font-bold text-yellow-900">
                                {(
                                  autoMLResults?.performance_metrics?.f1_score *
                                    100 || 0
                                ).toFixed(1)}
                                %
                              </p>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                              <p className="text-xs text-blue-600 font-semibold">
                                R² Score
                              </p>
                              <p className="text-lg font-bold text-blue-900">
                                {(
                                  autoMLResults?.performance_metrics
                                    ?.r2_score || 0
                                ).toFixed(3)}
                              </p>
                            </div>
                            <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                              <p className="text-xs text-purple-600 font-semibold">
                                RMSE
                              </p>
                              <p className="text-lg font-bold text-purple-900">
                                {(
                                  autoMLResults?.performance_metrics?.rmse || 0
                                ).toFixed(2)}
                              </p>
                            </div>
                            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                              <p className="text-xs text-green-600 font-semibold">
                                MAE
                              </p>
                              <p className="text-lg font-bold text-green-900">
                                {(
                                  autoMLResults?.performance_metrics?.mae || 0
                                ).toFixed(2)}
                              </p>
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Top Features */}
                    {autoMLResults?.top_features &&
                      autoMLResults.top_features.length > 0 && (
                        <div>
                          <h4 className="font-bold text-gray-900 mb-3">
                            ⭐ Top Features
                          </h4>
                          <div className="space-y-2">
                            {autoMLResults.top_features
                              .slice(0, 5)
                              .map((feature: any, idx: number) => (
                                <div
                                  key={idx}
                                  className="flex items-center justify-between p-2 bg-gray-50 rounded"
                                >
                                  <span className="text-gray-700 font-medium">
                                    {feature.feature}
                                  </span>
                                  <div className="flex items-center gap-2">
                                    <div className="w-24 h-2 bg-gray-200 rounded-full">
                                      <div
                                        className="h-full bg-gradient-to-r from-blue-600 to-cyan-600 rounded-full"
                                        style={{
                                          width: `${Math.min(feature.importance * 100, 100)}%`,
                                        }}
                                      ></div>
                                    </div>
                                    <span className="text-xs text-gray-600 w-12">
                                      {(feature.importance * 100).toFixed(1)}%
                                    </span>
                                  </div>
                                </div>
                              ))}
                          </div>
                        </div>
                      )}

                    {/* Recommended Models */}
                    {autoMLResults?.recommended_models && (
                      <div>
                        <h4 className="font-bold text-gray-900 mb-3">
                          💡 Recommended Models
                        </h4>
                        <div className="space-y-2">
                          {autoMLResults.recommended_models
                            .slice(0, 5)
                            .map((model: string, idx: number) => (
                              <div
                                key={idx}
                                className="p-2 bg-blue-50 border border-blue-200 rounded flex items-center gap-2"
                              >
                                <span className="inline-block w-6 h-6 bg-blue-600 text-white rounded-full text-center text-xs font-bold">
                                  {idx + 1}
                                </span>
                                <span className="text-gray-800 font-medium">
                                  {model}
                                </span>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}

                    {/* Close Button */}
                    <button
                      onClick={() => {
                        setShowAutoMLModal(false);
                        setAutoMLFile(null);
                        setAutoMLTargetColumn("");
                        setAutoMLResults(null);
                      }}
                      className="w-full mt-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-2 px-4 rounded-lg font-semibold transition"
                    >
                      Close
                    </button>
                  </div>
                ) : (
                  // Input Form
                  <div className="space-y-6">
                    {/* File Upload */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-2">
                        📁 Dataset File (CSV or Excel)
                      </label>
                      <div
                        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition cursor-pointer"
                        onClick={() =>
                          document.getElementById("automl-file-input")?.click()
                        }
                      >
                        <input
                          id="automl-file-input"
                          type="file"
                          accept=".csv,.xlsx,.xls"
                          onChange={(e) =>
                            setAutoMLFile(e.target.files?.[0] || null)
                          }
                          className="hidden"
                        />
                        <p className="text-gray-600">
                          {autoMLFile ? (
                            <>
                              ✓ Selected: <strong>{autoMLFile.name}</strong>
                            </>
                          ) : (
                            <>
                              Click to upload or drag & drop
                              <br />
                              <span className="text-xs text-gray-500">
                                CSV, XLSX, or XLS files accepted
                              </span>
                            </>
                          )}
                        </p>
                      </div>
                    </div>

                    {/* Target Column Input */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-2">
                        🎯 Target Column Name
                      </label>
                      <input
                        type="text"
                        value={autoMLTargetColumn}
                        onChange={(e) => setAutoMLTargetColumn(e.target.value)}
                        placeholder='e.g., "age", "price", "survived"'
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        The column you want to predict (target variable)
                      </p>
                    </div>

                    {/* Information Box */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-sm text-blue-900">
                        <strong>ℹ️ AutoML will:</strong>
                      </p>
                      <ul className="text-sm text-blue-800 space-y-1 mt-2 ml-4 list-disc">
                        <li>Detect problem type (classification/regression)</li>
                        <li>Train a RandomForest baseline model</li>
                        <li>Calculate performance metrics</li>
                        <li>Extract feature importance</li>
                        <li>Suggest alternative models</li>
                      </ul>
                    </div>

                    {/* Train Button */}
                    <button
                      onClick={handleAutoMLSubmit}
                      disabled={
                        autoMLLoading || !autoMLFile || !autoMLTargetColumn
                      }
                      className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-semibold transition shadow-lg"
                    >
                      {autoMLLoading ? (
                        <span className="flex items-center justify-center gap-2">
                          <span className="inline-block w-4 h-4 bg-white rounded-full animate-spin"></span>
                          Training Model...
                        </span>
                      ) : (
                        "🚀 Train Baseline Model"
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        <InfoGuide
          isOpen={showInfoGuide}
          onClose={() => setShowInfoGuide(false)}
        />
      </div>
    </div>
  );
};

export default Dashboard;
