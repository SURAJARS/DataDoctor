import React from "react";

interface LandingPageProps {
  onNavigateToUpload: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onNavigateToUpload,
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="bg-slate-900/95 backdrop-blur border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">Data Doctor 🏥</h1>
          <button
            onClick={onNavigateToUpload}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition"
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-8 py-20">
        <div className="text-center mb-12">
          <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Dataset Quality Inspector
          </h2>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-8">
            Deep dive analysis of any dataset. Detect ALL possible defects that
            could break your machine learning pipeline.
          </p>
          <button
            onClick={onNavigateToUpload}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold text-lg transition transform hover:scale-105"
          >
            Upload Dataset →
          </button>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-16">
          {[
            {
              icon: "📊",
              title: "Comprehensive Analysis",
              description:
                "Missing values, duplicates, outliers, class imbalance, and more.",
            },
            {
              icon: "🎯",
              title: "ML Readiness Score",
              description:
                "Know if your dataset is ready for training. Get actionable recommendations.",
            },
            {
              icon: "⚙️",
              title: "Feature Engineering",
              description:
                "Auto-generated transformations and feature engineering suggestions.",
            },
            {
              icon: "🔍",
              title: "Bias Detection",
              description:
                "Identify bias in target distribution and demographic features.",
            },
            {
              icon: "🚀",
              title: "Feature Importance",
              description: "Quick baseline model to rank feature importance.",
            },
            {
              icon: "🛠️",
              title: "Data Cleaning Guide",
              description: "Step-by-step Python code for data preparation.",
            },
            {
              icon: "✨",
              title: "Auto-Fix Dataset",
              description:
                "Automatically fix common dataset issues with smart recommendations.",
            },
            {
              icon: "📄",
              title: "PDF Report Download",
              description:
                "Generate and download comprehensive analysis reports as PDF.",
            },
            {
              icon: "📧",
              title: "Email Reports",
              description:
                "Send your analysis reports directly to your email inbox.",
            },
            {
              icon: "⚠️",
              title: "Risk Score Assessment",
              description:
                "Get a risk score showing dataset quality and ML pipeline compatibility.",
            },
            {
              icon: "📈",
              title: "Data Drift Detection",
              description:
                "Detect distribution shifts between training and test datasets.",
            },
            {
              icon: "🔧",
              title: "ML Pipeline Generator",
              description:
                "Auto-generate production-ready scikit-learn preprocessing pipelines.",
            },
          ].map((feature, idx) => (
            <div
              key={idx}
              className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-blue-500 transition"
            >
              <div className="text-4xl mb-3">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-slate-400">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Key Metrics */}
        <div className="mt-20 grid md:grid-cols-4 gap-8 text-center">
          {[
            { number: "45+", label: "Quality Checks" },
            { number: "12", label: "Advanced Features" },
            { number: "100%", label: "Large Datasets" },
            { number: "4", label: "File Formats" },
          ].map((metric, idx) => (
            <div key={idx}>
              <div className="text-4xl font-bold text-blue-400">
                {metric.number}
              </div>
              <p className="text-slate-400 mt-2">{metric.label}</p>
            </div>
          ))}
        </div>

        {/* Advanced Features Section */}
        <div className="mt-20">
          <h3 className="text-3xl font-bold text-white mb-10 text-center">
            Advanced Capabilities
          </h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg p-8 border border-slate-600">
              <h4 className="text-xl font-semibold text-blue-400 mb-4">
                🔧 Automated Repairs
              </h4>
              <p className="text-slate-300 mb-4">
                Auto-Fix Dataset analyzes your data and automatically applies
                recommended fixes to common data quality issues like missing
                values, inconsistent formats, and outliers.
              </p>
              <ul className="text-sm text-slate-400 space-y-2">
                <li>✓ Intelligent missing value imputation</li>
                <li>✓ Outlier handling strategies</li>
                <li>✓ Format standardization</li>
                <li>✓ Duplicate removal</li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg p-8 border border-slate-600">
              <h4 className="text-xl font-semibold text-green-400 mb-4">
                📊 Report Generation
              </h4>
              <p className="text-slate-300 mb-4">
                Generate professional PDF reports and email them directly.
                Perfect for sharing findings with stakeholders and maintaining
                audit trails.
              </p>
              <ul className="text-sm text-slate-400 space-y-2">
                <li>✓ Comprehensive PDF reports</li>
                <li>✓ Email delivery</li>
                <li>✓ Visualization included</li>
                <li>✓ Recommendations section</li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg p-8 border border-slate-600">
              <h4 className="text-xl font-semibold text-orange-400 mb-4">
                ⚠️ Risk Assessment
              </h4>
              <p className="text-slate-300 mb-4">
                Get a quantified risk score that indicates how well your dataset
                will perform in ML pipelines. Identify potential showstoppers
                before deployment.
              </p>
              <ul className="text-sm text-slate-400 space-y-2">
                <li>✓ Risk scoring algorithm</li>
                <li>✓ ML compatibility assessment</li>
                <li>✓ Critical issue flagging</li>
                <li>✓ Remediation roadmap</li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg p-8 border border-slate-600">
              <h4 className="text-xl font-semibold text-purple-400 mb-4">
                🚀 Production Ready
              </h4>
              <p className="text-slate-300 mb-4">
                Auto-generate production-ready scikit-learn pipelines that
                handle all preprocessing steps. Drift detection ensures model
                stability over time.
              </p>
              <ul className="text-sm text-slate-400 space-y-2">
                <li>✓ Auto-generated pipelines</li>
                <li>✓ Distribution drift detection</li>
                <li>✓ Sklearn compatible code</li>
                <li>✓ Deployment ready</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Supported Formats */}
        <div className="mt-20 bg-slate-800 rounded-lg p-8 border border-slate-700">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">
            Supported Formats
          </h3>
          <div className="grid md:grid-cols-4 gap-4 text-center">
            {["CSV", "Excel", "Parquet", "JSON"].map((format, idx) => (
              <div key={idx} className="bg-slate-700 py-4 rounded-lg">
                <p className="text-white font-semibold">{format}</p>
              </div>
            ))}
          </div>
          <p className="text-slate-400 text-center mt-6">
            Handles datasets from 1MB to 10GB+ with automatic chunking
          </p>
        </div>

        {/* CTA */}
        <div className="mt-20 text-center">
          <h3 className="text-3xl font-bold text-white mb-4">
            Start Analyzing Your Data Today
          </h3>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-12 py-4 rounded-lg font-semibold text-lg transition transform hover:scale-105">
            Upload Your First Dataset
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 mt-20 py-8 text-center text-slate-400">
        <p>Data Doctor • Dataset Quality Inspector • Built for ML Engineers</p>
      </footer>
    </div>
  );
};

export default LandingPage;
