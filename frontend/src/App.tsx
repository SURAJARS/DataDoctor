import React, { useState } from "react";
import { UploadPage } from "./pages/Upload";
import { Dashboard } from "./components/Dashboard";
import { LandingPage } from "./pages/Landing";
import "./App.css";

function App() {
  const [currentPage, setCurrentPage] = useState<
    "landing" | "upload" | "dashboard"
  >("landing");
  const [analysisReport, setAnalysisReport] = useState<any>(null);

  const handleAnalysisComplete = (report: any) => {
    setAnalysisReport(report);
    setCurrentPage("dashboard");
  };

  const handleReset = () => {
    setCurrentPage("landing");
    setAnalysisReport(null);
  };

  return (
    <div className="App">
      {currentPage === "landing" && (
        <LandingPage onNavigateToUpload={() => setCurrentPage("upload")} />
      )}
      {currentPage === "upload" && (
        <UploadPage onAnalysisComplete={handleAnalysisComplete} />
      )}
      {currentPage === "dashboard" && analysisReport && (
        <>
          <button
            onClick={handleReset}
            className="fixed top-4 left-4 z-50 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition"
          >
            ← Back Home
          </button>
          <Dashboard report={analysisReport} />
        </>
      )}

      {/* Navigation Button */}
      {currentPage !== "upload" && currentPage !== "dashboard" && (
        <button
          onClick={() => setCurrentPage("upload")}
          className="fixed bottom-8 right-8 z-50 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition transform hover:scale-105"
        >
          Upload Dataset →
        </button>
      )}
    </div>
  );
}

export default App;
