"""
Feature Importance Engine
Trains quick baseline models and computes feature importance
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')


class FeatureImportanceEngine:
    """Computes feature importance using quick baseline models"""
    
    def __init__(self, df: pd.DataFrame, target_column: str = None):
        """
        Initialize engine
        
        Args:
            df: Input DataFrame
            target_column: Target variable column name
        """
        self.df = df
        self.target_column = target_column
        self.importance_results = {}
    
    def compute_feature_importance(self) -> Dict[str, Any]:
        """Compute feature importance"""
        if self.target_column is None or self.target_column not in self.df.columns:
            # Fallback: compute statistical importance without target column
            return self._compute_statistical_importance()
        
        try:
            # Prepare data
            X, y = self._prepare_data()
            
            if X is None or len(X) < 10:
                return {
                    'status': 'insufficient_data',
                    'importance_scores': {},
                    'top_features': []
                }
            
            # Train models and get importance
            importance_dict = {}
            
            try:
                # Random Forest (if classification or regression works)
                if y.dtype == 'object' or len(np.unique(y)) < 20:
                    # Classification
                    model = RandomForestClassifier(
                        n_estimators=100,
                        random_state=42,
                        n_jobs=-1
                    )
                else:
                    # Regression
                    model = RandomForestRegressor(
                        n_estimators=100,
                        random_state=42,
                        n_jobs=-1
                    )
                
                model.fit(X, y)
                
                # Get feature importance
                importance_dict = dict(zip(X.columns, model.feature_importances_))
            except Exception as e:
                return {
                    'status': f'error_training_model: {str(e)}',
                    'importance_scores': {},
                    'top_features': []
                }
            
            # Sort by importance
            sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'status': 'success',
                'importance_scores': {k: round(v, 4) for k, v in importance_dict.items()},
                'top_features': [
                    {'feature': k, 'importance': round(v, 4), 'rank': i+1}
                    for i, (k, v) in enumerate(sorted_importance[:10])
                ],
                'model_type': 'RandomForest',
                'accuracy': round(model.score(X, y), 4) if hasattr(model, 'score') else None
            }
        
        except Exception as e:
            return {
                'status': f'error: {str(e)}',
                'importance_scores': {},
                'top_features': []
            }
    
    def _compute_statistical_importance(self) -> Dict[str, Any]:
        """Compute feature importance using statistical analysis (no target column needed)"""
        try:
            importance_scores = {}
            
            # Analyze numeric columns
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if self.df[col].isnull().sum() > 0:
                    continue
                
                # Compute statistical importance metrics
                mean_val = self.df[col].mean()
                std_val = self.df[col].std()
                range_val = self.df[col].max() - self.df[col].min()
                variance = self.df[col].var()
                
                # Combine into importance score (0-1 normalized)
                if std_val == 0:
                    importance = 0.01
                else:
                    # Score based on variance and range
                    importance = min(1.0, (variance / (mean_val ** 2 + 1)) * 0.5 + (range_val / (abs(mean_val) + 1)) * 0.5)
                
                importance_scores[col] = max(0.01, round(importance, 4))
            
            # Analyze categorical columns by cardinality
            categorical_cols = self.df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if self.df[col].isnull().sum() > 0:
                    continue
                
                # Importance based on cardinality and entropy
                unique_count = len(self.df[col].unique())
                total_count = len(self.df)
                cardinality_ratio = unique_count / total_count
                
                # Lower importance for too high or too low cardinality
                if cardinality_ratio > 0.9 or cardinality_ratio < 0.01:
                    importance = 0.1
                else:
                    importance = cardinality_ratio
                
                importance_scores[col] = round(importance, 4)
            
            # Normalize scores so they sum to 1
            if importance_scores:
                total = sum(importance_scores.values())
                importance_scores = {k: v/total for k, v in importance_scores.items()}
            
            # Sort by importance
            sorted_importance = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'status': 'statistical_analysis',
                'importance_scores': importance_scores,
                'top_features': [
                    {'feature': k, 'importance': round(v, 4), 'rank': i+1}
                    for i, (k, v) in enumerate(sorted_importance[:15])
                ],
                'model_type': 'Statistical Analysis',
                'note': 'Feature importance computed from statistical properties (no target column available)'
            }
        
        except Exception as e:
            return {
                'status': f'error: {str(e)}',
                'importance_scores': {},
                'top_features': []
            }
    
    def _prepare_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for model training"""
        try:
            # Remove target column
            X = self.df.drop(columns=[self.target_column])
            y = self.df[self.target_column]
            
            # Remove rows with missing target
            valid_idx = ~y.isnull()
            X = X[valid_idx]
            y = y[valid_idx]
            
            if len(X) == 0:
                return None, None
            
            # Handle missing values in features
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            categorical_cols = X.select_dtypes(include=['object']).columns
            
            # Fill numeric missing values with median
            for col in numeric_cols:
                if X[col].isnull().sum() > 0:
                    X[col].fillna(X[col].median(), inplace=True)
            
            # Encode categorical columns
            label_encoders = {}
            for col in categorical_cols:
                if X[col].isnull().sum() > 0:
                    X[col].fillna('MISSING', inplace=True)
                
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                label_encoders[col] = le
            
            # Encode target if categorical
            if y.dtype == 'object':
                le = LabelEncoder()
                y = le.fit_transform(y.astype(str))
            
            return X, y
        
        except Exception as e:
            return None, None
