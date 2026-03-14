import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  // Upload and analyze dataset
  analyzeDataset: (file: File, targetColumn?: string, sensitiveFeatures?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (targetColumn) formData.append('target_column', targetColumn);
    if (sensitiveFeatures) formData.append('sensitive_features', sensitiveFeatures);

    return axios.post(`${API_BASE_URL}/analyze`, formData);
  },

  // Get full report
  getReport: (analysisId: string) => {
    return axios.get(`${API_BASE_URL}/report/${analysisId}`);
  },

  // Get specific analysis results
  getHealthScore: (analysisId: string) => {
    return axios.get(`${API_BASE_URL}/health-score/${analysisId}`);
  },

  getMLReadiness: (analysisId: string) => {
    return axios.get(`${API_BASE_URL}/ml-readiness/${analysisId}`);
  },

  getFeatureEngineering: (analysisId: string) => {
    return axios.get(`${API_BASE_URL}/feature-engineering/${analysisId}`);
  },

  getBiasDetection: (analysisId: string) => {
    return axios.get(`${API_BASE_URL}/bias-detection/${analysisId}`);
  },

  getDataCleaning: (analysisId: string) => {
    return axios.get(`${API_BASE_URL}/data-cleaning/${analysisId}`);
  },

  getFeatureImportance: (analysisId: string) => {
    return axios.get(`${API_BASE_URL}/feature-importance/${analysisId}`);
  },

  // Get issues
  getIssues: (analysisId: string, severity?: string) => {
    const params = severity ? { severity } : {};
    return axios.get(`${API_BASE_URL}/issues/${analysisId}`, { params });
  },

  // Get recommendations
  getRecommendations: (analysisId: string) => {
    return axios.get(`${API_BASE_URL}/recommendations/${analysisId}`);
  },

  // Get summary
  getSummary: (analysisId: string) => {
    return axios.get(`${API_BASE_URL}/summary/${analysisId}`);
  }
};
