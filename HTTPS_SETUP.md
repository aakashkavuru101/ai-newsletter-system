# HTTPS Setup Guide

## Development vs Production

### Development (Current Setup)
- Backend runs on HTTP (port 5000)
- Frontend proxy correctly configured for HTTP in `frontend/vite.config.js`
- No SSL certificates needed
- Works perfectly for local development

### Production HTTPS Setup

#### Option 1: Flask with SSL Certificates
Set environment variables for SSL:
```bash
export SSL_CERT_PATH=/path/to/your/certificate.pem
export SSL_KEY_PATH=/path/to/your/private-key.pem
```

The backend will automatically use HTTPS when these are set.

#### Option 2: Reverse Proxy (Recommended)
Use a production web server like Nginx or Apache:

**Nginx Configuration Example:**
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.pem;
    ssl_certificate_key /path/to/private-key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Option 3: Cloud Platform SSL
Most cloud platforms (Heroku, Railway, DigitalOcean, etc.) provide automatic SSL:
- Deploy your Flask app normally (HTTP)
- Enable SSL/HTTPS at the platform level
- Platform handles SSL termination and forwards to your app

## Getting SSL Certificates

### Free Options:
- **Let's Encrypt**: Free automated certificates
- **Cloudflare**: Free SSL proxy service
- **Cloud Platform SSL**: Most platforms include free SSL

### Paid Options:
- Traditional SSL certificate providers
- Extended validation certificates for business use

## Frontend Configuration

Update frontend API calls in production to use HTTPS:
```javascript
// Development
const API_BASE = 'http://localhost:5000';

// Production
const API_BASE = 'https://yourdomain.com';
```

## Troubleshooting

### "Bad Request Version" Errors
This happens when:
1. Frontend tries HTTPS but backend only supports HTTP
2. Mixed HTTP/HTTPS content

**Solution:** Ensure both frontend and backend use the same protocol (HTTP in dev, HTTPS in production)

### CORS Issues with HTTPS
Ensure CORS allows your production domain:
```python
from flask_cors import CORS
CORS(app, origins=['https://yourdomain.com'])
```

## Security Best Practices

1. **Use HTTPS in production** - Never send sensitive data over HTTP
2. **Secure headers** - Add security headers for production
3. **Certificate management** - Keep certificates updated
4. **Environment variables** - Never commit SSL keys to version control