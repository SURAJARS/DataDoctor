"""
Core Dataset Analyzer Module
Performs comprehensive quality checks on datasets
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')


class DatasetAnalyzer:
    """Main dataset analyzer class"""
    
    def __init__(self, df: pd.DataFrame, target_column: str = None):
        """
        Initialize analyzer
        
        Args:
            df: Input DataFrame
            target_column: Name of target column for ML tasks
        """
        self.df = df
        self.target_column = target_column
        self.num_rows = len(df)
        self.num_cols = len(df.columns)
        self.analysis_results = {}
    
    def analyze_all(self) -> Dict[str, Any]:
        """Run all analysis checks"""
        self.analysis_results = {
            'missing_values': self._analyze_missing_values(),
            'duplicates': self._analyze_duplicates(),
            'data_types': self._analyze_data_types(),
            'cardinality': self._analyze_cardinality(),
            'outliers': self._analyze_outliers(),
            'distribution': self._analyze_distribution(),
            'correlation': self._analyze_correlation(),
            'class_imbalance': self._analyze_class_imbalance(),
            'feature_scaling': self._analyze_feature_scaling(),
            'constant_features': self._analyze_constant_features(),
            'data_drift': self._analyze_data_drift(),
            'rare_categories': self._analyze_rare_categories(),
            'data_quality': self._analyze_data_quality(),
        }
        return self.analysis_results
    
    def _analyze_missing_values(self) -> Dict[str, Any]:
        """Detect and analyze missing values"""
        missing_data = {}
        total_cells = self.num_rows * self.num_cols
        total_missing = self.df.isnull().sum().sum()
        
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            missing_pct = (missing_count / self.num_rows) * 100
            
            if missing_count > 0:
                missing_data[col] = {
                    'count': int(missing_count),
                    'percentage': round(missing_pct, 2),
                    'severity': 'critical' if missing_pct > 50 else 
                               'high' if missing_pct > 30 else
                               'medium' if missing_pct > 10 else 'low'
                }
        
        return {
            'total_missing': int(total_missing),
            'missing_percentage': round((total_missing / total_cells) * 100, 2),
            'columns_with_missing': missing_data,
            'status': 'clean' if total_missing == 0 else 'has_missing_values'
        }
    
    def _analyze_duplicates(self) -> Dict[str, Any]:
        """Detect duplicate rows and columns"""
        # Duplicate rows
        duplicate_rows = self.df.duplicated().sum()
        duplicate_rows_pct = (duplicate_rows / self.num_rows) * 100
        
        # Duplicate columns
        duplicate_cols = []
        cols_list = self.df.columns.tolist()
        for i in range(len(cols_list)):
            for j in range(i+1, len(cols_list)):
                if self.df[cols_list[i]].equals(self.df[cols_list[j]]):
                    duplicate_cols.append({
                        'col1': cols_list[i],
                        'col2': cols_list[j]
                    })
        
        return {
            'duplicate_rows': int(duplicate_rows),
            'duplicate_rows_percentage': round(duplicate_rows_pct, 2),
            'duplicate_columns': duplicate_cols,
            'status': 'no_duplicates' if duplicate_rows == 0 and len(duplicate_cols) == 0 else 'duplicates_found'
        }
    
    def _analyze_data_types(self) -> Dict[str, Any]:
        """Analyze data types and detect issues"""
        type_info = {}
        mixed_types = {}
        
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            type_info[col] = dtype
            
            # Check for mixed types
            if dtype == 'object':
                try:
                    # Try to infer better type
                    inferred_type = pd.api.types.infer_dtype(self.df[col])
                    if inferred_type == 'mixed':
                        mixed_types[col] = True
                except:
                    pass
        
        return {
            'column_types': type_info,
            'mixed_type_columns': mixed_types,
            'numeric_columns': self.df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': self.df.select_dtypes(include=['object']).columns.tolist(),
            'datetime_columns': self.df.select_dtypes(include=['datetime']).columns.tolist(),
        }
    
    def _analyze_cardinality(self) -> Dict[str, Any]:
        """Analyze feature cardinality"""
        cardinality_info = {}
        high_cardinality = []
        
        for col in self.df.columns:
            unique_count = self.df[col].nunique()
            cardinality_ratio = unique_count / self.num_rows
            
            cardinality_info[col] = {
                'unique_values': int(unique_count),
                'cardinality_ratio': round(cardinality_ratio, 4)
            }
            
            # High cardinality detection
            if cardinality_ratio > 0.9:
                high_cardinality.append(col)
        
        return {
            'cardinality_by_column': cardinality_info,
            'high_cardinality_features': high_cardinality,
            'status': 'normal' if len(high_cardinality) == 0 else 'high_cardinality_detected'
        }
    
    def _analyze_outliers(self) -> Dict[str, Any]:
        """Multi-method outlier detection"""
        outlier_info = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            
            # Z-score method
            z_scores = np.abs(stats.zscore(col_data))
            z_outliers = int((z_scores > 3).sum())
            
            # IQR method
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            iqr_outliers = int(((col_data < (Q1 - 1.5 * IQR)) | (col_data > (Q3 + 1.5 * IQR))).sum())
            
            # Isolation Forest
            try:
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                iso_predictions = iso_forest.fit_predict(col_data.values.reshape(-1, 1))
                iso_outliers = int((iso_predictions == -1).sum())
            except:
                iso_outliers = 0
            
            outlier_info[col] = {
                'z_score_outliers': z_outliers,
                'iqr_outliers': iqr_outliers,
                'isolation_forest_outliers': iso_outliers,
                'outlier_percentage': round((iqr_outliers / len(col_data)) * 100, 2)
            }
        
        return {
            'outlier_detection': outlier_info,
            'status': 'no_outliers' if all(v['iqr_outliers'] == 0 for v in outlier_info.values()) else 'outliers_found'
        }
    
    def _analyze_distribution(self) -> Dict[str, Any]:
        """Analyze feature distributions"""
        dist_info = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            
            if len(col_data) > 0:
                # Skewness
                skewness = col_data.skew()
                # Kurtosis
                kurtosis = col_data.kurtosis()
                
                # KS test for normality
                ks_stat, ks_pvalue = stats.kstest(col_data, 'norm', args=(col_data.mean(), col_data.std()))
                
                dist_info[col] = {
                    'mean': round(float(col_data.mean()), 4),
                    'median': round(float(col_data.median()), 4),
                    'std': round(float(col_data.std()), 4),
                    'min': round(float(col_data.min()), 4),
                    'max': round(float(col_data.max()), 4),
                    'skewness': round(float(skewness), 4),
                    'kurtosis': round(float(kurtosis), 4),
                    'ks_test_pvalue': round(float(ks_pvalue), 4),
                    'is_normal': 'Yes' if ks_pvalue > 0.05 else 'No',
                    'is_skewed': 'Yes' if abs(skewness) > 1 else 'No'
                }
        
        return {
            'distribution_analysis': dist_info,
            'status': 'normal_distributions' if all(v.get('is_normal') == 'Yes' for v in dist_info.values()) else 'skewed_distributions'
        }
    
    def _analyze_correlation(self) -> Dict[str, Any]:
        """Analyze feature correlations"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'correlation_matrix': {}, 'high_correlations': [], 'status': 'insufficient_numeric_features'}
        
        corr_matrix = self.df[numeric_cols].corr()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.9:  # High correlation threshold
                    high_corr_pairs.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': round(float(corr_val), 4)
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'high_correlations': high_corr_pairs,
            'multicollinearity_detected': len(high_corr_pairs) > 0,
            'status': 'multicollinearity_issues' if len(high_corr_pairs) > 0 else 'healthy_correlations'
        }
    
    def _analyze_class_imbalance(self) -> Dict[str, Any]:
        """Detect class imbalance in target column"""
        if self.target_column is None or self.target_column not in self.df.columns:
            return {'status': 'no_target_column', 'class_distribution': {}}
        
        target = self.df[self.target_column]
        class_counts = target.value_counts().to_dict()
        class_pcts = target.value_counts(normalize=True).to_dict()
        
        # Calculate imbalance ratio
        if len(class_counts) > 1:
            max_count = max(class_counts.values())
            min_count = min(class_counts.values())
            imbalance_ratio = max_count / min_count
        else:
            imbalance_ratio = 1.0
        
        return {
            'class_distribution': {str(k): int(v) for k, v in class_counts.items()},
            'class_percentages': {str(k): round(v * 100, 2) for k, v in class_pcts.items()},
            'imbalance_ratio': round(imbalance_ratio, 4),
            'status': 'balanced' if imbalance_ratio < 1.5 else 'moderately_imbalanced' if imbalance_ratio < 3 else 'severely_imbalanced'
        }
    
    def _analyze_feature_scaling(self) -> Dict[str, Any]:
        """Detect feature scaling issues"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        scaling_issues = []
        
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            if len(col_data) == 0:
                continue
            
            std = col_data.std()
            mean = col_data.mean()
            value_range = col_data.max() - col_data.min()
            
            # Check if features have very different scales
            if std > 1000 or value_range > 10000:
                scaling_issues.append({
                    'column': col,
                    'range': round(value_range, 2),
                    'std': round(std, 2),
                    'severity': 'high'
                })
        
        return {
            'scaling_issues': scaling_issues,
            'status': 'needs_scaling' if len(scaling_issues) > 0 else 'well_scaled'
        }
    
    def _analyze_constant_features(self) -> Dict[str, Any]:
        """Detect constant and near-constant features"""
        constant_features = []
        near_constant_features = []
        
        for col in self.df.columns:
            unique_ratio = self.df[col].nunique() / len(self.df)
            
            if self.df[col].nunique() == 1:
                constant_features.append(col)
            elif unique_ratio < 0.01:  # Less than 1% unique values
                near_constant_features.append({
                    'column': col,
                    'unique_ratio': round(unique_ratio, 4)
                })
        
        return {
            'constant_features': constant_features,
            'near_constant_features': near_constant_features,
            'status': 'redundant_features' if len(constant_features) > 0 or len(near_constant_features) > 0 else 'no_constant_features'
        }
    
    def _analyze_data_drift(self) -> Dict[str, Any]:
        """Detect potential data drift indicators"""
        drift_indicators = []
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            if len(col_data) < 100:
                continue
            
            # Check for unusual range
            mean = col_data.mean()
            std = col_data.std()
            
            # Detect values far from expected range
            outlier_count = ((col_data < mean - 5*std) | (col_data > mean + 5*std)).sum()
            outlier_pct = (outlier_count / len(col_data)) * 100
            
            if outlier_pct > 5:
                drift_indicators.append({
                    'column': col,
                    'drift_indicator': 'extreme_values',
                    'percentage': round(outlier_pct, 2)
                })
        
        return {
            'drift_indicators': drift_indicators,
            'status': 'drift_detected' if len(drift_indicators) > 0 else 'no_drift'
        }
    
    def _analyze_rare_categories(self) -> Dict[str, Any]:
        """Detect rare categories in categorical features"""
        rare_categories = {}
        cat_cols = self.df.select_dtypes(include=['object']).columns
        
        for col in cat_cols:
            value_counts = self.df[col].value_counts()
            total_count = len(self.df)
            
            rare_cats = []
            for cat, count in value_counts.items():
                pct = (count / total_count) * 100
                if pct < 1:  # Less than 1%
                    rare_cats.append({
                        'category': str(cat),
                        'percentage': round(pct, 2)
                    })
            
            if rare_cats:
                rare_categories[col] = rare_cats
        
        return {
            'rare_categories': rare_categories,
            'status': 'rare_categories_found' if rare_categories else 'no_rare_categories'
        }
    
    def _analyze_data_quality(self) -> Dict[str, Any]:
        """Comprehensive data quality assessment"""
        quality_score = 100
        issues = []
        
        # Deduct for missing values
        missing_pct = self.analysis_results.get('missing_values', {}).get('missing_percentage', 0)
        if missing_pct > 30:
            quality_score -= 20
            issues.append(f'High missing values: {missing_pct}%')
        elif missing_pct > 10:
            quality_score -= 10
        
        # Deduct for duplicates
        dup_rows_pct = self.analysis_results.get('duplicates', {}).get('duplicate_rows_percentage', 0)
        if dup_rows_pct > 10:
            quality_score -= 15
            issues.append(f'High duplicate rows: {dup_rows_pct}%')
        
        # Deduct for outliers
        total_outliers = sum(v.get('iqr_outliers', 0) for v in self.analysis_results.get('outliers', {}).get('outlier_detection', {}).values())
        if total_outliers > 0:
            quality_score -= 5
            issues.append(f'Outliers detected: {total_outliers}')
        
        # Deduct for scaling issues
        if len(self.analysis_results.get('feature_scaling', {}).get('scaling_issues', [])) > 0:
            quality_score -= 5
            issues.append('Features need scaling')
        
        # Deduct for constant features
        if len(self.analysis_results.get('constant_features', {}).get('constant_features', [])) > 0:
            quality_score -= 10
            issues.append('Constant features detected')
        
        return {
            'quality_score': max(0, quality_score),
            'issues': issues,
            'status': 'excellent' if quality_score >= 80 else 'good' if quality_score >= 60 else 'poor'
        }
