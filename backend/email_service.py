"""
Email Service Module
Sends analysis reports via email with PDF attachment
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import os
from typing import Dict, Any, Optional
from datetime import datetime


class EmailService:
    """Send reports via email"""
    
    def __init__(self, 
                 smtp_server: str = None,
                 smtp_port: int = 587,
                 sender_email: str = None,
                 sender_password: str = None):
        """
        Initialize email service
        
        Args:
            smtp_server: SMTP server (default: gmail)
            smtp_port: SMTP port (default: 587 for TLS)
            sender_email: Sender email address
            sender_password: Sender email password
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port
        self.sender_email = sender_email or os.getenv('SENDER_EMAIL')
        self.sender_password = sender_password or os.getenv('SENDER_PASSWORD')
    
    def send_report(self,
                   recipient_email: str,
                   subject: str,
                   body: str,
                   attachments: list = None) -> Dict[str, Any]:
        """
        Send report via email with multiple attachments
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            body: Email body text
            attachments: List of tuples (file_bytes, filename)
                e.g., [(pdf_bytes, 'report.pdf'), (csv_bytes, 'data.csv')]
        
        Returns:
            Status dictionary
        """
        try:
            # Validate email
            if not self._is_valid_email(recipient_email):
                return {
                    'status': 'error',
                    'message': 'Invalid email address'
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject
            
            # Add text content
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if provided
            if attachments:
                for file_bytes, filename in attachments:
                    if file_bytes:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file_bytes)
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment',
                                      filename=filename)
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            return {
                'status': 'success',
                'message': f'Report sent successfully to {recipient_email}',
                'timestamp': datetime.now().isoformat()
            }
        
        except smtplib.SMTPAuthenticationError:
            return {
                'status': 'error',
                'message': 'Email authentication failed. Check sender email/password.'
            }
        except smtplib.SMTPException as e:
            return {
                'status': 'error',
                'message': f'Email sending failed: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }
    
    def send_analysis_report(self,
                            recipient_email: str,
                            analysis_data: Dict[str, Any],
                            pdf_bytes: bytes = None,
                            csv_bytes: bytes = None) -> Dict[str, Any]:
        """
        Send analysis report with formatted content and attachments
        
        Args:
            recipient_email: Recipient email
            analysis_data: Analysis results dictionary
            pdf_bytes: PDF report bytes
            csv_bytes: Cleaned dataset CSV bytes
        
        Returns:
            Send status
        """
        # Generate email content
        subject = f"DATA DOCTOR Analysis Report - {analysis_data.get('analysis_id', 'Report')}"
        
        # Create email body
        health_score = analysis_data.get('health_score', {})
        ml_readiness = analysis_data.get('ml_readiness', {})
        dataset_info = analysis_data.get('dataset_info', {})
        
        body = f"""
Dear User,

Your DATA DOCTOR analysis report is ready!

=== DATASET INFORMATION ===
Rows: {dataset_info.get('rows', 'N/A')}
Columns: {dataset_info.get('columns', 'N/A')}
File Size: {dataset_info.get('file_size_mb', 'N/A')} MB
File Type: {dataset_info.get('file_type', 'N/A')}

=== HEALTH SCORE ===
Overall Score: {health_score.get('dataset_health_score', 'N/A')}/100
Status: {health_score.get('overall_status', 'Unknown')}
Critical Issues: {len(health_score.get('critical_issues', []))}
Warnings: {len(health_score.get('warnings', []))}

=== ML READINESS ===
Readiness Score: {ml_readiness.get('ml_readiness_score', 'N/A')}/100
Status: {ml_readiness.get('readiness_status', 'Unknown')}

=== ATTACHMENTS ===
✓ Detailed Analysis Report (PDF)
✓ Cleaned & Auto-Fixed Dataset (CSV)

=== NEXT STEPS ===
1. Review the attached PDF report for detailed analysis
2. Download the cleaned dataset for immediate use
3. Check the recommendations section for improvements
4. Apply suggested fixes to improve dataset quality
5. Re-run analysis after making changes

Thank you for using DATA DOCTOR!

Best regards,
DATA DOCTOR Team
Dataset Quality Inspector
        """
        
        # Prepare attachments list
        attachments = []
        if pdf_bytes:
            attachments.append((pdf_bytes, 'DataDoctor_Analysis_Report.pdf'))
        if csv_bytes:
            analysis_id = analysis_data.get('analysis_id', 'dataset')
            attachments.append((csv_bytes, f'cleaned_dataset_{analysis_id}.csv'))
        
        return self.send_report(
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            attachments=attachments if attachments else None
        )
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Simple email validation"""
        return '@' in email and '.' in email.split('@')[1]
    
    @staticmethod
    def get_test_credentials() -> Dict[str, str]:
        """Get test credentials template"""
        return {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'your_email@gmail.com',
            'sender_password': 'your_app_password'  # Gmail App Password
        }
