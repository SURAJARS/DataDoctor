"""
Model Suggestion Engine
Recommends models based on dataset properties
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List


class ModelSuggestionEngine:
    """Suggest appropriate models based on dataset characteristics"""
    
    def __init__(self):
        self.dataset_properties = {}
    
    def analyze_dataset(self, df: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
        """
        Analyze dataset to identify key properties
        
        Args:
            df: Input dataframe
            target_column: Optional target column name
        
        Returns:
            Dictionary of dataset properties
        """
        properties = {
            'rows': len(df),
            'columns': len(df.columns),
            'numeric_features': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_features': len(df.select_dtypes(include=['object', 'category']).columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
        }
        
        # Analyze feature nonlinearity
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        properties['feature_nonlinearity'] = self._assess_nonlinearity(df[numeric_cols])
        
        # Analyze sparsity
        properties['sparsity_ratio'] = self._calculate_sparsity(df)
        
        # Analyze target if provided
        if target_column and target_column in df.columns:
            properties['target_type'] = self._get_target_type(df[target_column])
            properties['class_balance'] = self._assess_class_balance(df[target_column])
        
        self.dataset_properties = properties
        return properties
    
    def suggest_models(self, df: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
        """
        Suggest models based on dataset analysis
        
        Args:
            df: Input dataframe
            target_column: Optional target column name
        
        Returns:
            Dictionary with model suggestions and reasoning
        """
        # Analyze dataset
        properties = self.analyze_dataset(df, target_column)
        
        # Determine recommendations
        recommendations = []
        reasoning_parts = []
        
        rows = properties['rows']
        numeric_features = properties['numeric_features']
        categorical_features = properties['categorical_features']
        nonlinearity = properties['feature_nonlinearity']
        sparsity = properties['sparsity_ratio']
        
        # Determine if this is classification or regression
        is_classification = False
        if target_column and target_column in df.columns:
            target_type = properties.get('target_type', 'regression')
            is_classification = (target_type == 'classification')
        
        # Rule 1: Dataset size
        if rows < 10000:
            if 'RandomForest' not in recommendations:
                recommendations.append('RandomForest')
            reasoning_parts.append(f"Small dataset ({rows:,} rows) - RandomForest handles small data well")
            
            # Only recommend LogisticRegression for CLASSIFICATION problems with small datasets
            # Don't add it if RandomForest is already the primary recommendation
            if is_classification and rows < 5000 and numeric_features < 50 and len(recommendations) >= 2:
                if 'LogisticRegression' not in recommendations:
                    recommendations.append('LogisticRegression')
                reasoning_parts.append("Small dataset - LogisticRegression provides fast baseline for comparison")
        else:
            # Large dataset
            if 'LightGBM' not in recommendations:
                recommendations.append('LightGBM')
            reasoning_parts.append(f"Large dataset ({rows:,} rows) - LightGBM is efficient at scale")
            
            if 'XGBoost' not in recommendations:
                recommendations.append('XGBoost')
            reasoning_parts.append("Large dataset - XGBoost provides excellent performance")
        
        # Rule 2: Feature characteristics
        if numeric_features > categorical_features and numeric_features > 0:
            if 'RandomForest' not in recommendations:
                recommendations.append('RandomForest')
            reasoning_parts.append("Predominantly numeric features - RandomForest is ideal")
        
        if categorical_features > numeric_features and categorical_features > 0:
            if 'LightGBM' not in recommendations and rows > 5000:
                recommendations.append('LightGBM')
            reasoning_parts.append("High categorical feature count - LightGBM handles categoricals efficiently")
        
        # Rule 3: Feature nonlinearity
        if nonlinearity > 0.7:
            if 'RandomForest' not in recommendations:
                recommendations.append('RandomForest')
            reasoning_parts.append("Highly nonlinear features detected - RandomForest captures complex patterns")
        
        # Rule 4: Sparsity
        if sparsity > 0.5:
            if 'LightGBM' not in recommendations:
                recommendations.append('LightGBM')
            reasoning_parts.append("Sparse dataset - LightGBM handles sparsity efficiently")
        
        # Default recommendation if empty
        if not recommendations:
            if is_classification:
                recommendations = ['RandomForest', 'LightGBM']
                reasoning_parts.append("Balanced classification dataset - ensemble methods recommended")
            else:
                recommendations = ['RandomForest', 'LightGBM']
                reasoning_parts.append("Balanced regression dataset - ensemble methods recommended")
        
        # Build result
        result = {
            'recommended_models': list(dict.fromkeys(recommendations))[:3],  # Limit to top 3
            'reason': ' | '.join(reasoning_parts),
            'dataset_properties': properties
        }
        
        return result
    
    def _assess_nonlinearity(self, numeric_df: pd.DataFrame) -> float:
        """
        Assess feature nonlinearity (0 to 1)
        Higher values indicate more nonlinear relationships
        """
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return 0.5
        
        try:
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr(method='pearson').abs()
            
            # Average absolute correlation indicates linearity
            # Lower correlation = more nonlinearity opportunity
            avg_correlation = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
            
            # Invert: low correlation = high nonlinearity
            nonlinearity = 1 - min(avg_correlation, 1.0)
            return float(nonlinearity)
        except:
            return 0.5
    
    def _calculate_sparsity(self, df: pd.DataFrame) -> float:
        """
        Calculate sparsity ratio (0 to 1)
        Higher values indicate more sparse data (more zeros/nulls)
        """
        total_elements = df.size
        null_elements = df.isnull().sum().sum()
        zero_elements = (df == 0).sum().sum()
        
        sparse_elements = null_elements + zero_elements
        sparsity_ratio = sparse_elements / total_elements if total_elements > 0 else 0
        
        return float(min(sparsity_ratio, 1.0))
    
    def _get_target_type(self, target_series: pd.Series) -> str:
        """Determine if target is classification or regression"""
        if pd.api.types.is_numeric_dtype(target_series):
            unique_count = len(target_series.unique())
            if unique_count <= 20:
                return 'classification'
            else:
                return 'regression'
        else:
            return 'classification'
    
    def _assess_class_balance(self, target_series: pd.Series) -> Dict[str, Any]:
        """
        Assess class balance for classification targets
        
        Returns:
            Dictionary with balance metrics
        """
        value_counts = target_series.value_counts()
        
        if len(value_counts) <= 1:
            return {'balanced': True, 'ratio': 1.0}
        
        # Calculate balance ratio
        max_count = value_counts.max()
        min_count = value_counts.min()
        balance_ratio = min_count / max_count if max_count > 0 else 0
        
        # Threshold: ratio < 0.8 is considered imbalanced
        is_balanced = balance_ratio >= 0.8
        
        return {
            'balanced': is_balanced,
            'ratio': float(balance_ratio),
            'class_distribution': value_counts.to_dict()
        }
    
    def get_model_descriptions(self) -> Dict[str, str]:
        """Get descriptions of available models"""
        return {
            'RandomForest': 'Ensemble of decision trees. Great for mixed feature types and nonlinear patterns.',
            'XGBoost': 'Gradient boosting. Excellent accuracy, slower training. Best for large datasets.',
            'LightGBM': 'Fast gradient boosting. Efficient with large datasets and categorical features.',
            'LogisticRegression': 'Linear classifier. Fast, interpretable. Good for small datasets and linear relationships.',
            'SVM': 'Support Vector Machine. Good for high-dimensional data. Slow on large datasets.',
            'KNN': 'K-Nearest Neighbors. Simple, nonparametric. Fast prediction, slow training.',
            'NeuralNetwork': 'Deep learning. Excellent for complex patterns. Requires large dataset and careful tuning.',
            'GradientBoosting': 'Scikit-learn gradient boosting. Moderate speed, good accuracy.',
            'Ridge': 'Linear model with L2 regularization. Interpretable, handles collinearity.',
            'Lasso': 'Linear model with L1 regularization. Interpretable, feature selection.'
        }
