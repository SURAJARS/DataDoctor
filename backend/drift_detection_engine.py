"""
Data Drift Detection Engine
Detects distribution shifts between datasets (train vs test)
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class DriftDetectionEngine:
    """Detects data drift between two datasets"""
    
    def __init__(self, df_train: pd.DataFrame, df_test: pd.DataFrame):
        """
        Initialize drift detector
        
        Args:
            df_train: Training dataset
            df_test: Test dataset
        """
        self.df_train = df_train
        self.df_test = df_test
        self.drift_results = {}
    
    def detect_all_drifts(self, threshold: float = 0.05) -> Dict[str, Any]:
        """
        Detect all types of data drift
        
        Args:
            threshold: P-value threshold for statistical tests (default: 0.05)
        
        Returns:
            Comprehensive drift report
        """
        numeric_cols = self.df_train.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df_train.select_dtypes(include=['object']).columns.tolist()
        
        drift_summary = {
            'total_features': len(numeric_cols) + len(categorical_cols),
            'features_with_drift': 0,
            'feature_drifts': [],
            'target_drift': None,
            'overall_drift_risk': 'LOW'
        }
        
        # Check numeric columns
        for col in numeric_cols:
            drift_result = self._detect_numeric_drift(col, threshold)
            if drift_result:
                drift_summary['features_with_drift'] += 1
                drift_summary['feature_drifts'].append(drift_result)
        
        # Check categorical columns
        for col in categorical_cols:
            drift_result = self._detect_categorical_drift(col, threshold)
            if drift_result:
                drift_summary['features_with_drift'] += 1
                drift_summary['feature_drifts'].append(drift_result)
        
        # Calculate overall risk
        drift_pct = (drift_summary['features_with_drift'] / drift_summary['total_features']) * 100
        if drift_pct > 50:
            drift_summary['overall_drift_risk'] = 'CRITICAL'
        elif drift_pct > 30:
            drift_summary['overall_drift_risk'] = 'HIGH'
        elif drift_pct > 20:
            drift_summary['overall_drift_risk'] = 'MODERATE'
        else:
            drift_summary['overall_drift_risk'] = 'LOW'
        
        return {
            'status': 'success',
            'train_samples': len(self.df_train),
            'test_samples': len(self.df_test),
            'drift_detected': True if drift_summary['features_with_drift'] > 0 else False,
            'drift_summary': drift_summary,
            'recommendations': self._get_drift_recommendations(drift_summary)
        }
    
    def _detect_numeric_drift(self, col: str, threshold: float) -> Dict[str, Any]:
        """Detect drift in numeric column using KS test"""
        if col not in self.df_train.columns or col not in self.df_test.columns:
            return None
        
        train_col = self.df_train[col].dropna()
        test_col = self.df_test[col].dropna()
        
        if len(train_col) == 0 or len(test_col) == 0:
            return None
        
        # Kolmogorov-Smirnov test
        ks_stat, p_value = stats.ks_2samp(train_col, test_col)
        
        # Statistical drift detection
        if p_value < threshold:
            # Also check effect size
            effect_size = abs(train_col.mean() - test_col.mean()) / np.sqrt((train_col.std()**2 + test_col.std()**2) / 2 + 1e-8)
            
            return {
                'feature': col,
                'type': 'numeric',
                'drift_detected': True,
                'ks_statistic': float(ks_stat),
                'p_value': float(p_value),
                'effect_size': float(effect_size),
                'train_mean': float(train_col.mean()),
                'test_mean': float(test_col.mean()),
                'train_std': float(train_col.std()),
                'test_std': float(test_col.std()),
                'drift_type': self._classify_numeric_drift(train_col, test_col),
                'severity': self._get_numeric_drift_severity(ks_stat, effect_size)
            }
        
        return None
    
    def _detect_categorical_drift(self, col: str, threshold: float) -> Dict[str, Any]:
        """Detect drift in categorical column using Chi-Square test"""
        if col not in self.df_train.columns or col not in self.df_test.columns:
            return None
        
        train_col = self.df_train[col].value_counts()
        test_col = self.df_test[col].value_counts()
        
        if len(train_col) == 0 or len(test_col) == 0:
            return None
        
        # Get common categories
        common_cats = set(train_col.index) & set(test_col.index)
        
        if len(common_cats) == 0:
            return {
                'feature': col,
                'type': 'categorical',
                'drift_detected': True,
                'p_value': 0.0,
                'drift_type': 'NEW_CATEGORIES',
                'severity': 'HIGH',
                'train_categories': len(train_col),
                'test_categories': len(test_col),
                'missing_categories': list(set(train_col.index) - set(test_col.index))[:5]
            }
        
        # Chi-square test
        observed = [test_col.get(cat, 0) for cat in common_cats]
        expected = [train_col.get(cat, 1) for cat in common_cats]
        
        chi2_stat, p_value = stats.chisquare(observed, expected)
        
        if p_value < threshold:
            return {
                'feature': col,
                'type': 'categorical',
                'drift_detected': True,
                'chi2_statistic': float(chi2_stat),
                'p_value': float(p_value),
                'train_categories': len(train_col),
                'test_categories': len(test_col),
                'common_categories': len(common_cats),
                'drift_type': 'DISTRIBUTION_SHIFT',
                'severity': self._get_categorical_drift_severity(chi2_stat)
            }
        
        return None
    
    @staticmethod
    def _classify_numeric_drift(train_col: pd.Series, test_col: pd.Series) -> str:
        """Classify type of numeric drift"""
        mean_diff = abs(train_col.mean() - test_col.mean())
        std_diff = abs(train_col.std() - test_col.std())
        
        if mean_diff > train_col.std():
            return 'MEAN_SHIFT'
        elif std_diff > train_col.std() * 0.5:
            return 'VARIANCE_SHIFT'
        else:
            return 'DISTRIBUTION_SHIFT'
    
    @staticmethod
    def _get_numeric_drift_severity(ks_stat: float, effect_size: float) -> str:
        """Get severity of numeric drift"""
        if ks_stat > 0.3 or effect_size > 1.0:
            return 'CRITICAL'
        elif ks_stat > 0.2 or effect_size > 0.5:
            return 'HIGH'
        elif ks_stat > 0.1:
            return 'MODERATE'
        else:
            return 'LOW'
    
    @staticmethod
    def _get_categorical_drift_severity(chi2_stat: float) -> str:
        """Get severity of categorical drift"""
        if chi2_stat > 50:
            return 'CRITICAL'
        elif chi2_stat > 20:
            return 'HIGH'
        elif chi2_stat > 10:
            return 'MODERATE'
        else:
            return 'LOW'
    
    @staticmethod
    def _get_drift_recommendations(drift_summary: Dict) -> List[str]:
        """Generate recommendations based on drift"""
        recommendations = []
        risk = drift_summary.get('overall_drift_risk', 'LOW')
        
        if risk == 'CRITICAL':
            recommendations.append('⚠️ CRITICAL: Model retraining recommended immediately')
            recommendations.append('Review feature engineering pipeline')
            recommendations.append('Investigate root cause of distribution shift')
        
        elif risk == 'HIGH':
            recommendations.append('Consider model retraining with recent data')
            recommendations.append('Monitor drift-affected features closely')
            recommendations.append('Implement automated retraining triggers')
        
        elif risk == 'MODERATE':
            recommendations.append('Schedule regular model evaluation')
            recommendations.append('Set up drift monitoring dashboard')
            recommendations.append('Plan for model update in next cycle')
        
        else:
            recommendations.append('✓ Dataset distribution is stable')
            recommendations.append('Continue regular monitoring')
        
        return recommendations
