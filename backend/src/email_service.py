"""
Email Service Integration for Listmonk
Handles email campaign creation and subscriber management
"""

import os
import requests
import json
from datetime import datetime

class EmailService:
    def __init__(self):
        self.base_url = os.environ.get('LISTMONK_URL', 'http://localhost:9000')
        self.username = os.environ.get('LISTMONK_USERNAME', 'admin')
        self.password = os.environ.get('LISTMONK_PASSWORD', 'admin')
        self.auth = (self.username, self.password)
        
    def is_configured(self):
        """Check if Listmonk is configured and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/health", auth=self.auth, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_lists(self):
        """Get all subscriber lists"""
        try:
            response = requests.get(f"{self.base_url}/api/lists", auth=self.auth, timeout=10)
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching lists: {e}")
            return []
    
    def create_list(self, name, description="AI Newsletter Subscribers"):
        """Create a new subscriber list"""
        try:
            data = {
                'name': name,
                'type': 'public',
                'optin': 'single',
                'tags': ['ai-newsletter'],
                'description': description
            }
            
            response = requests.post(
                f"{self.base_url}/api/lists",
                json=data,
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                print(f"Error creating list: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating list: {e}")
            return None
    
    def add_subscriber(self, email, name="", lists=None):
        """Add a subscriber to Listmonk"""
        if lists is None:
            lists = [1]  # Default to first list
            
        try:
            data = {
                'email': email,
                'name': name,
                'status': 'enabled',
                'lists': lists,
                'preconfirm_subscriptions': True
            }
            
            response = requests.post(
                f"{self.base_url}/api/subscribers",
                json=data,
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                print(f"Error adding subscriber: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error adding subscriber: {e}")
            return None
    
    def create_campaign(self, subject, content, lists=None):
        """Create and send an email campaign"""
        if lists is None:
            lists = [1]  # Default to first list
            
        try:
            # Create campaign
            campaign_data = {
                'name': f"AI Newsletter - {datetime.now().strftime('%Y-%m-%d')}",
                'subject': subject,
                'lists': lists,
                'type': 'regular',
                'content_type': 'html',
                'body': content,
                'template_id': 1  # Default template
            }
            
            response = requests.post(
                f"{self.base_url}/api/campaigns",
                json=campaign_data,
                auth=self.auth,
                timeout=15
            )
            
            if response.status_code == 200:
                campaign = response.json().get('data', {})
                campaign_id = campaign.get('id')
                
                # Start the campaign
                if campaign_id:
                    start_response = requests.put(
                        f"{self.base_url}/api/campaigns/{campaign_id}/status",
                        json={'status': 'running'},
                        auth=self.auth,
                        timeout=10
                    )
                    
                    if start_response.status_code == 200:
                        return campaign
                    else:
                        print(f"Error starting campaign: {start_response.status_code}")
                        return campaign
                
                return campaign
            else:
                print(f"Error creating campaign: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating campaign: {e}")
            return None
    
    def sync_subscribers(self, subscribers):
        """Sync subscribers from local database to Listmonk"""
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        # Ensure default list exists
        lists = self.get_lists()
        if not lists:
            default_list = self.create_list("AI Newsletter Subscribers", "Main list for AI newsletter subscribers")
            if default_list:
                lists = [default_list]
        
        if not lists:
            return {'success': 0, 'failed': len(subscribers), 'errors': ['No lists available']}
        
        list_id = lists[0]['id']
        
        for subscriber in subscribers:
            email = subscriber['email']
            topics = subscriber.get('topics', [])
            
            # Create a name from topics for better organization
            name = f"Topics: {', '.join(topics[:2])}{'...' if len(topics) > 2 else ''}"
            
            result = self.add_subscriber(email, name, [list_id])
            if result:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to add {email}")
        
        return results
    
    def generate_html_content(self, newsletter_content):
        """Generate HTML email content from newsletter data"""
        subject = newsletter_content.get('subject', 'AI Newsletter')
        sections = newsletter_content.get('sections', [])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #ffffff; padding: 30px 20px; border: 1px solid #e0e0e0; }}
                .section {{ margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #f0f0f0; }}
                .section:last-child {{ border-bottom: none; }}
                .topic-title {{ color: #4a5568; font-size: 18px; font-weight: bold; margin-bottom: 15px; padding: 10px 0; border-left: 4px solid #667eea; padding-left: 15px; }}
                .topic-content {{ color: #2d3748; line-height: 1.8; }}
                .footer {{ background: #f7fafc; padding: 20px; text-align: center; color: #718096; font-size: 14px; border-radius: 0 0 8px 8px; }}
                .unsubscribe {{ color: #4299e1; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">🤖 AI Newsletter</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Your Weekly AI Updates</p>
            </div>
            
            <div class="content">
                <p>Hello! Here are your personalized AI updates for this week:</p>
        """
        
        for section in sections:
            topic = section.get('topic', 'AI Update')
            content = section.get('content', '')
            
            html += f"""
                <div class="section">
                    <h2 class="topic-title">{topic}</h2>
                    <div class="topic-content">{content}</div>
                </div>
            """
        
        html += f"""
            </div>
            
            <div class="footer">
                <p>Thank you for subscribing to our AI Newsletter!</p>
                <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
                <p><a href="{{{{ unsubscribe_url }}}}" class="unsubscribe">Unsubscribe</a> | <a href="#" class="unsubscribe">Update Preferences</a></p>
            </div>
        </body>
        </html>
        """
        
        return html