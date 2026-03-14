"""
Dataset Health Scoring Engine
Calculates overall dataset health score
"""

from typing import Dict, Any
import math


class ScoringEngine:
    """Scoring system for dataset health"""
    
    def __init__(self, analysis_results: Dict[str, Any]):
        """
        Initialize scoring engine
        
        Args:
            analysis_results: Dictionary from DatasetAnalyzer.analyze_all()
        """
        self.analysis_results = analysis_results
        self.score = 100
        self.issues = []
    
    def calculate_health_score(self) -> Dict[str, Any]:
        """Calculate overall dataset health score (0-100)"""
        self.score = 100
        self.issues = []
        
        # Missing values penalty
        self._score_missing_values()
        
        # Duplicates penalty
        self._score_duplicates()
        
        # Class imbalance penalty
        self._score_class_imbalance()
        
        # Outliers penalty
        self._score_outliers()
        
        # Correlation/multicollinearity penalty
        self._score_correlation()
        
        # Constant features penalty
        self._score_constant_features()
        
        # Data drift penalty
        self._score_data_drift()
        
        # Data type issues penalty
        self._score_data_types()
        
        # Ensure score is between 0-100
        self.score = max(0, min(100, self.score))
        
        return {
            'dataset_health_score': round(self.score, 1),
            'score_breakdown': self._get_score_breakdown(),
            'critical_issues': self._get_critical_issues(),
            'warnings': self._get_warnings(),
            'overall_status': self._get_status(),
            'recommendation': self._get_recommendation()
        }
    
    def _score_missing_values(self):
        """Penalty for missing values"""
        missing_data = self.analysis_results.get('missing_values', {})
        missing_pct = missing_data.get('missing_percentage', 0)
        
        if missing_pct > 50:
            penalty = 30
            self.issues.append({
                'severity': 'critical',
                'type': 'missing_values',
                'description': f'Critical missing values: {missing_pct}% of data is missing'
            })
        elif missing_pct > 30:
            penalty = 20
            self.issues.append({
                'severity': 'high',
                'type': 'missing_values',
                'description': f'High missing values: {missing_pct}% of data is missing'
            })
        elif missing_pct > 10:
            penalty = 10
            self.issues.append({
                'severity': 'medium',
                'type': 'missing_values',
                'description': f'Moderate missing values: {missing_pct}% of data is missing'
            })
        elif missing_pct > 5:
            penalty = 5
        else:
            penalty = 0
        
        self.score -= penalty
    
    def _score_duplicates(self):
        """Penalty for duplicate rows"""
        dup_data = self.analysis_results.get('duplicates', {})
        dup_pct = dup_data.get('duplicate_rows_percentage', 0)
        dup_cols = len(dup_data.get('duplicate_columns', []))
        
        if dup_pct > 20:
            self.score -= 15
            self.issues.append({
                'severity': 'high',
                'type': 'duplicates',
                'description': f'{dup_pct}% duplicate rows detected'
            })
        elif dup_pct > 5:
            self.score -= 8
            self.issues.append({
                'severity': 'medium',
                'type': 'duplicates',
                'description': f'{dup_pct}% duplicate rows detected'
            })
        
        if dup_cols > 0:
            self.score -= 10
            self.issues.append({
                'severity': 'high',
                'type': 'duplicate_columns',
                'description': f'{dup_cols} duplicate column pairs detected'
            })
    
    def _score_class_imbalance(self):
        """Penalty for class imbalance"""
        imbalance_data = self.analysis_results.get('class_imbalance', {})
        imbalance_ratio = imbalance_data.get('imbalance_ratio', 1)
        status = imbalance_data.get('status', '')
        
        if status == 'severely_imbalanced' and imbalance_ratio > 0:
            self.score -= 15
            self.issues.append({
                'severity': 'high',
                'type': 'class_imbalance',
                'description': f'Severe class imbalance: {imbalance_ratio:.1f}:1 ratio'
            })
        elif status == 'moderately_imbalanced':
            self.score -= 8
            self.issues.append({
                'severity': 'medium',
                'type': 'class_imbalance',
                'description': f'Moderate class imbalance: {imbalance_ratio:.1f}:1 ratio'
            })
    
    def _score_outliers(self):
        """Penalty for outliers"""
        outlier_data = self.analysis_results.get('outliers', {})
        outlier_detection = outlier_data.get('outlier_detection', {})
        
        total_outliers = sum(
            v.get('iqr_outliers', 0) for v in outlier_detection.values()
        )
        
        if total_outliers > 0:
            # Calculate outlier percentage
            total_data_points = sum(
                self.analysis_results.get('missing_values', {}).get('total_missing', 0)
                for _ in range(1)  # Placeholder
            )
            
            if total_outliers > 100:
                self.score -= 12
                self.issues.append({
                    'severity': 'high',
                    'type': 'outliers',
                    'description': f'{total_outliers} outliers detected'
                })
            else:
                self.score -= 5
    
    def _score_correlation(self):
        """Penalty for multicollinearity"""
        corr_data = self.analysis_results.get('correlation', {})
        high_corr_pairs = len(corr_data.get('high_correlations', []))
        
        if high_corr_pairs > 5:
            self.score -= 15
            self.issues.append({
                'severity': 'high',
                'type': 'multicollinearity',
                'description': f'{high_corr_pairs} highly correlated feature pairs'
            })
        elif high_corr_pairs > 0:
            self.score -= 8
            self.issues.append({
                'severity': 'medium',
                'type': 'multicollinearity',
                'description': f'{high_corr_pairs} highly correlated feature pairs'
            })
    
    def _score_constant_features(self):
        """Penalty for constant features"""
        const_data = self.analysis_results.get('constant_features', {})
        const_features = len(const_data.get('constant_features', []))
        near_const = len(const_data.get('near_constant_features', []))
        
        if const_features > 0:
            self.score -= 10
            self.issues.append({
                'severity': 'high',
                'type': 'constant_features',
                'description': f'{const_features} constant/redundant columns'
            })
        
        if near_const > 0:
            self.score -= 5
    
    def _score_data_drift(self):
        """Penalty for data drift indicators"""
        drift_data = self.analysis_results.get('data_drift', {})
        drift_indicators = len(drift_data.get('drift_indicators', []))
        
        if drift_indicators > 0:
            self.score -= 8
            self.issues.append({
                'severity': 'medium',
                'type': 'data_drift',
                'description': f'Data drift indicators detected in {drift_indicators} columns'
            })
    
    def _score_data_types(self):
        """Penalty for data type issues"""
        type_data = self.analysis_results.get('data_types', {})
        mixed_types = len(type_data.get('mixed_type_columns', {}))
        
        if mixed_types > 0:
            self.score -= 8
            self.issues.append({
                'severity': 'medium',
                'type': 'mixed_types',
                'description': f'{mixed_types} columns have mixed data types'
            })
    
    def _get_score_breakdown(self) -> Dict[str, float]:
        """Get detailed score breakdown"""
        return {
            'missing_values_impact': 30,
            'duplicates_impact': 15,
            'class_imbalance_impact': 15,
            'outliers_impact': 12,
            'multicollinearity_impact': 15,
            'redundant_features_impact': 10,
            'data_drift_impact': 8,
            'data_types_impact': 5
        }
    
    def _get_critical_issues(self) -> list:
        """Get critical issues only"""
        return [issue for issue in self.issues if issue['severity'] == 'critical']
    
    def _get_warnings(self) -> list:
        """Get all issues"""
        return self.issues
    
    def _get_status(self) -> str:
        """Get overall status"""
        if self.score >= 80:
            return 'Excellent'
        elif self.score >= 70:
            return 'Good'
        elif self.score >= 60:
            return 'Fair'
        elif self.score >= 50:
            return 'Poor'
        else:
            return 'Critical'
    
    def _get_recommendation(self) -> str:
        """Get recommendation based on score"""
        if self.score >= 80:
            return 'Dataset is ready for ML training. Proceed with model development.'
        elif self.score >= 70:
            return 'Dataset is mostly ready. Consider addressing medium-severity issues.'
        elif self.score >= 60:
            return 'Dataset needs attention. Address high-severity issues before ML training.'
        elif self.score >= 50:
            return 'Dataset has significant quality issues. Major cleaning required.'
        else:
            return 'Dataset quality is critical. Extensive data preparation required before ML use.'
