"""
Newsletter Scheduler - Handles automated newsletter generation and sending
"""

import schedule
import time
import threading
from datetime import datetime
import sqlite3
import json
import os

class NewsletterScheduler:
    def __init__(self, content_generator, email_service, database_path):
        self.content_generator = content_generator
        self.email_service = email_service
        self.database_path = database_path
        self.is_running = False
        self.scheduler_thread = None
        self.last_run = None
        self.next_run = None
        
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            return False, "Scheduler is already running"
        
        try:
            # Schedule weekly newsletter generation (every Monday at 9:00 AM)
            schedule.clear()
            schedule.every().monday.at("09:00").do(self._generate_and_send_newsletters)
            
            # Calculate next run time
            self._update_next_run()
            
            # Start scheduler in background thread
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            return True, "Scheduler started successfully"
        except Exception as e:
            return False, f"Failed to start scheduler: {str(e)}"
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return False, "Scheduler is not running"
        
        self.is_running = False
        schedule.clear()
        self.next_run = None
        
        return True, "Scheduler stopped successfully"
    
    def get_status(self):
        """Get scheduler status"""
        return {
            'running': self.is_running,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'scheduled_jobs': len(schedule.jobs)
        }
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
            if self.is_running:
                self._update_next_run()
    
    def _update_next_run(self):
        """Update the next run time"""
        if schedule.jobs:
            self.next_run = min(job.next_run for job in schedule.jobs)
        else:
            self.next_run = None
    
    def _generate_and_send_newsletters(self):
        """Generate and send newsletters to all subscribers"""
        try:
            print(f"Starting automated newsletter generation at {datetime.now()}")
            self.last_run = datetime.now()
            
            # Get all active subscribers
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT email, topics FROM subscribers WHERE active = 1')
            subscribers = cursor.fetchall()
            
            if not subscribers:
                print("No active subscribers found")
                conn.close()
                return
            
            # Group subscribers by topic combinations to optimize content generation
            topic_groups = {}
            for email, topics_json in subscribers:
                topics_key = topics_json
                if topics_key not in topic_groups:
                    topic_groups[topics_key] = []
                topic_groups[topics_key].append(email)
            
            newsletters_generated = 0
            
            # Generate content for each unique topic combination
            for topics_json, emails in topic_groups.items():
                topics = json.loads(topics_json)
                content = self.content_generator.generate_newsletter_content(topics)
                
                # If email service is configured, send emails
                if self.email_service.is_configured():
                    html_content = self.email_service.generate_html_content(content)
                    
                    # In a real implementation, you would send individual emails
                    # or create targeted campaigns for each topic group
                    print(f"Would send newsletter to {len(emails)} subscribers with topics: {topics}")
                else:
                    print(f"Email service not configured - newsletter content generated for {len(emails)} subscribers")
                
                # Log the generated newsletter for each subscriber
                for email in emails:
                    cursor.execute(
                        'INSERT INTO newsletter_logs (subscriber_email, topics, content, success) VALUES (?, ?, ?, ?)',
                        (email, topics_json, json.dumps(content), True)
                    )
                    newsletters_generated += 1
            
            conn.commit()
            conn.close()
            
            print(f"Newsletter generation completed. Generated {newsletters_generated} newsletters for {len(topic_groups)} unique topic combinations.")
            
        except Exception as e:
            print(f"Error in automated newsletter generation: {e}")
    
    def manual_run(self):
        """Manually trigger newsletter generation"""
        try:
            self._generate_and_send_newsletters()
            return True, "Newsletter generation completed successfully"
        except Exception as e:
            return False, f"Failed to generate newsletters: {str(e)}"