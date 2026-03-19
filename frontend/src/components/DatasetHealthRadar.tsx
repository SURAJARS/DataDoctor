import React, { useState, useEffect } from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// API Base URL - auto-detects production vs development
const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "https://datadoctor.onrender.com/api"
    : "http://localhost:8000/api";

interface RadarMetric {
  metric: string;
  value: number;
}

interface DatasetHealthRadarProps {
  analysisId: string;
}

interface RadarData {
  radar_metrics: RadarMetric[];
  overall_score: number;
  overall_color: string;
  health_level: string;
  color_scale: {
    green: { min: number; color: string; label: string };
    yellow: { min: number; max: number; color: string; label: string };
    red: { max: number; color: string; label: string };
  };
}

const DatasetHealthRadar: React.FC<DatasetHealthRadarProps> = ({
  analysisId,
}) => {
  const [radarData, setRadarData] = useState<RadarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Don't fetch if analysisId is missing or "latest"
    if (!analysisId || analysisId === "latest") {
      setError("Please run an analysis first to see dataset health metrics");
      setLoading(false);
      return;
    }

    const fetchRadarData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `${API_BASE_URL}/dataset-health-radar/${analysisId}`,
        );

        if (!response.ok) {
          throw new Error(
            `Failed to fetch radar data (HTTP ${response.status})`,
          );
        }

        const data = await response.json();
        setRadarData(data);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch radar data",
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRadarData();
  }, [analysisId]);

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-xl shadow-md">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="inline-block">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-full animate-spin"></div>
            </div>
            <p className="mt-2 text-gray-600">Loading radar data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !radarData) {
    return (
      <div className="p-6 bg-white rounded-xl shadow-md border border-red-200">
        <div className="text-red-600">
          <p className="font-semibold">Error loading radar data</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  const getMetricColor = (value: number): string => {
    if (value >= 80) return "#22c55e"; // Green
    if (value >= 60) return "#facc15"; // Yellow
    return "#ef4444"; // Red
  };

  const getMetricTooltip = (metric: string, value: number) => {
    const descriptions: { [key: string]: string } = {
      Completeness: "Percentage of non-null values in dataset",
      "Class Balance":
        "Balance between different class distributions (for classification)",
      Outliers: "Percentage of data points that are statistical outliers",
      Correlation: "Multicollinearity detection score",
      "Bias Risk": "Fairness and bias detection score",
      "Drift Risk": "Data drift detection score",
      "ML Readiness": "Overall machine learning readiness of dataset",
    };

    return `${metric}: ${value}/100\n${descriptions[metric] || ""}`;
  };

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-lg md:text-2xl font-bold text-gray-900">
          Dataset Health Overview
        </h2>
        <p className="text-gray-600 text-xs md:text-sm mt-1">
          Comprehensive view of dataset quality across 7 dimensions
        </p>
      </div>

      {/* Main Radar Card */}
      <div className="bg-white rounded-xl shadow-md p-4 md:p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
          {/* Radar Chart */}
          <div className="lg:col-span-2 w-full flex flex-col">
            <div className="h-80 md:h-screen md:max-h-96 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart
                  data={radarData.radar_metrics}
                  margin={{ top: 5, right: 20, bottom: 5, left: 20 }}
                >
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar
                    name="Dataset Quality"
                    dataKey="value"
                    stroke={radarData.overall_color}
                    fill={radarData.overall_color}
                    fillOpacity={0.6}
                    isAnimationActive={true}
                  />
                  <Tooltip
                    formatter={(value: number) => `${value}/100`}
                    contentStyle={{
                      backgroundColor: "#ffffff",
                      border: `2px solid ${radarData.overall_color}`,
                      borderRadius: "8px",
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Health Summary Card */}
          <div className="space-y-3 md:space-y-4">
            {/* Overall Health Score */}
            <div
              className={`p-3 md:p-4 rounded-lg border-2`}
              style={{
                backgroundColor:
                  radarData.overall_color === "#22c55e"
                    ? "#f0fdf4"
                    : radarData.overall_color === "#facc15"
                      ? "#fffbeb"
                      : "#fef2f2",
                borderColor: radarData.overall_color,
              }}
            >
              <p className="text-xs md:text-sm font-medium text-gray-600">
                Overall Health
              </p>
              <p
                className="text-2xl md:text-3xl font-bold mt-1"
                style={{ color: radarData.overall_color }}
              >
                {radarData.overall_score.toFixed(1)}/100
              </p>
              <p
                className="text-xs md:text-sm font-semibold mt-2"
                style={{ color: radarData.overall_color }}
              >
                {radarData.health_level}
              </p>
            </div>

            {/* Color Legend */}
            <div className="p-3 md:p-4 bg-gray-50 rounded-lg space-y-2">
              <p className="text-xs md:text-sm font-semibold text-gray-700">
                Quality Scale
              </p>
              <div className="space-y-1.5 text-xs">
                <div className="flex items-center gap-2">
                  <div
                    className="w-2.5 h-2.5 md:w-3 md:h-3 rounded-full"
                    style={{ backgroundColor: "#22c55e" }}
                  ></div>
                  <span className="text-gray-600">Healthy (≥80)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className="w-2.5 h-2.5 md:w-3 md:h-3 rounded-full"
                    style={{ backgroundColor: "#facc15" }}
                  ></div>
                  <span className="text-gray-600">Moderate (60-79)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className="w-2.5 h-2.5 md:w-3 md:h-3 rounded-full"
                    style={{ backgroundColor: "#ef4444" }}
                  ></div>
                  <span className="text-gray-600">Critical (&lt;60)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="bg-white rounded-xl shadow-md p-4 md:p-6">
        <h3 className="text-base md:text-lg font-bold text-gray-900 mb-4">
          Detailed Metrics Breakdown
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-4">
          {radarData.radar_metrics.map((metric, idx) => (
            <div
              key={idx}
              className="p-3 md:p-4 border border-gray-200 rounded-lg"
            >
              <p className="text-xs md:text-sm font-medium text-gray-600">
                {metric.metric}
              </p>
              <div className="mt-2 flex items-end justify-between">
                <p className="text-xl md:text-2xl font-bold text-gray-900">
                  {metric.value}
                </p>
                <div
                  className="w-0.5 h-8 md:h-12 rounded"
                  style={{ backgroundColor: getMetricColor(metric.value) }}
                ></div>
              </div>

              {/* Mini Progress Bar */}
              <div className="mt-2 w-full bg-gray-200 rounded-full h-1">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${metric.value}%`,
                    backgroundColor: getMetricColor(metric.value),
                  }}
                ></div>
              </div>

              <p className="text-xs text-gray-500 mt-1">
                {metric.value >= 80
                  ? "✓ Excellent"
                  : metric.value >= 60
                    ? "⚠ Acceptable"
                    : "✗ Needs attention"}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Information Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 md:p-4">
        <p className="text-xs md:text-sm text-blue-900">
          <span className="font-semibold">ℹ️ How to use this radar:</span> Each
          axis represents a different quality dimension. Higher values indicate
          better dataset quality. Aim for all metrics to be in the green zone
          (≥80) for optimal ML performance.
        </p>
      </div>
    </div>
  );
};

export default DatasetHealthRadar;
