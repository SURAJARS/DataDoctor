import React, { useState } from "react";

interface InfoItem {
  title: string;
  description: string;
  details: string[];
  example: string;
}

const infoDatabase: { [key: string]: InfoItem } = {
  health_score: {
    title: "Dataset Health Score",
    description:
      "Measures the overall quality and cleanliness of your dataset based on multiple quality factors.",
    details: [
      "Evaluates missing values, duplicates, outliers, and consistency",
      "Ranges from 0-100, where higher is better",
      "Considers data type correctness and formatting issues",
      "Identifies problematic patterns that could break ML pipelines",
    ],
    example:
      "A dataset with 95/100 health score has minimal data quality issues and is ready for most ML tasks.",
  },
  ml_readiness: {
    title: "ML Readiness Score",
    description:
      "Indicates whether your dataset is prepared for machine learning model training and deployment.",
    details: [
      "Assesses feature engineering requirements and transformations needed",
      "Evaluates if data splits are balanced and sufficient",
      "Checks if features have predictive power for your target",
      "Identifies data requirements for model performance",
      "Ranges from 0-100, where higher means more ready for ML",
    ],
    example:
      "An ML readiness of 75 suggests some feature engineering needed but dataset is generally suitable for model training.",
  },
  difference: {
    title: "Health Score vs ML Readiness Score",
    description:
      "Two complementary metrics that measure different aspects of dataset quality.",
    details: [
      "HEALTH SCORE: Focuses on data quality (cleanliness, consistency, missing values)",
      "ML READINESS: Focuses on ML suitability (feature quality, balance, sufficiency)",
      "A dataset can be clean but not ready for ML (needs feature engineering)",
      "A dataset can have issues but become ML-ready after fixes",
      "Together they provide complete quality assessment",
    ],
    example:
      "Dataset A: Health=90 (clean data), ML Readiness=60 (needs more features). Dataset B: Health=70 (messy), ML Readiness=85 (good features).",
  },
  risk_score: {
    title: "Risk Score Assessment",
    description:
      "Quantifies potential issues and risks that could impact your machine learning model performance.",
    details: [
      "Risk Level: Low (0-30), Medium (31-60), High (61-100)",
      "Combines health score and ML readiness metrics",
      "Identifies bias, drift, and data quality risks",
      "Provides actionable recommendations for risk mitigation",
      "Higher risk score = more attention needed before ML deployment",
    ],
    example:
      "A high risk score of 75 might indicate severe class imbalance or significant missing patterns that need addressing.",
  },
  bias_detection: {
    title: "Bias Detection",
    description:
      "Identifies harmful biases in your data that could lead to unfair or discriminatory ML models.",
    details: [
      "Detects demographic parity violations",
      "Identifies disparate impact in target distribution",
      "Analyzes sensitive feature distributions",
      "Flags potential discrimination risks",
      "Suggests fairness-aware preprocessing techniques",
    ],
    example:
      "If 80% of positive outcomes go to one demographic group, bias detection alerts you to potential fairness issues.",
  },
  drift_detection: {
    title: "Drift Detection",
    description:
      "Identifies when your data patterns change over time, which could degrade model performance.",
    details: [
      "Detects feature distribution shifts",
      "Identifies target label changes (label drift)",
      "Monitors for concept drift in relationships",
      "Tracks data quality degradation over time",
      "Alerts when models need retraining",
    ],
    example:
      "If customer behavior patterns change seasonally, drift detection helps you retrain models at the right time.",
  },
  feature_importance: {
    title: "Feature Importance",
    description:
      "Ranks which input features have the most influence on your target variable.",
    details: [
      "Uses baseline model to compute importance scores",
      "Scores range from 0 to 1, where 1 is most important",
      "Shows which features drive model predictions",
      "Helps identify redundant features for removal",
      "Guides feature engineering efforts",
    ],
    example:
      "In a loan prediction model, 'credit_score' might have importance 0.45, meaning it's a top predictor.",
  },
  auto_fix: {
    title: "Auto-Fix Dataset",
    description:
      "Automatically applies recommended fixes to common data quality issues.",
    details: [
      "Fills missing values using intelligent strategies",
      "Removes or handles duplicate records",
      "Detects and removes outliers appropriately",
      "Standardizes data formats and types",
      "Generates cleaned CSV for immediate use",
    ],
    example:
      "Auto-fix can fill missing numeric values with median, missing categorical with mode, and remove exact duplicates.",
  },
  pipeline_code: {
    title: "Pipeline Code Generator",
    description:
      "Generates production-ready Python code for your data cleaning and preprocessing pipeline.",
    details: [
      "Creates pandas-based transformation code",
      "Includes all identified fixes and transformations",
      "Ready to integrate into ML workflows",
      "Follows best practices and error handling",
      "Can be version controlled and deployed",
    ],
    example:
      "Generated code might include: fill_missing(), remove_duplicates(), encode_categorical(), scale_features().",
  },
  pdf_report: {
    title: "PDF Report",
    description:
      "Comprehensive report containing all analysis results, visualizations, and recommendations.",
    details: [
      "Includes executive summary of findings",
      "Visual charts and graphs for key metrics",
      "Detailed analysis of each data quality issue",
      "Prioritized recommendations for improvements",
      "Technical appendix with detailed statistics",
    ],
    example:
      "PDF includes charts showing missing value patterns, statistical summaries, and step-by-step fixes.",
  },
  email_report: {
    title: "Email Report",
    description:
      "Sends your complete analysis results and cleaned dataset directly to your email.",
    details: [
      "Includes full PDF analysis report",
      "Attaches cleaned and auto-fixed dataset (CSV)",
      "Summary statistics in email body",
      "Can be shared with team members",
      "Archives for future reference",
    ],
    example:
      "Receive email with 2 attachments: analysis_report.pdf and cleaned_dataset.csv ready for immediate use.",
  },
  data_quality: {
    title: "Data Quality Metrics",
    description:
      "Key indicators that measure the cleanliness and reliability of your data.",
    details: [
      "Missing Value Rate: % of empty cells in dataset",
      "Duplicate Rate: % of completely duplicate rows",
      "Outlier Count: # of unusual data points detected",
      "Type Consistency: % of values matching expected data type",
      "Cardinality: # of unique values in categorical features",
    ],
    example:
      "A dataset with 2% missing values, 0.5% duplicates is generally high quality.",
  },
  categorical: {
    title: "Categorical Features",
    description:
      "Non-numeric variables that represent categories or groups (like country, color, status).",
    details: [
      "Can have limited number of distinct values",
      "Require encoding for ML algorithms",
      "Common types: binary, ordinal, nominal",
      "May have imbalanced categories",
      "Important for bias and fairness analysis",
    ],
    example:
      "Examples: [USA, Canada, Mexico], [Red, Green, Blue], [Active, Inactive].",
  },
  numeric: {
    title: "Numeric Features",
    description:
      "Quantitative variables that represent measurements or counts (like age, price, quantity).",
    details: [
      "Can be continuous (any value in range) or discrete (integers)",
      "Used directly in most ML algorithms",
      "Require normalization/scaling for best results",
      "Sensitive to outliers",
      "Easy to compute statistics on",
    ],
    example: "Examples: age, salary, temperature, count of items.",
  },
};

