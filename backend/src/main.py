"""
AI Newsletter Backend - Main Flask Application
Provides REST API for newsletter subscription and content generation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import re
from datetime import datetime
import json
from content_generator import ContentGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connection

# Configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'newsletter.db')
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
LISTMONK_URL = os.environ.get('LISTMONK_URL', 'http://localhost:9000')
LISTMONK_USERNAME = os.environ.get('LISTMONK_USERNAME', 'admin')
LISTMONK_PASSWORD = os.environ.get('LISTMONK_PASSWORD', 'admin')

# Initialize content generator
content_generator = ContentGenerator()

# Available AI newsletter topics
AVAILABLE_TOPICS = [
    "LLMs released this week",
    "Coding tools and IDEs", 
    "Agentic AI systems",
    "AI tools for business workflows",
    "AI tools for personal productivity",
    "Computer vision and image AI",
    "Natural language processing",
    "AI research papers",
    "AI startup news",
    "AI ethics and regulation"
]

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create subscribers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            topics TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create newsletter_logs table for tracking sent newsletters
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newsletter_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscriber_email TEXT NOT NULL,
            topics TEXT NOT NULL,
            content TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_topics(topics):
    """Validate topic selection"""
    if not isinstance(topics, list):
        return False, "Topics must be a list"
    
    if len(topics) == 0:
        return False, "Please select at least one topic"
    
    if len(topics) > 3:
        return False, "You can select maximum 3 topics"
    
    for topic in topics:
        if topic not in AVAILABLE_TOPICS:
            return False, f"Invalid topic: {topic}"
    
    return True, None

@app.route('/api/topics', methods=['GET'])
def get_topics():
    """Get available newsletter topics"""
    return jsonify({
        'success': True,
        'topics': AVAILABLE_TOPICS
    })

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Subscribe to newsletter with email and topic preferences"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
        
        email = data.get('email', '').strip().lower()
        topics = data.get('topics', [])
        
        # Validate email
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        if not validate_email(email):
            return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
        
        # Validate topics
        valid, error = validate_topics(topics)
        if not valid:
            return jsonify({'success': False, 'error': error}), 400
        
        # Save to database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            # Check if email already exists
            cursor.execute('SELECT id, topics FROM subscribers WHERE email = ?', (email,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing subscription
                cursor.execute(
                    'UPDATE subscribers SET topics = ?, created_at = CURRENT_TIMESTAMP, active = 1 WHERE email = ?',
                    (json.dumps(topics), email)
                )
                message = 'Subscription updated successfully'
            else:
                # Create new subscription
                cursor.execute(
                    'INSERT INTO subscribers (email, topics) VALUES (?, ?)',
                    (email, json.dumps(topics))
                )
                message = 'Successfully subscribed to AI newsletter'
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': message,
                'email': email,
                'topics': topics
            })
            
        except sqlite3.Error as e:
            conn.rollback()
            return jsonify({'success': False, 'error': 'Database error occurred'}), 500
        
        finally:
            conn.close()
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server error occurred'}), 500

@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """Get all subscribers (admin endpoint)"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT email, topics, created_at, active FROM subscribers ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        subscribers = []
        for row in rows:
            subscribers.append({
                'email': row[0],
                'topics': json.loads(row[1]),
                'created_at': row[2],
                'active': bool(row[3])
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'subscribers': subscribers,
            'total': len(subscribers)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to retrieve subscribers'}), 500

@app.route('/api/test-content', methods=['GET'])
def test_content():
    """Test content generation endpoint"""
    test_topics = ['LLMs released this week', 'Coding tools and IDEs']
    content = content_generator.generate_newsletter_content(test_topics)
    
    return jsonify({
        'success': True,
        'content': content,
        'api_configured': content_generator.is_configured()
    })

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    """Generate content for specific topics"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
        
        topics = data.get('topics', [])
        
        # Validate topics
        valid, error = validate_topics(topics)
        if not valid:
            return jsonify({'success': False, 'error': error}), 400
        
        content = content_generator.generate_newsletter_content(topics)
        
        return jsonify({
            'success': True,
            'content': content,
            'api_configured': content_generator.is_configured()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to generate content'}), 500

@app.route('/api/generate-newsletter', methods=['POST'])
def generate_newsletter():
    """Generate newsletter for specific subscriber"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Get subscriber's topics from database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT topics FROM subscribers WHERE email = ? AND active = 1', (email,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'error': 'Subscriber not found'}), 404
        
        topics = json.loads(result[0])
        conn.close()
        
        # Generate content for subscriber's topics
        content = content_generator.generate_newsletter_content(topics)
        
        return jsonify({
            'success': True,
            'email': email,
            'content': content,
            'api_configured': content_generator.is_configured()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to generate newsletter'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if os.path.exists(DATABASE_PATH) else 'not_initialized',
        'perplexity_api': 'configured' if content_generator.is_configured() else 'not_configured'
    })

@app.route('/api/scheduler-status', methods=['GET'])
def scheduler_status():
    """Check scheduler status"""
    return jsonify({
        'success': True,
        'scheduler_running': False,  # Will implement actual scheduler later
        'next_run': None,
        'last_run': None
    })

@app.route('/api/start-scheduler', methods=['POST'])
def start_scheduler():
    """Start weekly scheduler (placeholder)"""
    return jsonify({
        'success': True,
        'message': 'Scheduler start requested (implementation pending)',
        'scheduler_running': False
    })

@app.route('/api/stop-scheduler', methods=['POST'])
def stop_scheduler():
    """Stop scheduler (placeholder)"""
    return jsonify({
        'success': True,
        'message': 'Scheduler stop requested (implementation pending)',
        'scheduler_running': False
    })

@app.route('/api/generate-newsletters', methods=['POST'])
def generate_newsletters():
    """Generate newsletters for all active subscribers"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get all active subscribers grouped by topics to optimize API calls
        cursor.execute('SELECT email, topics FROM subscribers WHERE active = 1')
        subscribers = cursor.fetchall()
        
        if not subscribers:
            return jsonify({
                'success': True,
                'message': 'No active subscribers found',
                'newsletters_generated': 0
            })
        
        # Group subscribers by topic combinations to minimize content generation
        topic_groups = {}
        for email, topics_json in subscribers:
            topics_key = topics_json  # Use JSON string as key
            if topics_key not in topic_groups:
                topic_groups[topics_key] = []
            topic_groups[topics_key].append(email)
        
        generated_count = 0
        
        # Generate content for each unique topic combination
        for topics_json, emails in topic_groups.items():
            topics = json.loads(topics_json)
            content = content_generator.generate_newsletter_content(topics)
            
            # Log the generated newsletter for each subscriber
            for email in emails:
                cursor.execute(
                    'INSERT INTO newsletter_logs (subscriber_email, topics, content, success) VALUES (?, ?, ?, ?)',
                    (email, topics_json, json.dumps(content), True)
                )
                generated_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Generated newsletters for {generated_count} subscribers',
            'newsletters_generated': generated_count,
            'unique_content_generated': len(topic_groups)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to generate newsletters'}), 500

@app.route('/api/email-service-status', methods=['GET'])
def email_service_status():
    """Check email service status (placeholder for Listmonk integration)"""
    return jsonify({
        'success': True,
        'email_service': 'listmonk',
        'status': 'not_configured',
        'url': LISTMONK_URL,
        'message': 'Listmonk integration pending'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting AI Newsletter Backend on port {port}")
    print(f"Database path: {DATABASE_PATH}")
    print(f"CORS enabled for frontend connections")
    
    app.run(host='0.0.0.0', port=port, debug=True)