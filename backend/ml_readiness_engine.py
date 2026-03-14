"""
ML Readiness Engine
Predicts whether dataset is suitable for ML training
"""

from typing import Dict, Any, List
import numpy as np


class MLReadinessEngine:
    """Evaluates ML readiness of dataset"""
    
    def __init__(self, analysis_results: Dict[str, Any], df_shape: tuple):
        """
        Initialize ML Readiness Engine
        
        Args:
            analysis_results: Dictionary from DatasetAnalyzer.analyze_all()
            df_shape: (num_rows, num_cols) tuple
        """
        self.analysis_results = analysis_results
        self.num_rows, self.num_cols = df_shape
        self.ml_readiness_score = 100
        self.issues = []
        self.warnings = []
    
    def evaluate(self) -> Dict[str, Any]:
        """Evaluate ML readiness"""
        self.ml_readiness_score = 100
        self.issues = []
        self.warnings = []
        
        self._check_dataset_size()
        self._check_features()
        self._check_target_variable()
        self._check_data_quality()
        self._check_feature_distribution()
        self._check_feature_relationships()
        
        # Ensure score is 0-100
        self.ml_readiness_score = max(0, min(100, self.ml_readiness_score))
        
        return {
            'ml_readiness_score': round(self.ml_readiness_score, 1),
            'readiness_status': self._get_readiness_status(),
            'critical_blockers': [i for i in self.issues if i['severity'] == 'critical'],
            'warnings': self.warnings,
            'recommendations': self._get_recommendations(),
            'estimated_training_difficulty': self._estimate_difficulty()
        }
    
    def _check_dataset_size(self):
        """Check if dataset size is suitable for ML"""
        if self.num_rows < 100:
            self.issues.append({
                'severity': 'critical',
                'issue': 'insufficient_samples',
                'description': f'Only {self.num_rows} samples. Need at least 100-1000 samples for meaningful ML.'
            })
            self.ml_readiness_score -= 20
        elif self.num_rows < 1000:
            self.warnings.append(
                f'Small dataset ({self.num_rows} rows). Results may be unreliable.'
            )
            self.ml_readiness_score -= 10
        
        if self.num_cols < 2:
            self.issues.append({
                'severity': 'critical',
                'issue': 'insufficient_features',
                'description': 'Dataset has fewer than 2 features. Need features for ML.'
            })
            self.ml_readiness_score -= 20
    
    def _check_features(self):
        """Check feature quality"""
        const_features = len(
            self.analysis_results.get('constant_features', {}).get('constant_features', [])
        )
        
        if const_features > 0:
            self.issues.append({
                'severity': 'high',
                'issue': 'constant_features',
                'description': f'{const_features} constant features provide no signal for ML.'
            })
            self.ml_readiness_score -= 15
        
        # Check feature scaling
        scaling_issues = len(
            self.analysis_results.get('feature_scaling', {}).get('scaling_issues', [])
        )
        
        if scaling_issues > 0:
            self.warnings.append(
                f'{scaling_issues} features need scaling before training.'
            )
            self.ml_readiness_score -= 5
    
    def _check_target_variable(self):
        """Check target variable quality"""
        imbalance_data = self.analysis_results.get('class_imbalance', {})
        imbalance_ratio = imbalance_data.get('imbalance_ratio', 1)
        status = imbalance_data.get('status', '')
        
        if status == 'severely_imbalanced' and imbalance_ratio > 10:
            self.issues.append({
                'severity': 'high',
                'issue': 'severe_class_imbalance',
                'description': f'Target variable has severe imbalance ({imbalance_ratio:.1f}:1). '
                             'Requires special handling (SMOTE, class weights, etc.).'
            })
            self.ml_readiness_score -= 15
        elif status == 'moderately_imbalanced':
            self.warnings.append(
                f'Target variable moderately imbalanced ({imbalance_ratio:.1f}:1). '
                'Consider using class weights or resampling.'
            )
            self.ml_readiness_score -= 8
    
    def _check_data_quality(self):
        """Check overall data quality"""
        missing_pct = self.analysis_results.get('missing_values', {}).get('missing_percentage', 0)
        
        if missing_pct > 40:
            self.issues.append({
                'severity': 'critical',
                'issue': 'excessive_missing_data',
                'description': f'{missing_pct}% missing values. Data too incomplete for training.'
            })
            self.ml_readiness_score -= 25
        elif missing_pct > 20:
            self.warnings.append(
                f'{missing_pct}% missing values. Will need imputation strategy.'
            )
            self.ml_readiness_score -= 10
        
        # Check duplicates
        dup_pct = self.analysis_results.get('duplicates', {}).get('duplicate_rows_percentage', 0)
        
        if dup_pct > 15:
            self.warnings.append(
                f'{dup_pct}% duplicate rows. May cause data leakage.'
            )
            self.ml_readiness_score -= 10
    
    def _check_feature_distribution(self):
        """Check feature distributions"""
        dist_info = self.analysis_results.get('distribution', {}).get('distribution_analysis', {})
        
        skewed_features = []
        for col, info in dist_info.items():
            if info.get('is_skewed') == 'Yes':
                skewed_features.append(col)
        
        if len(skewed_features) > len(dist_info) * 0.5:  # More than 50% skewed
            self.warnings.append(
                f'{len(skewed_features)} features are highly skewed. '
                'Consider log transformation or power transformation.'
            )
            self.ml_readiness_score -= 8
    
    def _check_feature_relationships(self):
        """Check correlations and multicollinearity"""
        high_corr_pairs = len(
            self.analysis_results.get('correlation', {}).get('high_correlations', [])
        )
        
        if high_corr_pairs > 10:
            self.warnings.append(
                f'High multicollinearity detected ({high_corr_pairs} highly correlated pairs). '
                'Consider feature selection or PCA.'
            )
            self.ml_readiness_score -= 12
        elif high_corr_pairs > 0:
            self.warnings.append(
                f'{high_corr_pairs} highly correlated feature pairs. '
                'May need feature selection.'
            )
            self.ml_readiness_score -= 5
    
    def _get_readiness_status(self) -> str:
        """Get readiness status"""
        critical_issues = [i for i in self.issues if i['severity'] == 'critical']
        
        if critical_issues:
            return 'NOT_READY'
        elif self.ml_readiness_score >= 85:
            return 'READY'
        elif self.ml_readiness_score >= 70:
            return 'MOSTLY_READY'
        elif self.ml_readiness_score >= 50:
            return 'NEEDS_PREPARATION'
        else:
            return 'NOT_RECOMMENDED'
    
    def _get_recommendations(self) -> List[str]:
        """Get actionable recommendations"""
        recommendations = []
        
        if len(self.issues) > 0:
            recommendations.append('Address critical blockers before training.')
        
        # Missing value strategy
        missing_pct = self.analysis_results.get('missing_values', {}).get('missing_percentage', 0)
        if missing_pct > 5:
            recommendations.append(
                'Implement imputation strategy (mean, median, KNN, or model-based).'
            )
        
        # Scaling recommendation
        const_features = self.analysis_results.get('constant_feature', {}).get('constant_features', [])
        if len(const_features) > 0:
            recommendations.append(
                f'Remove constant features: {", ".join(const_features[:5])}...'
            )
        
        # Feature scaling
        if self.ml_readiness_score < 80:
            recommendations.append(
                'Normalize/standardize numerical features (StandardScaler or MinMaxScaler).'
            )
        
        # Data splitting
        if self.num_rows > 1000:
            recommendations.append(
                'Use stratified train-test split due to class imbalance.'
            )
        
        # Class imbalance handling
        imbalance_ratio = self.analysis_results.get('class_imbalance', {}).get('imbalance_ratio', 1)
        if imbalance_ratio > 3:
            recommendations.append(
                'Use SMOTE or class weights to handle class imbalance.'
            )
        
        # Feature engineering
        if self.num_cols < 15:
            recommendations.append(
                'Consider feature engineering to create more predictive features.'
            )
        
        return recommendations
    
    def _estimate_difficulty(self) -> Dict[str, Any]:
        """Estimate ML training difficulty"""
        difficulty_factors = {
            'data_quality': 'Good' if self.analysis_results.get('missing_values', {}).get('missing_percentage', 0) < 10 else 'Poor',
            'class_balance': 'Balanced' if self.analysis_results.get('class_imbalance', {}).get('imbalance_ratio', 1) < 1.5 else 'Imbalanced',
            'feature_quality': 'Good' if len(self.analysis_results.get('constant_features', {}).get('constant_features', [])) == 0 else 'Poor',
            'feature_count': 'Adequate' if self.num_cols >= 5 else 'Insufficient',
            'sample_count': 'Adequate' if self.num_rows >= 1000 else 'Small',
        }
        
        # Estimate training difficulty
        negative_factors = sum(1 for v in difficulty_factors.values() if v in ['Poor', 'Imbalanced', 'Insufficient', 'Small'])
        
        if negative_factors == 0:
            difficulty = 'Easy'
        elif negative_factors <= 2:
            difficulty = 'Moderate'
        elif negative_factors <= 4:
            difficulty = 'Hard'
        else:
            difficulty = 'Very Hard'
        
        return {
            'difficulty_level': difficulty,
            'factors': difficulty_factors,
            'estimated_effort': 'Low (~1-2 hours)' if difficulty == 'Easy' else
                               'Medium (~3-4 hours)' if difficulty == 'Moderate' else
                               'High (~5-8 hours)' if difficulty == 'Hard' else
                               'Very High (>8 hours)'
        }