interface InfoGuideProps {
  isOpen: boolean;
  onClose: () => void;
  searchTerm?: string;
}

export const InfoGuide: React.FC<InfoGuideProps> = ({
  isOpen,
  onClose,
  searchTerm = "",
}) => {
  const [selectedTopic, setSelectedTopic] = useState<string | null>(
    searchTerm in infoDatabase ? searchTerm : null,
  );

  if (!isOpen) return null;

  const displayInfo = selectedTopic
    ? infoDatabase[selectedTopic]
    : Object.values(infoDatabase)[0];

  const topicList = Object.keys(infoDatabase);

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white p-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">📚 Data Doctor Guide</h1>
            <p className="text-blue-100 mt-1">
              Understand all analysis terms and metrics
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 p-2 rounded-lg transition"
          >
            ✕
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Topics Sidebar */}
          <div className="w-64 bg-slate-50 border-r border-slate-200 overflow-y-auto">
            <div className="p-4 space-y-2">
              {topicList.map((topic) => (
                <button
                  key={topic}
                  onClick={() => setSelectedTopic(topic)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition ${
                    selectedTopic === topic
                      ? "bg-blue-600 text-white font-semibold"
                      : "text-slate-700 hover:bg-slate-200"
                  }`}
                >
                  {infoDatabase[topic].title}
                </button>
              ))}
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-6">
            {displayInfo && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-3xl font-bold text-slate-900 mb-2">
                    {displayInfo.title}
                  </h2>
                  <p className="text-lg text-slate-600">
                    {displayInfo.description}
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-slate-800 mb-3">
                    Key Points:
                  </h3>
                  <ul className="space-y-2">
                    {displayInfo.details.map((detail, idx) => (
                      <li
                        key={idx}
                        className="flex items-start gap-3 text-slate-700"
                      >
                        <span className="text-blue-600 font-bold mt-0.5">
                          ▸
                        </span>
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
                  <h3 className="font-semibold text-blue-900 mb-2">
                    💡 Example:
                  </h3>
                  <p className="text-blue-800">{displayInfo.example}</p>
                </div>

                {selectedTopic === "difference" && (
                  <div className="bg-purple-50 border-l-4 border-purple-600 p-4 rounded">
                    <h3 className="font-semibold text-purple-900 mb-3">
                      📊 Quick Reference Table:
                    </h3>
                    <div className="space-y-2 text-sm text-purple-800">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="font-semibold mb-1">Health Score</p>
                          <p className="text-xs">
                            ✓ Cleanliness
                            <br />✓ Consistency
                            <br />✓ Completeness
                          </p>
                        </div>
                        <div>
                          <p className="font-semibold mb-1">ML Readiness</p>
                          <p className="text-xs">
                            ✓ Feature Quality
                            <br />✓ Data Balance
                            <br />✓ Model Suitability
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-slate-100 border-t border-slate-200 px-6 py-4 flex justify-between items-center">
          <p className="text-sm text-slate-600">
            💡 Tip: Use this guide to understand each metric in your dashboard
          </p>
          <button
            onClick={onClose}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition"
          >
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
};

export default InfoGuide;
