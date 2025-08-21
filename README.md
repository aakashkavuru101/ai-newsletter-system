# AI Newsletter - Automated Weekly AI Updates

A modern, automated newsletter system that delivers curated AI news and updates to subscribers based on their interests.

## 🚀 Features

- **Topic Selection**: Choose up to 3 AI topics from 10 available categories
- **Automated Content Generation**: AI-powered content curation using Perplexity AI
- **Weekly Automation**: Scheduled newsletter delivery every Monday
- **Professional Email Delivery**: Powered by Listmonk email service
- **Responsive Design**: Beautiful, mobile-friendly subscription interface
- **Real-time Validation**: Email validation and topic selection feedback

## 📋 Available Topics

1. **LLMs released this week** - Latest language model announcements
2. **Coding tools and IDEs** - New developer tools and IDE features
3. **Agentic AI systems** - Autonomous AI agents and systems
4. **AI tools for business workflows** - Business automation and productivity
5. **AI tools for personal productivity** - Personal AI assistants and apps
6. **Computer vision and image AI** - Image processing and computer vision
7. **Natural language processing** - NLP tools and techniques
8. **AI research papers** - Latest academic research and papers
9. **AI startup news** - Funding, launches, and startup announcements
10. **AI ethics and regulation** - Policy, governance, and ethical considerations

## 🛠 Technology Stack

### Frontend
- **React** with Vite
- **Tailwind CSS** for styling
- **shadcn/ui** components
- **Lucide React** icons
- **Responsive design** for all devices

### Backend
- **Flask** REST API
- **SQLite** database
- **SQLAlchemy** ORM
- **Flask-CORS** for cross-origin requests

### Email Service
- **Listmonk** for professional email delivery
- **Docker** containerization
- **PostgreSQL** for Listmonk data

### AI Content Generation
- **Perplexity AI** for real-time content generation
- **Fallback content** system for reliability
- **Topic-specific** content curation

### Automation
- **Python Schedule** library
- **Weekly automation** (Mondays at 9 AM)
- **Manual trigger** capabilities
- **Status monitoring** and control

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (for email service)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-newsletter
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Start Listmonk (Email Service)**
   ```bash
   docker run -d --name listmonk_postgres -e POSTGRES_PASSWORD=listmonk -e POSTGRES_USER=listmonk -e POSTGRES_DB=listmonk postgres:17-alpine
   docker run -d --name listmonk_app -p 9000:9000 --link listmonk_postgres:db listmonk/listmonk:latest
   ```

5. **Configure environment variables**
   ```bash
   export PERPLEXITY_API_KEY="your-perplexity-api-key"
   export LISTMONK_URL="http://localhost:9000"
   export LISTMONK_USERNAME="admin"
   export LISTMONK_PASSWORD="your-password"
   ```

6. **Start the services**
   ```bash
   # Backend (Terminal 1)
   cd backend && python src/main.py
   
   # Frontend (Terminal 2)
   cd frontend && npm run dev
   ```

7. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000
   - Listmonk Admin: http://localhost:9000

## 📡 API Endpoints

### Subscription Management
- `GET /api/topics` - Get available topics
- `POST /api/subscribe` - Subscribe with email and topics
- `GET /api/subscribers` - List all subscribers

### Content Generation
- `GET /api/test-content` - Test content generation
- `POST /api/generate-newsletter` - Generate newsletter for subscriber
- `POST /api/generate-content` - Generate content for specific topics

### Automation Control
- `POST /api/start-scheduler` - Start weekly automation
- `POST /api/stop-scheduler` - Stop automation
- `GET /api/scheduler-status` - Check scheduler status
- `POST /api/generate-newsletters` - Manual newsletter generation

### Email Service
- `GET /api/email-service-status` - Check Listmonk connection
- `POST /api/sync-subscribers` - Sync subscribers to Listmonk

## 🔧 Configuration

### Perplexity AI Setup
1. Get API key from [Perplexity AI](https://www.perplexity.ai/)
2. Set environment variable: `PERPLEXITY_API_KEY=your-key`
3. The system uses the cost-effective "sonar" model by default

### Listmonk Setup
1. Access admin panel at http://localhost:9000
2. Create admin account during first setup
3. Configure SMTP settings for email delivery
4. Create subscriber lists and campaigns

### Deployment
The frontend is deployed to GitHub Pages, while the backend can be deployed to any cloud service that supports Flask applications.

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Flask Backend │    │   Listmonk      │
│   (GitHub Pages) │◄──►│   (Cloud Host)  │◄──►│   (Email Service)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Perplexity AI │
                       │   (Content Gen) │
                       └─────────────────┘
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Perplexity AI](https://www.perplexity.ai/) for content generation
- [Listmonk](https://listmonk.app/) for email service
- [shadcn/ui](https://ui.shadcn.com/) for UI components
- [Tailwind CSS](https://tailwindcss.com/) for styling

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for the AI community**

