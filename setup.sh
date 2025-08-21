#!/bin/bash

# AI Newsletter System Development Setup Script

echo "🚀 Setting up AI Newsletter System for development..."

# Check if we're in the correct directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

cd ..

# Create environment variables file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file template..."
    cat > .env << EOL
# AI Newsletter System Environment Configuration

# Perplexity AI API Configuration
PERPLEXITY_API_KEY=your-perplexity-api-key-here

# Listmonk Email Service Configuration
LISTMONK_URL=http://localhost:9000
LISTMONK_USERNAME=admin
LISTMONK_PASSWORD=your-secure-password

# Backend Configuration
PORT=5000
FLASK_ENV=development
EOL
    echo "✅ Created .env file. Please update with your API keys."
else
    echo "📝 .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Start the backend: cd backend && source venv/bin/activate && python src/main.py"
echo "3. Start the frontend: cd frontend && python -m http.server 8080"
echo "4. Visit http://localhost:8080/index-dev.html to test the application"
echo ""
echo "📚 API Documentation:"
echo "- Health check: http://localhost:5000/api/health"
echo "- Topics: http://localhost:5000/api/topics"
echo "- Test content: http://localhost:5000/api/test-content"
echo ""
echo "🔧 Optional: Set up Listmonk for email functionality:"
echo "docker run -d --name listmonk_postgres -e POSTGRES_PASSWORD=listmonk -e POSTGRES_USER=listmonk -e POSTGRES_DB=listmonk postgres:17-alpine"
echo "docker run -d --name listmonk_app -p 9000:9000 --link listmonk_postgres:db listmonk/listmonk:latest"