"""
Content Generation Service using Perplexity AI
Handles AI-powered content generation for newsletter topics
"""

import os
import requests
import json
from datetime import datetime, timedelta

class ContentGenerator:
    def __init__(self):
        self.api_key = os.environ.get('PERPLEXITY_API_KEY')
        self.base_url = 'https://api.perplexity.ai/chat/completions'
        
    def is_configured(self):
        """Check if Perplexity API key is configured"""
        return self.api_key is not None and self.api_key.strip() != ""
    
    def generate_content_for_topic(self, topic, max_words=200):
        """Generate content for a specific AI topic"""
        if not self.is_configured():
            return self._get_fallback_content(topic)
        
        # Create topic-specific prompt
        prompt = self._create_prompt(topic, max_words)
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.1-sonar-small-128k-online',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are an AI news curator specializing in providing concise, accurate updates on artificial intelligence developments. Focus on recent news from the past week.'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': 300,
                    'temperature': 0.2,
                    'top_p': 0.9
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return {
                    'content': content.strip(),
                    'source': 'perplexity_ai',
                    'generated_at': datetime.now().isoformat()
                }
            else:
                print(f"Perplexity API error: {response.status_code} - {response.text}")
                return self._get_fallback_content(topic)
                
        except Exception as e:
            print(f"Error generating content with Perplexity: {e}")
            return self._get_fallback_content(topic)
    
    def _create_prompt(self, topic, max_words):
        """Create a topic-specific prompt for content generation"""
        prompts = {
            "LLMs released this week": f"What are the most significant large language model releases, updates, or announcements from the past week? Include specific model names, capabilities, and companies involved. Keep response under {max_words} words.",
            
            "Coding tools and IDEs": f"What are the latest updates, new features, or releases in coding tools, IDEs, and developer environments from the past week? Include specific tool names and new capabilities. Keep response under {max_words} words.",
            
            "Agentic AI systems": f"What are the recent developments in autonomous AI agents and agentic AI systems from the past week? Include new frameworks, platforms, or significant implementations. Keep response under {max_words} words.",
            
            "AI tools for business workflows": f"What are the newest AI tools and platforms for business automation and productivity released or updated this week? Include specific tools and their business applications. Keep response under {max_words} words.",
            
            "AI tools for personal productivity": f"What are the latest AI-powered personal productivity tools, apps, and features released this week? Include specific tools and their capabilities. Keep response under {max_words} words.",
            
            "Computer vision and image AI": f"What are the recent developments in computer vision, image generation, and visual AI from the past week? Include new models, tools, or significant research. Keep response under {max_words} words.",
            
            "Natural language processing": f"What are the latest advancements in natural language processing, text analysis, and language AI from the past week? Include new techniques, tools, or applications. Keep response under {max_words} words.",
            
            "AI research papers": f"What are the most important AI research papers published or highlighted this week? Include paper titles, key findings, and institutions involved. Keep response under {max_words} words.",
            
            "AI startup news": f"What are the significant AI startup funding announcements, launches, or major developments from the past week? Include company names, funding amounts, and what they're building. Keep response under {max_words} words.",
            
            "AI ethics and regulation": f"What are the latest developments in AI ethics, governance, policy, and regulation from the past week? Include specific policies, guidelines, or regulatory actions. Keep response under {max_words} words."
        }
        
        return prompts.get(topic, f"Provide the latest news and updates about {topic} from the past week in under {max_words} words.")
    
    def _get_fallback_content(self, topic):
        """Provide fallback content when Perplexity API is not available"""
        fallback_content = {
            "LLMs released this week": "Stay tuned for the latest large language model releases. This week's updates will include new model announcements, capability improvements, and performance benchmarks from leading AI companies.",
            
            "Coding tools and IDEs": "Discover the newest coding tools and IDE features that are enhancing developer productivity. From AI-powered code completion to advanced debugging tools, we'll cover the latest innovations in development environments.",
            
            "Agentic AI systems": "Explore the cutting-edge world of autonomous AI agents and agentic systems. Learn about new frameworks, platforms, and implementations that are pushing the boundaries of AI autonomy.",
            
            "AI tools for business workflows": "Transform your business processes with the latest AI-powered automation tools. We'll highlight new platforms and solutions that are revolutionizing workplace productivity and efficiency.",
            
            "AI tools for personal productivity": "Boost your personal productivity with AI-powered assistants and tools. From smart scheduling to automated task management, discover the latest apps that can streamline your daily workflows.",
            
            "Computer vision and image AI": "Dive into the latest advancements in computer vision and image AI. From breakthrough models to practical applications, we'll cover the innovations shaping visual AI technology.",
            
            "Natural language processing": "Explore recent developments in natural language processing and text AI. Learn about new techniques, models, and applications that are advancing our understanding of human language.",
            
            "AI research papers": "Access summaries of the most impactful AI research papers. We'll break down complex findings from leading institutions and explain their potential real-world implications.",
            
            "AI startup news": "Get insights into the dynamic AI startup ecosystem. From funding announcements to product launches, stay informed about the companies building tomorrow's AI solutions.",
            
            "AI ethics and regulation": "Stay informed about AI governance, ethics, and policy developments. Learn about new regulations, guidelines, and frameworks shaping the responsible development of AI technology."
        }
        
        return {
            'content': fallback_content.get(topic, f"Latest updates on {topic} will be available soon. Subscribe to stay informed about the most important developments in this area."),
            'source': 'fallback',
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_newsletter_content(self, topics):
        """Generate complete newsletter content for multiple topics"""
        sections = []
        
        for topic in topics:
            content_data = self.generate_content_for_topic(topic)
            sections.append({
                'topic': topic,
                'content': content_data['content'],
                'source': content_data['source'],
                'generated_at': content_data['generated_at']
            })
        
        return {
            'subject': f'Weekly AI Newsletter - {datetime.now().strftime("%B %d, %Y")}',
            'generated_at': datetime.now().isoformat(),
            'sections': sections,
            'topics_count': len(topics)
        }