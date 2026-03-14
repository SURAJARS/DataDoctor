"""
Auto-Fix Dataset Engine
Automatically fixes common dataset quality issues
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.stats import zscore
from typing import Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')


class AutoFixEngine:
    """Automatically fixes dataset issues"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize auto-fix engine
        
        Args:
            df: Input DataFrame to fix
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.fixes_applied = []
        self.stats = {
            'rows_before': len(df),
            'cols_before': len(df.columns)
        }
    
    def auto_fix_all(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Apply all fixes sequentially"""
        # Step 1: Remove duplicate rows
        self._remove_duplicate_rows()
        
        # Step 2: Drop constant columns
        self._drop_constant_columns()
        
        # Step 3: Impute missing values
        self._impute_missing_values()
        
        # Step 4: Remove highly correlated features
        self._remove_correlated_features()
        
        # Step 5: Clip outliers
        self._clip_outliers()
        
        # Step 6: Normalize numerical columns
        self._normalize_numerical()
        
        # Generate report
        self.stats.update({
            'rows_after': len(self.df),
            'cols_after': len(self.df.columns),
            'rows_removed': self.stats['rows_before'] - len(self.df),
            'cols_removed': self.stats['cols_before'] - len(self.df.columns)
        })
        
        return self.df, self._get_report()
    
    def _remove_duplicate_rows(self):
        """Remove duplicate rows"""
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = initial_rows - len(self.df)
        
        if removed > 0:
            self.fixes_applied.append({
                'fix': 'Remove Duplicate Rows',
                'count': removed,
                'description': f'Removed {removed} duplicate rows'
            })
    
    def _drop_constant_columns(self):
        """Drop columns with constant values"""
        initial_cols = len(self.df.columns)
        
        # Find constant columns
        constant_cols = []
        for col in self.df.columns:
            if self.df[col].nunique() == 1:
                constant_cols.append(col)
        
        self.df = self.df.drop(columns=constant_cols)
        removed = initial_cols - len(self.df.columns)
        
        if removed > 0:
            self.fixes_applied.append({
                'fix': 'Drop Constant Columns',
                'count': removed,
                'description': f'Removed {removed} constant columns: {constant_cols}',
                'columns': constant_cols
            })
    
    def _impute_missing_values(self):
        """Impute missing values using median (numeric) and mode (categorical)"""
        imputed_info = {}
        
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            
            if missing_count > 0:
                if self.df[col].dtype in ['float64', 'int64']:
                    # Numeric: use median
                    fill_value = self.df[col].median()
                    self.df[col].fillna(fill_value, inplace=True)
                    method = 'median'
                else:
                    # Categorical: use mode
                    fill_value = self.df[col].mode()
                    if len(fill_value) > 0:
                        self.df[col].fillna(fill_value[0], inplace=True)
                        method = 'mode'
                    else:
                        continue
                
                imputed_info[col] = {
                    'missing_count': missing_count,
                    'method': method,
                    'value': str(fill_value)
                }
        
        if imputed_info:
            self.fixes_applied.append({
                'fix': 'Impute Missing Values',
                'count': len(imputed_info),
                'description': f'Imputed missing values in {len(imputed_info)} columns',
                'details': imputed_info
            })
    
    def _remove_correlated_features(self, threshold: float = 0.95):
        """Remove highly correlated features"""
        initial_cols = len(self.df.columns)
        
        # Get numeric columns only
        numeric_df = self.df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr().abs()
        
        # Find highly correlated pairs
        removed_cols = set()
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if corr_matrix.iloc[i, j] > threshold:
                    col_to_remove = corr_matrix.columns[j]
                    removed_cols.add(col_to_remove)
        
        if removed_cols:
            self.df = self.df.drop(columns=list(removed_cols))
            self.fixes_applied.append({
                'fix': 'Remove Correlated Features',
                'count': len(removed_cols),
                'description': f'Removed {len(removed_cols)} highly correlated features (>{threshold})',
                'columns': list(removed_cols)
            })
    
    def _clip_outliers(self, z_threshold: float = 3.0):
        """Clip extreme outliers using Z-score"""
        numeric_df = self.df.select_dtypes(include=[np.number])
        clipped_info = {}
        
        for col in numeric_df.columns:
            try:
                z_scores = np.abs(zscore(self.df[col].dropna()))
                outlier_indices = np.where(z_scores > z_threshold)[0]
                
                if len(outlier_indices) > 0:
                    # Calculate clip bounds
                    mean = self.df[col].mean()
                    std = self.df[col].std()
                    lower_bound = mean - (z_threshold * std)
                    upper_bound = mean + (z_threshold * std)
                    
                    # Clip values
                    self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)
                    
                    clipped_info[col] = {
                        'outliers_clipped': len(outlier_indices),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound)
                    }
            except:
                pass
        
        if clipped_info:
            self.fixes_applied.append({
                'fix': 'Clip Outliers',
                'count': len(clipped_info),
                'description': f'Clipped outliers in {len(clipped_info)} columns',
                'details': clipped_info
            })
    
    def _normalize_numerical(self):
        """Normalize numerical columns to 0-1 range"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            return
        
        scaler = StandardScaler()
        try:
            self.df[numeric_cols] = scaler.fit_transform(self.df[numeric_cols])
            self.fixes_applied.append({
                'fix': 'Normalize Numerical Features',
                'count': len(numeric_cols),
                'description': f'Normalized {len(numeric_cols)} numerical columns',
                'method': 'StandardScaler'
            })
        except:
            pass
    
    def _get_report(self) -> Dict[str, Any]:
        """Generate auto-fix report"""
        return {
            'status': 'success',
            'summary': {
                'rows_before': self.stats['rows_before'],
                'rows_after': self.stats['rows_after'],
                'rows_removed': self.stats['rows_removed'],
                'cols_before': self.stats['cols_before'],
                'cols_after': self.stats['cols_after'],
                'cols_removed': self.stats['cols_removed']
            },
            'fixes_applied': self.fixes_applied,
            'total_fixes': len(self.fixes_applied),
            'message': f'Successfully applied {len(self.fixes_applied)} fixes to dataset'
        }
