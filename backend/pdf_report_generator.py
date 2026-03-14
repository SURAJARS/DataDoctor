"""
PDF Report Generator
Generates professional PDF reports from analysis results
"""

import io
from typing import Dict, Any
from datetime import datetime
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class PDFReportGenerator:
    """Generates professional PDF reports"""
    
    def __init__(self):
        """Initialize PDF generator"""
        if not HAS_REPORTLAB:
            raise ImportError("reportlab not installed. Run: pip install reportlab")
    
    def generate_report(self, analysis_data: Dict[str, Any], filename: str = None) -> bytes:
        """
        Generate PDF report from analysis data
        
        Args:
            analysis_data: Complete analysis report dict
            filename: Output filename (if None, returns bytes)
        
        Returns:
            PDF bytes or saves to file
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, title="DATA DOCTOR Report")
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        story = []
        
        # Title
        story.append(Paragraph("DATA DOCTOR", title_style))
        story.append(Paragraph("Dataset Quality Analysis Report", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Metadata
        if 'timestamp' in analysis_data:
            story.append(Paragraph(f"<b>Report Generated:</b> {analysis_data['timestamp']}", styles['Normal']))
        if 'analysis_id' in analysis_data:
            story.append(Paragraph(f"<b>Analysis ID:</b> {analysis_data['analysis_id']}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Dataset Info
        if 'dataset_info' in analysis_data:
            story.append(Paragraph("Dataset Information", heading_style))
            dataset_data = analysis_data['dataset_info']
            dataset_table = [
                ['Rows', 'Columns', 'File Size (MB)', 'File Type'],
                [
                    str(dataset_data.get('rows', 'N/A')),
                    str(dataset_data.get('columns', 'N/A')),
                    str(dataset_data.get('file_size_mb', 'N/A')),
                    str(dataset_data.get('file_type', 'N/A'))
                ]
            ]
            dataset_table_obj = Table(dataset_table, colWidths=[1.5*inch]*4)
            dataset_table_obj.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(dataset_table_obj)
            story.append(Spacer(1, 0.3*inch))
        
        # Health Score Section
        if 'health_score' in analysis_data:
            story.append(Paragraph("Dataset Health Score", heading_style))
            health = analysis_data['health_score']
            score = health.get('dataset_health_score', 'N/A')
            status = health.get('overall_status', 'Unknown')
            
            score_para = Paragraph(
                f"<font size=18><b>{score}/100</b></font> - <b>{status}</b>",
                styles['Normal']
            )
            story.append(score_para)
            story.append(Spacer(1, 0.2*inch))
        
        # ML Readiness Section
        if 'ml_readiness' in analysis_data:
            story.append(Paragraph("ML Readiness Assessment", heading_style))
            ml = analysis_data['ml_readiness']
            ml_score = ml.get('ml_readiness_score', 'N/A')
            ml_status = ml.get('readiness_status', 'Unknown')
            
            ml_para = Paragraph(
                f"<font size=14>Score: <b>{ml_score}/100</b> - Status: <b>{ml_status}</b></font>",
                styles['Normal']
            )
            story.append(ml_para)
            story.append(Spacer(1, 0.2*inch))
        
        # Critical Issues
        if 'health_score' in analysis_data:
            issues = analysis_data['health_score'].get('critical_issues', [])
            if issues:
                story.append(Paragraph("Critical Issues", heading_style))
                for issue in issues[:5]:  # First 5 issues
                    issue_text = f"• {issue.get('description', 'Issue')}"
                    story.append(Paragraph(issue_text, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Warnings
        if 'health_score' in analysis_data:
            warnings_list = analysis_data['health_score'].get('warnings', [])
            if warnings_list:
                story.append(Paragraph("Warnings & Observations", heading_style))
                for warning in warnings_list[:10]:  # First 10 warnings
                    warning_text = f"• {warning.get('description', 'Warning')}"
                    story.append(Paragraph(warning_text, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Feature Importance
        if 'feature_importance' in analysis_data:
            fi = analysis_data['feature_importance']
            if 'top_features' in fi:
                story.append(PageBreak())
                story.append(Paragraph("Feature Importance Analysis", heading_style))
                story.append(Spacer(1, 0.2*inch))
                
                features = fi['top_features'][:15]  # Top 15 features
                fi_table = [['Rank', 'Feature Name', 'Importance Score', 'Contribution']]
                for idx, feat in enumerate(features, 1):
                    importance = feat.get('importance', 0)
                    contrib = f"{importance * 100:.1f}%"
                    fi_table.append([
                        str(idx),
                        str(feat.get('feature', 'N/A'))[:25],  # Truncate long names
                        f"{importance:.4f}",
                        contrib
                    ])
                
                fi_table_obj = Table(fi_table, colWidths=[0.6*inch, 2*inch, 1.2*inch, 1*inch])
                fi_table_obj.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
                ]))
                story.append(fi_table_obj)
                story.append(Spacer(1, 0.3*inch))
                
                # Feature importance interpretation
                story.append(Paragraph(
                    "<b>Interpretation:</b> Features listed above are ranked by their importance in the dataset. "
                    "Higher scores indicate more predictive power for machine learning models.",
                    styles['Normal']
                ))
                story.append(Spacer(1, 0.3*inch))
        
        # Detailed Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Recommendations & Action Items", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Main recommendation from health score
        if 'health_score' in analysis_data:
            recommendation = analysis_data['health_score'].get('recommendation', '')
            if recommendation:
                story.append(Paragraph("<b>Primary Recommendation:</b>", styles['Normal']))
                story.append(Paragraph(recommendation, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Cleaning steps/recommendations
        if 'cleaning_recommendations' in analysis_data:
            steps = analysis_data['cleaning_recommendations'].get('cleaning_steps', [])
            if steps:
                story.append(Paragraph("<b>Data Cleaning Steps:</b>", styles['Normal']))
                for idx, step in enumerate(steps[:10], 1):
                    action = step.get('action', 'No action')
                    reason = step.get('reason', '')
                    priority = step.get('priority', 'Medium')
                    
                    step_text = f"<b>{idx}. {action}</b> [{priority}]"
                    story.append(Paragraph(step_text, styles['Normal']))
                    if reason:
                        story.append(Paragraph(f"   Reason: {reason}", styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                story.append(Spacer(1, 0.2*inch))
        
        # ML Readiness Recommendations
        if 'ml_readiness' in analysis_data:
            ml = analysis_data['ml_readiness']
            if 'recommendations' in ml:
                recs = ml['recommendations']
                if recs:
                    story.append(Paragraph("<b>ML Readiness Recommendations:</b>", styles['Normal']))
                    for idx, rec in enumerate(recs[:8], 1):
                        story.append(Paragraph(f"• {rec}", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))
        
        # Critical Blockers
        if 'ml_readiness' in analysis_data:
            blockers = analysis_data['ml_readiness'].get('critical_blockers', [])
            if blockers:
                story.append(Paragraph("<b>Critical Issues to Address:</b>", styles['Normal']))
                for blocker in blockers[:5]:
                    desc = blocker.get('description', 'Issue')
                    story.append(Paragraph(f"⚠️ {desc}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = "Generated by DATA DOCTOR — Dataset Quality Inspector"
        story.append(Paragraph(f"<i>{footer_text}</i>", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        
        # Save to file if filename provided
        if filename:
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    @staticmethod
    def get_default_filename() -> str:
        """Get default PDF filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"DataDoctor_Report_{timestamp}.pdf"
