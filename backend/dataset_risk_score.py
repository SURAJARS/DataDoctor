"""
Dataset Risk Score Module
Calculates comprehensive risk assessment for ML pipelines
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')


class DatasetRiskScorer:
    """Scores dataset risk (0-100) with detailed breakdown"""
    
    def __init__(self, df: pd.DataFrame, target_column: str = None):
        """
        Initialize risk scorer
        
        Args:
            df: Input DataFrame
            target_column: Name of target column for ML tasks
        """
        self.df = df
        self.target_column = target_column
        self.risk_score = 0
        self.risk_factors = {}
    
    def calculate_risk_score(self) -> Dict[str, Any]:
        """Calculate overall dataset risk score (0-100)"""
        scores = {}
        
        # 1. Missing Values Risk (Weight: 25%)
        scores['missing_values'] = self._assess_missing_values_risk()
        
        # 2. Class Imbalance Risk (Weight: 20%)
        scores['class_imbalance'] = self._assess_class_imbalance_risk()
        
        # 3. Data Leakage Risk (Weight: 15%)
        scores['data_leakage'] = self._assess_data_leakage_risk()
        
        # 4. Correlation/Multicollinearity Risk (Weight: 15%)
        scores['correlation'] = self._assess_correlation_risk()
        
        # 5. Outlier Risk (Weight: 15%)
        scores['outliers'] = self._assess_outlier_risk()
        
        # 6. Duplicate Data Risk (Weight: 10%)
        scores['duplicates'] = self._assess_duplicate_risk()
        
        # Calculate weighted risk score
        weights = {
            'missing_values': 0.25,
            'class_imbalance': 0.20,
            'data_leakage': 0.15,
            'correlation': 0.15,
            'outliers': 0.15,
            'duplicates': 0.10
        }
        
        self.risk_score = sum(scores[k] * weights[k] for k in scores.keys())
        self.risk_factors = scores
        
        return {
            'risk_score': round(100 - self.risk_score, 1),  # Invert: lower risk = higher score
            'risk_level': self._get_risk_level(self.risk_score),
            'detailed_scores': {k: round(v, 1) for k, v in scores.items()},
            'risk_factors': self._get_risk_summary(),
            'recommendations': self._get_risk_recommendations()
        }
    
    def _assess_missing_values_risk(self) -> float:
        """Assess risk from missing values (0-100, higher = more risky)"""
        total_cells = len(self.df) * len(self.df.columns)
        missing_cells = self.df.isnull().sum().sum()
        missing_pct = (missing_cells / total_cells) * 100
        
        if missing_pct < 1:
            return 0
        elif missing_pct < 5:
            return 20
        elif missing_pct < 10:
            return 40
        elif missing_pct < 20:
            return 60
        elif missing_pct < 30:
            return 80
        else:
            return 100
    
    def _assess_class_imbalance_risk(self) -> float:
        """Assess risk from class imbalance"""
        if self.target_column is None or self.target_column not in self.df.columns:
            return 0
        
        target_dist = self.df[self.target_column].value_counts(normalize=True)
        
        if len(target_dist) < 2:
            return 0  # Regression task
        
        min_class_pct = target_dist.min() * 100
        max_class_pct = target_dist.max() * 100
        imbalance_ratio = max_class_pct / (min_class_pct + 0.001)
        
        if imbalance_ratio < 1.5:
            return 0
        elif imbalance_ratio < 2:
            return 20
        elif imbalance_ratio < 5:
            return 40
        elif imbalance_ratio < 10:
            return 60
        elif imbalance_ratio < 50:
            return 80
        else:
            return 100
    
    def _assess_data_leakage_risk(self) -> float:
        """Assess risk of data leakage (suspicious perfect correlations)"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return 0
        
        corr_matrix = self.df[numeric_cols].corr().abs()
        
        # Find suspiciously high correlations (potential leakage)
        high_corr_pairs = 0
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if corr_matrix.iloc[i, j] > 0.98:
                    high_corr_pairs += 1
        
        if high_corr_pairs == 0:
            return 0
        elif high_corr_pairs <= 2:
            return 30
        elif high_corr_pairs <= 5:
            return 60
        else:
            return 100
    
    def _assess_correlation_risk(self) -> float:
        """Assess risk from multicollinearity"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return 0
        
        corr_matrix = self.df[numeric_cols].corr().abs()
        
        # Count high correlations (0.9-0.98)
        high_corr_count = 0
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if 0.85 < corr_matrix.iloc[i, j] < 0.98:
                    high_corr_count += 1
        
        if high_corr_count == 0:
            return 0
        elif high_corr_count <= 3:
            return 20
        elif high_corr_count <= 10:
            return 40
        else:
            return 60
    
    def _assess_outlier_risk(self) -> float:
        """Assess risk from extreme outliers"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            return 0
        
        total_outliers = 0
        total_values = 0
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            outlier_count = len(self.df[
                (self.df[col] < Q1 - 3*IQR) | (self.df[col] > Q3 + 3*IQR)
            ])
            
            total_outliers += outlier_count
            total_values += len(self.df)
        
        outlier_pct = (total_outliers / total_values) * 100
        
        if outlier_pct < 0.5:
            return 0
        elif outlier_pct < 1:
            return 20
        elif outlier_pct < 2:
            return 40
        elif outlier_pct < 5:
            return 60
        else:
            return 100
    
    def _assess_duplicate_risk(self) -> float:
        """Assess risk from duplicate rows"""
        duplicate_rows = self.df.duplicated().sum()
        duplicate_pct = (duplicate_rows / len(self.df)) * 100
        
        if duplicate_pct < 0.1:
            return 0
        elif duplicate_pct < 1:
            return 20
        elif duplicate_pct < 5:
            return 40
        elif duplicate_pct < 10:
            return 60
        else:
            return 100
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert score to risk level"""
        if risk_score < 10:
            return 'CRITICAL'
        elif risk_score < 20:
            return 'HIGH'
        elif risk_score < 40:
            return 'MODERATE'
        elif risk_score < 70:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _get_risk_summary(self) -> List[Dict]:
        """Get human-readable risk summary"""
        summary = []
        thresholds = {
            'missing_values': 40,
            'class_imbalance': 40,
            'data_leakage': 30,
            'correlation': 40,
            'outliers': 40,
            'duplicates': 20
        }
        
        for factor, score in self.risk_factors.items():
            if score > thresholds.get(factor, 40):
                summary.append({
                    'factor': factor.replace('_', ' ').title(),
                    'risk_score': round(score, 1),
                    'severity': 'HIGH' if score > 70 else 'MODERATE'
                })
        
        return summary
    
    def _get_risk_recommendations(self) -> List[str]:
        """Get recommendations based on risk factors"""
        recommendations = []
        
        if self.risk_factors.get('missing_values', 0) > 40:
            recommendations.append('Address missing values - consider imputation strategies')
        
        if self.risk_factors.get('class_imbalance', 0) > 40:
            recommendations.append('Handle class imbalance - use SMOTE or class weights')
        
        if self.risk_factors.get('data_leakage', 0) > 30:
            recommendations.append('Investigate suspiciously high correlations for data leakage')
        
        if self.risk_factors.get('correlation', 0) > 40:
            recommendations.append('Remove multicollinear features before training')
        
        if self.risk_factors.get('outliers', 0) > 40:
            recommendations.append('Detect and handle extreme outliers')
        
        if self.risk_factors.get('duplicates', 0) > 20:
            recommendations.append('Remove duplicate rows to prevent data leakage')
        
        return recommendations or ['Dataset risk level is acceptable']
