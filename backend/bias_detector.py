"""
Bias Detection Module
Detects bias in datasets
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class BiasDetector:
    """Detects various types of bias in datasets"""
    
    def __init__(self, df: pd.DataFrame, target_column: str = None, sensitive_features: List[str] = None):
        """
        Initialize bias detector
        
        Args:
            df: Input DataFrame
            target_column: Target variable column name
            sensitive_features: List of sensitive demographic features
        """
        self.df = df
        self.target_column = target_column
        self.sensitive_features = sensitive_features or []
        self.bias_findings = []
    
    def detect_all_biases(self) -> Dict[str, Any]:
        """Detect all types of bias"""
        self.bias_findings = []
        
        self._detect_class_imbalance_bias()
        self._detect_demographic_bias()
        self._detect_representation_bias()
        self._detect_measurement_bias()
        self._detect_selection_bias()
        
        return {
            'bias_findings': self.bias_findings,
            'bias_risk_level': self._assess_risk_level(),
            'recommendations': self._generate_recommendations()
        }
    
    def _detect_class_imbalance_bias(self):
        """Detect bias from class imbalance"""
        if self.target_column is None or self.target_column not in self.df.columns:
            return
        
        target = self.df[self.target_column]
        class_dist = target.value_counts(normalize=True)
        
        # Check for severe imbalance
        if len(class_dist) > 1:
            max_class_pct = class_dist.max() * 100
            min_class_pct = class_dist.min() * 100
            
            if max_class_pct > 90:
                self.bias_findings.append({
                    'type': 'Class Imbalance',
                    'severity': 'High',
                    'description': f'Majority class represents {max_class_pct:.1f}% of data',
                    'impact': 'Model may be biased towards majority class',
                    'mitigation': 'Use SMOTE, class weights, or stratified sampling'
                })
    
    def _detect_demographic_bias(self):
        """Detect bias across demographic groups"""
        if self.target_column is None or len(self.sensitive_features) == 0:
            return
        
        target = self.df[self.target_column]
        
        for feature in self.sensitive_features:
            if feature not in self.df.columns:
                continue
            
            # Calculate target rate by demographic group
            groups = self.df.groupby(feature)[self.target_column].agg(['count', 'sum'])
            groups['positive_rate'] = groups['sum'] / groups['count']
            
            # Detect disparate impact
            min_rate = groups['positive_rate'].min()
            max_rate = groups['positive_rate'].max()
            
            if min_rate > 0 and (max_rate / min_rate) > 1.25:  # 4/5 rule
                self.bias_findings.append({
                    'type': 'Demographic Bias',
                    'severity': 'High',
                    'feature': feature,
                    'description': f'Disparate positive rates: {min_rate:.1%} to {max_rate:.1%}',
                    'impact': 'Different demographic groups have different model outcomes',
                    'mitigation': 'Apply fairness constraints or use bias-aware training'
                })
    
    def _detect_representation_bias(self):
        """Detect representation bias (missing groups)"""
        if len(self.sensitive_features) == 0:
            return
        
        for feature in self.sensitive_features:
            if feature not in self.df.columns:
                continue
            
            total_samples = len(self.df)
            group_sizes = self.df[feature].value_counts()
            
            # Identify underrepresented groups
            for group, size in group_sizes.items():
                group_pct = (size / total_samples) * 100
                
                if group_pct < 5:
                    self.bias_findings.append({
                        'type': 'Representation Bias',
                        'severity': 'Medium',
                        'feature': feature,
                        'group': str(group),
                        'description': f'Group represents only {group_pct:.1f}% of data',
                        'impact': 'Underrepresented groups may have poor model performance',
                        'mitigation': 'Collect more data for underrepresented groups or use weighted losses'
                    })
    
    def _detect_measurement_bias(self):
        """Detect measurement bias (data quality issues)"""
        # Check for missing values by demographic groups
        if len(self.sensitive_features) == 0:
            return
        
        for feature in self.sensitive_features:
            if feature not in self.df.columns:
                continue
            
            # Calculate missing value rate by group
            for col in self.df.columns:
                missing_by_group = self.df.groupby(feature)[col].apply(
                    lambda x: x.isnull().sum() / len(x)
                )
                
                if missing_by_group.max() - missing_by_group.min() > 0.2:
                    self.bias_findings.append({
                        'type': 'Measurement Bias',
                        'severity': 'Medium',
                        'feature': feature,
                        'column': col,
                        'description': f'Missing data rates vary significantly by {feature}',
                        'impact': 'Different data quality for different demographic groups',
                        'mitigation': 'Investigate data collection process for potential bias'
                    })
    
    def _detect_selection_bias(self):
        """Detect selection bias in data"""
        # Check for temporal patterns that might indicate selection bias
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            
            # Check if data looks artificially constrained
            if len(col_data) > 100:
                # Count values at boundaries
                min_val = col_data.min()
                max_val = col_data.max()
                
                at_min = (col_data == min_val).sum()
                at_max = (col_data == max_val).sum()
                
                total_at_boundaries = at_min + at_max
                boundary_pct = (total_at_boundaries / len(col_data)) * 100
                
                if boundary_pct > 5:
                    self.bias_findings.append({
                        'type': 'Selection Bias',
                        'severity': 'Low',
                        'feature': col,
                        'description': f'{boundary_pct:.1f}% of values at min/max boundaries',
                        'impact': 'Data may be subject to selection bias or capping',
                        'mitigation': 'Understand data collection and preprocessing steps'
                    })
    
    def _assess_risk_level(self) -> str:
        """Assess overall bias risk level"""
        if not self.bias_findings:
            return 'Low'
        
        high_severity = sum(1 for b in self.bias_findings if b.get('severity') == 'High')
        medium_severity = sum(1 for b in self.bias_findings if b.get('severity') == 'Medium')
        
        if high_severity >= 2:
            return 'Critical'
        elif high_severity >= 1:
            return 'High'
        elif medium_severity >= 3:
            return 'High'
        elif medium_severity >= 1:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_recommendations(self) -> List[str]:
        """Generate bias mitigation recommendations"""
        recommendations = []
        
        if not self.bias_findings:
            recommendations.append('No significant bias detected.')
        else:
            if any(b['type'] == 'Class Imbalance' for b in self.bias_findings):
                recommendations.append('Use SMOTE or class weights to address class imbalance.')
            
            if any(b['type'] == 'Demographic Bias' for b in self.bias_findings):
                recommendations.append('Apply fairness constraints (calibration, equalized odds).')
                recommendations.append('Use threshold adjustment for different demographic groups.')
            
            if any(b['type'] == 'Representation Bias' for b in self.bias_findings):
                recommendations.append('Collect more data for underrepresented groups.')
                recommendations.append('Use stratified sampling during model development.')
            
            if any(b['type'] == 'Measurement Bias' for b in self.bias_findings):
                recommendations.append('Investigate and standardize data collection process.')
                recommendations.append('Apply group-specific preprocessing if appropriate.')
            
            recommendations.append('Use fairness metrics (disparate impact ratio, equalized odds, etc.) when evaluating models.')
            recommendations.append('Document and communicate limitations of the model across demographic groups.')
        
        return recommendations
