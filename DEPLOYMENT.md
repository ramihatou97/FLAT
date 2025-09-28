# Deployment Guide

## Quick Start (Development)

1. **Set Environment Variables**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

2. **Start with Docker Compose**
```bash
docker-compose up -d
```

3. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Production Deployment

1. **Set Production Environment Variables**
```bash
export OPENAI_API_KEY=your_openai_api_key
export SECRET_KEY=your_secret_key
export DB_USER=your_db_user
export DB_PASSWORD=your_secure_db_password
```

2. **Deploy with Production Configuration**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Manual Setup (Without Docker)

### Backend Setup

1. **Install Dependencies**
```bash
cd medical_platform_v3
pip install -r requirements.txt
```

2. **Set Environment Variables**
```bash
export DATABASE_URL=postgresql://user:password@localhost/medical_platform
export OPENAI_API_KEY=your_openai_api_key
```

3. **Initialize Database**
```bash
python init_db.py
```

4. **Start Backend**
```bash
python simple_main.py
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Start Development Server**
```bash
npm start
```

3. **Build for Production**
```bash
npm run build
```

## Database Management

### Initialize Database
```bash
python medical_platform_v3/init_db.py
```

### Backup Database
```bash
docker exec -t database pg_dump -U medical_user medical_platform > backup.sql
```

### Restore Database
```bash
docker exec -i database psql -U medical_user medical_platform < backup.sql
```

## Health Checks

- Backend Health: `GET /api/health/`
- System Status: `GET /api/health/status`
- Frontend: Access http://localhost:3000

## Environment Variables

### Required
- `OPENAI_API_KEY` - OpenAI API key for AI content generation

### Optional
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret key
- `DEBUG` - Enable debug mode (default: false)
- `ENVIRONMENT` - Environment name (development/production)

## Scaling

For production scaling:

1. **Use Production Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

2. **Add Load Balancer**
Configure nginx or a cloud load balancer to distribute traffic across backend instances.

3. **Database Optimization**
- Use connection pooling
- Set up read replicas for scaling reads
- Configure backup strategies

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify DATABASE_URL is correct
   - Ensure database exists

2. **AI Features Not Working**
   - Verify OPENAI_API_KEY is set
   - Check API key has sufficient credits
   - Review backend logs for API errors

3. **Frontend Can't Connect to Backend**
   - Verify backend is running on port 8000
   - Check CORS settings in backend
   - Ensure no firewall blocking connections

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs database
```

## Security Considerations

1. **Use Strong Passwords**
   - Set strong database passwords
   - Use secure secret keys

2. **SSL/HTTPS**
   - Configure SSL certificates for production
   - Use HTTPS for all traffic

3. **API Security**
   - Implement rate limiting
   - Use API authentication if needed
   - Keep API keys secure

4. **Database Security**
   - Limit database access
   - Regular security updates
   - Backup encryption