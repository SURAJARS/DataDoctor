"""
AutoML Baseline Engine
Trains baseline models and provides model performance metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, mean_squared_error, r2_score, mean_absolute_error
)
import warnings
warnings.filterwarnings('ignore')


class AutoMLEngine:
    """Automated ML baseline model training and evaluation"""
    
    def __init__(self):
        self.model = None
        self.problem_type = None
        self.feature_encoders = {}
        self.target_encoder = None
        self.feature_columns = None
        self.numeric_features = []
        self.categorical_features = []
    
    def detect_problem_type(self, target_series: pd.Series) -> str:
        """
        Detect if problem is classification or regression
        
        Args:
            target_series: Target column series
        
        Returns:
            'classification' or 'regression'
        """
        # Remove NaN values for analysis
        target_clean = target_series.dropna()
        
        # Check if target is numeric
        if pd.api.types.is_numeric_dtype(target_series):
            unique_count = len(target_clean.unique())
            value_range = target_clean.max() - target_clean.min()
            
            # If few unique values or categorical-like, treat as classification
            if unique_count <= 20 or (unique_count <= 100 and value_range < 1000):
                return 'classification'
            else:
                return 'regression'
        else:
            # Non-numeric target is classification
            return 'classification'
    
    def prepare_data(self, df: pd.DataFrame, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare data for modeling
        
        Args:
            df: Input dataframe
            target_column: Name of target column
        
        Returns:
            X (features), y (target)
        """
        # Handle missing target values
        df_clean = df.dropna(subset=[target_column]).copy()
        
        if len(df_clean) == 0:
            raise ValueError(f"No valid target values in {target_column}")
        
        # Separate features and target
        X = df_clean.drop(columns=[target_column])
        y = df_clean[target_column]
        
        # Store feature columns for later use
        self.feature_columns = X.columns.tolist()
        
        # Identify numeric and categorical features
        self.numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Fill missing values
        for col in self.numeric_features:
            X[col].fillna(X[col].median(), inplace=True)
        
        for col in self.categorical_features:
            X[col].fillna(X[col].mode().values[0] if len(X[col].mode()) > 0 else 'Unknown', inplace=True)
        
        # Encode categorical features
        for col in self.categorical_features:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.feature_encoders[col] = le
        
        # Encode target if classification
        self.problem_type = self.detect_problem_type(y)
        if self.problem_type == 'classification':
            self.target_encoder = LabelEncoder()
            y = self.target_encoder.fit_transform(y.astype(str))
        
        return X, y
    
    def train_baseline(self, X: pd.DataFrame, y: pd.Series, 
                      test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """
        Train baseline model
        
        Args:
            X: Features dataframe
            y: Target series
            test_size: Test set fraction
            random_state: Random seed
        
        Returns:
            Results dictionary
        """
        # Split data with stratification for classification to handle imbalanced classes
        if self.problem_type == 'classification':
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
        
        # Train model
        if self.problem_type == 'classification':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=random_state,
                n_jobs=-1,
                class_weight='balanced'  # Handle class imbalance
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=random_state,
                n_jobs=-1
            )
        
        self.model.fit(X_train, y_train)
        
        # Get predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics based on problem type
        results = {
            'model_type': self.model.__class__.__name__,
            'problem_type': self.problem_type,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'feature_count': X.shape[1]
        }
        
        if self.problem_type == 'classification':
            results.update(self._calculate_classification_metrics(y_test, y_pred))
        else:
            results.update(self._calculate_regression_metrics(y_test, y_pred))
        
        # Calculate feature importance
        results['top_features'] = self._get_top_features(X.columns)
        
        return results
    
    def _calculate_classification_metrics(self, y_true: np.ndarray, 
                                          y_pred: np.ndarray) -> Dict[str, Any]:
        """Calculate classification metrics"""
        accuracy = accuracy_score(y_true, y_pred)
        
        # Determine number of classes
        unique_classes = len(np.unique(y_true))
        
        # Use 'macro' average which treats all classes equally regardless of imbalance
        # Use 'binary' for actual binary classification
        average_method = 'binary' if unique_classes == 2 else 'macro'
        
        try:
            # Use zero_division=1 to avoid returning 0 metrics when no true positives
            # This prevents misleading 0 scores due to class imbalance in test set
            precision = precision_score(y_true, y_pred, average=average_method, zero_division=1)
            recall = recall_score(y_true, y_pred, average=average_method, zero_division=1)
            f1 = f1_score(y_true, y_pred, average=average_method, zero_division=1)
        except Exception as e:
            # Fallback if there's an issue with metric calculation
            print(f"Warning: Error calculating metrics: {e}")
            precision = accuracy  # Fallback to accuracy
            recall = accuracy
            f1 = accuracy
        
        cm = confusion_matrix(y_true, y_pred).tolist()
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': cm
        }
    
    def _calculate_regression_metrics(self, y_true: np.ndarray, 
                                       y_pred: np.ndarray) -> Dict[str, Any]:
        """Calculate regression metrics"""
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        return {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2_score': float(r2)
        }
    
    def _get_top_features(self, feature_names: List[str], top_n: int = 10) -> List[Dict[str, Any]]:
        """Extract top N features by importance"""
        if self.model is None:
            return []
        
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]
        
        top_features = []
        for idx in indices:
            if idx < len(feature_names):
                top_features.append({
                    'feature': feature_names[idx],
                    'importance': float(importances[idx])
                })
        
        return top_features
    
    def train_and_evaluate(self, df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """
        Complete workflow: prepare data and train model
        
        Args:
            df: Input dataframe
            target_column: Name of target column
        
        Returns:
            Complete results dictionary
        """
        try:
            # Sample if dataset is too large
            if len(df) > 50000:
                df = df.sample(n=50000, random_state=42)
            
            # Prepare data
            X, y = self.prepare_data(df, target_column)
            
            # Train and evaluate
            results = self.train_baseline(X, y)
            
            results['status'] = 'success'
            return results
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
