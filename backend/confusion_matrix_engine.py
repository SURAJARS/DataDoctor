"""
Confusion Matrix Engine
Generates and analyzes confusion matrices for classification tasks
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.metrics import confusion_matrix, classification_report


class ConfusionMatrixEngine:
    """Generate and analyze confusion matrices"""
    
    def __init__(self):
        self.confusion_matrix = None
        self.class_labels = None
    
    def generate_matrix(self, y_true: np.ndarray, y_pred: np.ndarray,
                       labels: List[str] = None) -> Dict[str, Any]:
        """
        Generate confusion matrix
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Optional class labels
        
        Returns:
            Dictionary with confusion matrix and metrics
        """
        # Get unique classes
        unique_classes = np.unique(np.concatenate([y_true, y_pred]))
        
        # Generate confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=unique_classes)
        self.confusion_matrix = cm
        self.class_labels = labels if labels else [str(c) for c in unique_classes]
        
        # Build result
        result = {
            'confusion_matrix': cm.tolist(),
            'class_labels': self.class_labels,
            'matrix_shape': cm.shape,
        }
        
        # Calculate per-class metrics
        if len(unique_classes) == 2:
            result.update(self._analyze_binary_classification(cm))
        else:
            result.update(self._analyze_multiclass_classification(cm))
        
        return result
    
    def _analyze_binary_classification(self, cm: np.ndarray) -> Dict[str, Any]:
        """
        Analyze binary classification confusion matrix
        
        Format:
        [[TN, FP],
         [FN, TP]]
        """
        tn, fp, fn, tp = cm.ravel()
        
        # Protection against division by zero
        epsilon = 1e-10
        
        # Calculate metrics
        accuracy = (tp + tn) / (tp + tn + fp + fn + epsilon)
        precision = tp / (tp + fp + epsilon)
        recall = tp / (tp + fn + epsilon)
        specificity = tn / (tn + fp + epsilon)
        f1 = 2 * (precision * recall) / (precision + recall + epsilon)
        
        # Calculate additional metrics
        false_positive_rate = fp / (fp + tn + epsilon)
        false_negative_rate = fn / (fn + tp + epsilon)
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'specificity': float(specificity),
            'f1_score': float(f1),
            'false_positive_rate': float(false_positive_rate),
            'false_negative_rate': float(false_negative_rate),
            'true_positive': int(tp),
            'true_negative': int(tn),
            'false_positive': int(fp),
            'false_negative': int(fn),
            'detailed_metrics': {
                'sensitivity': float(recall),
                'tnr': float(specificity),
                'fpr': float(false_positive_rate),
                'fnr': float(false_negative_rate)
            }
        }
    
    def _analyze_multiclass_classification(self, cm: np.ndarray) -> Dict[str, Any]:
        """
        Analyze multiclass classification confusion matrix
        """
        n_classes = cm.shape[0]
        
        # Calculate per-class metrics
        per_class_metrics = []
        
        for i in range(n_classes):
            tp = cm[i, i]
            fp = cm[:, i].sum() - tp
            fn = cm[i, :].sum() - tp
            tn = cm.sum() - tp - fp - fn
            
            epsilon = 1e-10
            
            precision = tp / (tp + fp + epsilon)
            recall = tp / (tp + fn + epsilon)
            f1 = 2 * (precision * recall) / (precision + recall + epsilon)
            
            per_class_metrics.append({
                'class': self.class_labels[i] if i < len(self.class_labels) else str(i),
                'true_positives': int(tp),
                'false_positives': int(fp),
                'false_negatives': int(fn),
                'true_negatives': int(tn),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1)
            })
        
        # Calculate macro and weighted averages
        precisions = [m['precision'] for m in per_class_metrics]
        recalls = [m['recall'] for m in per_class_metrics]
        f1_scores = [m['f1_score'] for m in per_class_metrics]
        
        macro_precision = np.mean(precisions)
        macro_recall = np.mean(recalls)
        macro_f1 = np.mean(f1_scores)
        
        # Calculate overall accuracy
        accuracy = np.trace(cm) / cm.sum()
        
        return {
            'accuracy': float(accuracy),
            'macro_precision': float(macro_precision),
            'macro_recall': float(macro_recall),
            'macro_f1': float(macro_f1),
            'per_class_metrics': per_class_metrics
        }
    
    def get_recommendations(self, cm_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on confusion matrix analysis
        
        Args:
            cm_analysis: Output from generate_matrix
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Binary classification analysis
        if 'false_positive_rate' in cm_analysis:
            accuracy = cm_analysis.get('accuracy', 0)
            precision = cm_analysis.get('precision', 0)
            recall = cm_analysis.get('recall', 0)
            fpr = cm_analysis.get('false_positive_rate', 0)
            fnr = cm_analysis.get('false_negative_rate', 0)
            
            if accuracy < 0.7:
                recommendations.append("Low accuracy detected. Consider collecting more data or engineering better features.")
            
            if recall < 0.6:
                recommendations.append("Low recall: Model misses many positive cases. Consider adjusting decision threshold or class weights.")
            
            if precision < 0.6:
                recommendations.append("Low precision: Many false positives. Might need more conservative prediction threshold.")
            
            if fpr > 0.3:
                recommendations.append("High false positive rate. Consider tuning model to be more conservative.")
            
            if fnr > 0.3:
                recommendations.append("High false negative rate. Model might need more complexity or better features.")
        
        # Multiclass analysis
        if 'per_class_metrics' in cm_analysis:
            per_class = cm_analysis['per_class_metrics']
            
            # Find problematic classes
            for metric in per_class:
                if metric['f1_score'] < 0.5:
                    recommendations.append(f"Class '{metric['class']}' has low F1-score ({metric['f1_score']:.2f}). "
                                          "This class might be underrepresented or difficult to predict.")
            
            accuracy = cm_analysis.get('accuracy', 0)
            if accuracy < 0.7:
                recommendations.append("Overall accuracy is low. Consider data augmentation or hyperparameter tuning.")
        
        # Ensure at least one recommendation
        if not recommendations:
            recommendations.append("Model performance is acceptable. Continue monitoring prediction quality on new data.")
        
        return recommendations
    
    def format_for_display(self, cm_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format confusion matrix analysis for UI display
        
        Args:
            cm_analysis: Output from generate_matrix
        
        Returns:
            Formatted dictionary for UI
        """
        result = {
            'confusion_matrix': cm_analysis.get('confusion_matrix', []),
            'class_labels': cm_analysis.get('class_labels', []),
            'metrics': {},
            'recommendations': self.get_recommendations(cm_analysis)
        }
        
        # Extract main metrics based on classification type
        if 'false_positive_rate' in cm_analysis:  # Binary
            result['metrics'] = {
                'accuracy': cm_analysis.get('accuracy', 0),
                'precision': cm_analysis.get('precision', 0),
                'recall': cm_analysis.get('recall', 0),
                'specificity': cm_analysis.get('specificity', 0),
                'f1_score': cm_analysis.get('f1_score', 0),
                'false_positive_rate': cm_analysis.get('false_positive_rate', 0),
                'false_negative_rate': cm_analysis.get('false_negative_rate', 0)
            }
        else:  # Multiclass
            result['metrics'] = {
                'accuracy': cm_analysis.get('accuracy', 0),
                'macro_precision': cm_analysis.get('macro_precision', 0),
                'macro_recall': cm_analysis.get('macro_recall', 0),
                'macro_f1': cm_analysis.get('macro_f1', 0)
            }
            result['per_class_metrics'] = cm_analysis.get('per_class_metrics', [])
        
        return result
