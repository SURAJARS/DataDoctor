"""
Data Cleaning Recommendations Module
Provides actionable data cleaning steps
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np


class DataCleaner:
    """Provides data cleaning recommendations"""
    
    def __init__(self, df: pd.DataFrame, analysis_results: Dict[str, Any]):
        """
        Initialize cleaner
        
        Args:
            df: Input DataFrame
            analysis_results: Analysis results from DatasetAnalyzer
        """
        self.df = df
        self.analysis_results = analysis_results
        self.cleaning_steps = []
    
    def generate_cleaning_plan(self) -> Dict[str, Any]:
        """Generate comprehensive cleaning plan"""
        self.cleaning_steps = []
        
        self._add_missing_value_steps()
        self._add_duplicate_steps()
        self._add_constant_feature_steps()
        self._add_outlier_steps()
        self._add_type_correction_steps()
        self._add_scaling_steps()
        
        return {
            'cleaning_steps': self._prioritize_steps(),
            'estimated_time': self._estimate_time(),
            'implementation_commands': self._get_implementation_script()
        }
    
    def _add_missing_value_steps(self):
        """Add steps for handling missing values"""
        missing_data = self.analysis_results.get('missing_values', {}).get('columns_with_missing', {})
        
        for col, info in missing_data.items():
            missing_pct = info.get('percentage', 0)
            severity = info.get('severity', 'low')
            
            if missing_pct > 50:
                self.cleaning_steps.append({
                    'category': 'Missing Values',
                    'priority': 'Critical',
                    'action': f'Drop column "{col}"',
                    'reason': f'{missing_pct}% missing values - too much data loss if imputed',
                    'code': f'df = df.drop(columns=["{col}"])',
                    'reversible': True
                })
            elif missing_pct > 30:
                self.cleaning_steps.append({
                    'category': 'Missing Values',
                    'priority': 'High',
                    'action': f'Impute column "{col}" with domain knowledge',
                    'reason': f'{missing_pct}% missing values',
                    'code': f'df["{col}"].fillna(df["{col}"].median(), inplace=True)  # or use KNN imputation',
                    'reversible': False
                })
            elif missing_pct > 5:
                self.cleaning_steps.append({
                    'category': 'Missing Values',
                    'priority': 'Medium',
                    'action': f'Impute column "{col}"',
                    'reason': f'{missing_pct}% missing values',
                    'code': f'df["{col}"].fillna(df["{col}"].mode()[0], inplace=True)',
                    'reversible': False
                })
    
    def _add_duplicate_steps(self):
        """Add steps for handling duplicates"""
        dup_data = self.analysis_results.get('duplicates', {})
        dup_pct = dup_data.get('duplicate_rows_percentage', 0)
        dup_cols = dup_data.get('duplicate_columns', [])
        
        if dup_pct > 0:
            self.cleaning_steps.append({
                'category': 'Duplicates',
                'priority': 'High' if dup_pct > 10 else 'Medium',
                'action': 'Remove duplicate rows',
                'reason': f'{dup_pct}% duplicate rows detected',
                'code': 'df = df.drop_duplicates()',
                'reversible': True
            })
        
        for dup_pair in dup_cols:
            self.cleaning_steps.append({
                'category': 'Duplicate Columns',
                'priority': 'Medium',
                'action': f'Drop duplicate column "{dup_pair["col2"]}"',
                'reason': f'Column "{dup_pair["col2"]}" is identical to "{dup_pair["col1"]}"',
                'code': f'df = df.drop(columns=["{dup_pair["col2"]}"])',
                'reversible': True
            })
    
    def _add_constant_feature_steps(self):
        """Add steps for removing constant features"""
        const_data = self.analysis_results.get('constant_features', {})
        const_features = const_data.get('constant_features', [])
        near_const = const_data.get('near_constant_features', [])
        
        if const_features:
            self.cleaning_steps.append({
                'category': 'Redundant Features',
                'priority': 'High',
                'action': f'Drop constant features: {", ".join(const_features)}',
                'reason': 'Constant features provide no predictive value',
                'code': f'df = df.drop(columns={const_features})',
                'reversible': True
            })
        
        for near_const_info in near_const:
            col = near_const_info['column']
            unique_ratio = near_const_info['unique_ratio']
            
            self.cleaning_steps.append({
                'category': 'Redundant Features',
                'priority': 'Medium',
                'action': f'Consider dropping "{col}"',
                'reason': f'Near-constant feature with only {unique_ratio*100:.2f}% unique values',
                'code': f'# Uncomment if not needed: df = df.drop(columns=["{col}"])',
                'reversible': True
            })
    
    def _add_outlier_steps(self):
        """Add steps for handling outliers"""
        outlier_data = self.analysis_results.get('outliers', {})
        outlier_detection = outlier_data.get('outlier_detection', {})
        
        for col, info in outlier_detection.items():
            iqr_outliers = info.get('iqr_outliers', 0)
            outlier_pct = info.get('outlier_percentage', 0)
            
            if iqr_outliers > 0 and outlier_pct > 1:
                self.cleaning_steps.append({
                    'category': 'Outliers',
                    'priority': 'Medium',
                    'action': f'Cap outliers in "{col}"',
                    'reason': f'{iqr_outliers} outliers detected ({outlier_pct}%)',
                    'code': f'''
Q1 = df["{col}"].quantile(0.25)
Q3 = df["{col}"].quantile(0.75)
IQR = Q3 - Q1
df["{col}"] = df["{col}"].clip(lower=Q1-1.5*IQR, upper=Q3+1.5*IQR)
                    '''.strip(),
                    'reversible': True
                })
    
    def _add_type_correction_steps(self):
        """Add steps for correcting data types"""
        type_data = self.analysis_results.get('data_types', {})
        mixed_types = type_data.get('mixed_type_columns', {})
        
        if mixed_types:
            for col in mixed_types:
                self.cleaning_steps.append({
                    'category': 'Data Types',
                    'priority': 'Medium',
                    'action': f'Investigate and convert "{col}" to consistent type',
                    'reason': f'Column "{col}" has mixed data types',
                    'code': f'# Investigate: df["{col}"].apply(type).value_counts()',
                    'reversible': False
                })
    
    def _add_scaling_steps(self):
        """Add steps for scaling features"""
        scaling_issues = self.analysis_results.get('feature_scaling', {}).get('scaling_issues', [])
        
        if scaling_issues:
            affected_cols = [issue['column'] for issue in scaling_issues]
            
            self.cleaning_steps.append({
                'category': 'Feature Scaling',
                'priority': 'High',
                'action': f'Scale columns: {", ".join(affected_cols[:3])}',
                'reason': 'Features have very different scales',
                'code': f'''
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df[{affected_cols[:3]}] = scaler.fit_transform(df[{affected_cols[:3]}])
                '''.strip(),
                'reversible': False
            })
    
    def _prioritize_steps(self) -> List[Dict[str, Any]]:
        """Prioritize cleaning steps"""
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        
        return sorted(
            self.cleaning_steps,
            key=lambda x: priority_order.get(x.get('priority', 'Low'), 99)
        )
    
    def _estimate_time(self) -> str:
        """Estimate time to complete cleaning"""
        critical = sum(1 for s in self.cleaning_steps if s['priority'] == 'Critical')
        high = sum(1 for s in self.cleaning_steps if s['priority'] == 'High')
        medium = sum(1 for s in self.cleaning_steps if s['priority'] == 'Medium')
        
        # Rough estimate: 2 min per critical, 1.5 min per high, 1 min per medium
        estimated_minutes = (critical * 2) + (high * 1.5) + (medium * 1)
        
        if estimated_minutes < 5:
            return 'Quick (< 5 minutes)'
        elif estimated_minutes < 15:
            return 'Moderate (5-15 minutes)'
        elif estimated_minutes < 60:
            return f'Significant ({int(estimated_minutes)-10}-{int(estimated_minutes)+10} minutes)'
        else:
            hours = estimated_minutes / 60
            return f'Extensive (>{int(hours)} hours)'
    
    def _get_implementation_script(self) -> str:
        """Get Python script for all cleaning steps"""
        script = """
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load data
df = pd.read_csv('your_data.csv')

# ===== CLEANING STEPS =====

"""
        
        for i, step in enumerate(self._prioritize_steps(), 1):
            script += f"\n# Step {i}: {step['action']}\n"
            script += f"# {step['reason']}\n"
            script += f"{step['code']}\n\n"
        
        script += """
# ===== SAVE CLEANED DATA =====
df.to_csv('cleaned_data.csv', index=False)
print("Data cleaning complete!")
"""
        
        return script
