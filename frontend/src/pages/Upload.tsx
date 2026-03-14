import React, { useState } from "react";
import axios from "axios";

interface UploadProps {
  onAnalysisComplete: (report: any) => void;
}

export const UploadPage: React.FC<UploadProps> = ({ onAnalysisComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [targetColumn, setTargetColumn] = useState("");
  const [sensitiveFeatures, setSensitiveFeatures] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a file");
      return;
    }

    setLoading(true);
    setProgress(0);

    const formData = new FormData();
    formData.append("file", file);
    if (targetColumn) formData.append("target_column", targetColumn);
    if (sensitiveFeatures)
      formData.append("sensitive_features", sensitiveFeatures);

    try {
      const response = await axios.post(
        "http://localhost:8000/api/analyze",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (progress) => {
            setProgress(Math.round((progress.loaded / progress.total!) * 100));
          },
        },
      );

      // Get full report
      const reportResponse = await axios.get(
        `http://localhost:8000/api/report/${response.data.analysis_id}`,
      );
      onAnalysisComplete(reportResponse.data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "An error occurred during analysis",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Data Doctor</h1>
        <p className="text-slate-600 mb-6">
          Upload your dataset for comprehensive quality analysis
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Input */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Dataset File
            </label>
            <div className="border-2 border-dashed border-blue-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-500 transition">
              <input
                type="file"
                onChange={handleFileChange}
                accept=".csv,.xlsx,.parquet,.json"
                className="hidden"
                id="file-input"
              />
              <label htmlFor="file-input" className="cursor-pointer">
                <div className="text-blue-600 font-semibold">
                  {file ? file.name : "Click to upload or drag and drop"}
                </div>
                <p className="text-slate-500 text-sm mt-1">
                  CSV, Excel, Parquet, or JSON
                </p>
              </label>
            </div>
          </div>

          {/* Target Column */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Target Column (Optional)
            </label>
            <input
              type="text"
              value={targetColumn}
              onChange={(e) => setTargetColumn(e.target.value)}
              placeholder="e.g., target, label, y"
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-slate-500 text-xs mt-1">
              If you have a target variable for ML tasks
            </p>
          </div>

          {/* Sensitive Features */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Sensitive Features (Optional)
            </label>
            <input
              type="text"
              value={sensitiveFeatures}
              onChange={(e) => setSensitiveFeatures(e.target.value)}
              placeholder="e.g., age, gender, race"
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-slate-500 text-xs mt-1">
              Comma-separated demographic features for bias detection
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Progress Bar */}
          {loading && progress > 0 && (
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-semibold text-slate-700">
                  Analyzing...
                </span>
                <span className="text-sm font-semibold text-slate-700">
                  {progress}%
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!file || loading}
            className={`w-full py-3 px-4 rounded-lg font-semibold transition ${
              loading || !file
                ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700"
            }`}
          >
            {loading ? "Analyzing Dataset..." : "Analyze Dataset"}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-200">
          <h3 className="font-semibold text-slate-800 mb-3">
            Supported Formats
          </h3>
          <ul className="text-slate-600 text-sm space-y-1">
            <li>✓ CSV files</li>
            <li>✓ Excel (.xlsx)</li>
            <li>✓ Parquet files</li>
            <li>✓ JSON files</li>
            <li>✓ Large datasets ({">"}500MB)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
