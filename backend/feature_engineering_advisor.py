"""
Feature Engineering Advisor Module
Recommends transformations and feature engineering techniques
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd


class FeatureEngineeringAdvisor:
    """Recommends feature engineering transformations"""
    
    def __init__(self, df: pd.DataFrame, analysis_results: Dict[str, Any]):
        """
        Initialize advisor
        
        Args:
            df: Input DataFrame
            analysis_results: Analysis results from DatasetAnalyzer
        """
        self.df = df
        self.analysis_results = analysis_results
        self.recommendations = []
    
    def generate_recommendations(self) -> Dict[str, Any]:
        """Generate feature engineering recommendations"""
        self.recommendations = []
        
        self._recommend_scaling()
        self._recommend_transformations()
        self._recommend_encoding()
        self._recommend_feature_creation()
        self._recommend_feature_selection()
        self._recommend_handling_special_cases()
        
        return {
            'recommendations': self.recommendations,
            'priority_ranking': self._rank_recommendations(),
            'implementation_guide': self._get_implementation_guide()
        }
    
    def _recommend_scaling(self):
        """Recommend scaling techniques"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        scaling_issues = self.analysis_results.get('feature_scaling', {}).get('scaling_issues', [])
        
        if scaling_issues:
            self.recommendations.append({
                'category': 'Scaling',
                'priority': 'High',
                'issue': 'Features have different scales',
                'recommendation': 'StandardScaler or MinMaxScaler',
                'affected_columns': [issue['column'] for issue in scaling_issues],
                'reason': 'Algorithms like KNN, SVM, and Neural Networks are sensitive to feature scaling.',
                'code_snippet': 'from sklearn.preprocessing import StandardScaler; scaler = StandardScaler(); X_scaled = scaler.fit_transform(X)'
            })
    
    def _recommend_transformations(self):
        """Recommend data transformations"""
        dist_info = self.analysis_results.get('distribution', {}).get('distribution_analysis', {})
        
        for col, info in dist_info.items():
            # Log transformation for skewed features
            if info.get('is_skewed') == 'Yes':
                skewness = info.get('skewness', 0)
                if abs(skewness) > 1:
                    self.recommendations.append({
                        'category': 'Transformation',
                        'priority': 'Medium',
                        'issue': f'Column "{col}" is highly skewed (skewness: {skewness:.2f})',
                        'recommendation': 'Log transformation or Box-Cox transformation',
                        'affected_columns': [col],
                        'reason': 'Skewed distributions can negatively impact model performance.',
                        'code_snippet': f'df["{col}"] = np.log1p(df["{col}"])'
                    })
    
    def _recommend_encoding(self):
        """Recommend categorical encoding"""
        cat_cols = self.df.select_dtypes(include=['object']).columns
        
        high_card_features = self.analysis_results.get('cardinality', {}).get('high_cardinality_features', [])
        
        for col in cat_cols:
            unique_count = self.df[col].nunique()
            
            if unique_count <= 10:
                self.recommendations.append({
                    'category': 'Encoding',
                    'priority': 'High',
                    'issue': f'Categorical column "{col}" with {unique_count} categories',
                    'recommendation': 'One-Hot Encoding',
                    'affected_columns': [col],
                    'reason': 'Most ML algorithms require numerical input. One-Hot encoding prevents ordinal bias.',
                    'code_snippet': f'df = pd.get_dummies(df, columns=["{col}"])'
                })
            elif col in high_card_features:
                self.recommendations.append({
                    'category': 'Encoding',
                    'priority': 'Medium',
                    'issue': f'High-cardinality categorical column "{col}" with {unique_count} unique values',
                    'recommendation': 'Target encoding or Frequency encoding',
                    'affected_columns': [col],
                    'reason': 'One-Hot encoding creates too many features. Use target encoding instead.',
                    'code_snippet': 'target_mean = df.groupby(col)[target].mean(); df[col] = df[col].map(target_mean)'
                })
            else:
                self.recommendations.append({
                    'category': 'Encoding',
                    'priority': 'Medium',
                    'issue': f'Categorical column "{col}" with {unique_count} categories',
                    'recommendation': 'Label Encoding or OrdinalEncoder',
                    'affected_columns': [col],
                    'reason': 'Convert categorical to ordinal values.',
                    'code_snippet': f'from sklearn.preprocessing import LabelEncoder; le = LabelEncoder(); df["{col}"] = le.fit_transform(df["{col}"])'
                })
    
    def _recommend_feature_creation(self):
        """Recommend feature creation strategies"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            self.recommendations.append({
                'category': 'Feature Creation',
                'priority': 'Medium',
                'issue': 'Limited feature set for modeling',
                'recommendation': 'Create interaction features and polynomial features',
                'affected_columns': numeric_cols[:3],
                'reason': 'New features can improve model performance and capture non-linear relationships.',
                'code_snippet': 'df["feature1_x_feature2"] = df["feature1"] * df["feature2"]'
            })
        
        # Datetime feature engineering
        datetime_cols = self.analysis_results.get('data_types', {}).get('datetime_columns', [])
        
        if datetime_cols:
            self.recommendations.append({
                'category': 'Feature Creation',
                'priority': 'High',
                'issue': 'Datetime columns not engineered',
                'recommendation': 'Extract year, month, day, dayofweek, hour from datetime',
                'affected_columns': datetime_cols,
                'reason': 'Datetime components often have predictive power.',
                'code_snippet': 'df["year"] = pd.to_datetime(df["date"]).dt.year'
            })
    
    def _recommend_feature_selection(self):
        """Recommend feature selection"""
        const_features = self.analysis_results.get('constant_features', {}).get('constant_features', [])
        
        if const_features:
            self.recommendations.append({
                'category': 'Feature Selection',
                'priority': 'Critical',
                'issue': 'Constant features provide no signal',
                'recommendation': 'Remove constant features',
                'affected_columns': const_features,
                'reason': 'Constant features waste model capacity and provide no predictive value.',
                'code_snippet': f'df = df.drop(columns={const_features})'
            })
        
        # Multicollinearity
        high_corr_pairs = self.analysis_results.get('correlation', {}).get('high_correlations', [])
        
        if high_corr_pairs:
            features_to_drop = set()
            for pair in high_corr_pairs[:5]:  # Top 5 pairs
                features_to_drop.add(pair['feature2'])  # Keep feature1, drop feature2
            
            if features_to_drop:
                self.recommendations.append({
                    'category': 'Feature Selection',
                    'priority': 'High',
                    'issue': 'High multicollinearity detected',
                    'recommendation': 'Remove highly correlated features',
                    'affected_columns': list(features_to_drop),
                    'reason': 'Highly correlated features increase model complexity without adding new information.',
                    'code_snippet': f'df = df.drop(columns={list(features_to_drop)})'
                })
    
    def _recommend_handling_special_cases(self):
        """Recommend handling for special cases"""
        # Missing values
        missing_cols = self.analysis_results.get('missing_values', {}).get('columns_with_missing', {})
        
        if missing_cols:
            self.recommendations.append({
                'category': 'Missing Value Handling',
                'priority': 'Critical',
                'issue': f'{len(missing_cols)} columns have missing values',
                'recommendation': 'Imputation (mean, median, KNN, or model-based)',
                'affected_columns': list(missing_cols.keys()),
                'reason': 'Most ML algorithms cannot handle missing values.',
                'code_snippet': 'df.fillna(df.mean(), inplace=True)  # or use SimpleImputer'
            })
        
        # Rare categories
        rare_categories = self.analysis_results.get('rare_category', {}).get('rare_categories', {})
        
        if rare_categories:
            self.recommendations.append({
                'category': 'Rare Category Handling',
                'priority': 'Medium',
                'issue': 'Rare categories detected in categorical features',
                'recommendation': 'Group rare categories into "Other" category',
                'affected_columns': list(rare_categories.keys()),
                'reason': 'Rare categories can cause overfitting and sparse encoding.',
                'code_snippet': 'df[col] = df[col].where(df[col].value_counts()[df[col]] > threshold, "Other")'
            })
        
        # Outliers
        outlier_data = self.analysis_results.get('outliers', {})
        total_outliers = sum(
            v.get('iqr_outliers', 0) 
            for v in outlier_data.get('outlier_detection', {}).values()
        )
        
        if total_outliers > 0:
            self.recommendations.append({
                'category': 'Outlier Handling',
                'priority': 'Medium',
                'issue': f'{total_outliers} outliers detected',
                'recommendation': 'Remove, cap, or transform outliers',
                'affected_columns': [k for k, v in outlier_data.get('outlier_detection', {}).items() if v.get('iqr_outliers', 0) > 0],
                'reason': 'Outliers can significantly impact model performance.',
                'code_snippet': 'Q1 = df[col].quantile(0.25); Q3 = df[col].quantile(0.75); df[col] = df[col].clip(lower=Q1-1.5*(Q3-Q1), upper=Q3+1.5*(Q3-Q1))'
            })
    
    def _rank_recommendations(self) -> List[Dict[str, Any]]:
        """Rank recommendations by priority"""
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        
        return sorted(
            self.recommendations,
            key=lambda x: priority_order.get(x.get('priority', 'Low'), 99)
        )
    
    def _get_implementation_guide(self) -> str:
        """Get step-by-step implementation guide"""
        guide = """
        ## Feature Engineering Implementation Guide

        ### Step 1: Handle Missing Values
        - Use SimpleImputer for numerical features (mean/median)
        - Use fill_na for categorical features (most frequent)

        ### Step 2: Remove Redundant Features
        - Drop constant features
        - Drop one feature from each highly correlated pair

        ### Step 3: Encode Categorical Variables
        - Use One-Hot Encoding for low-cardinality features
        - Use Target Encoding for high-cardinality features

        ### Step 4: Handle Outliers
        - Cap outliers using IQR method
        - Or remove extreme outliers if they're data errors

        ### Step 5: Transform Skewed Features
        - Apply log transformation for right-skewed distributions
        - Apply Box-Cox transformation for better results

        ### Step 6: Scale Numerical Features
        - Use StandardScaler for normally distributed features
        - Use MinMaxScaler for features with known bounds

        ### Step 7: Create New Features
        - Extract datetime components if applicable
        - Create interaction features for important pairs
        - Create polynomial features if appropriate

        ### Step 8: Feature Selection
        - Use feature importance from tree-based models
        - Use RFE (Recursive Feature Elimination)
        - Use SelectKBest for statistical tests

        ### Step 9: Validation
        - Check for data leakage
        - Ensure train-test split is done before transformation
        - Validate on hold-out test set
        """
        
        return guide
