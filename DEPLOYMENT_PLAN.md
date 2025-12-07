# TasteBuds Yelp Companion - Production Deployment Plan

## Overview
This document outlines the complete deployment strategy for TasteBuds Yelp Companion, including all infrastructure components, services, and configurations.

---

## Architecture Overview

```
┌─────────────────┐
│   Netlify       │ ← Frontend (Next.js 16)
│   (Frontend)    │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────┐
│   Render        │ ← Backend API (FastAPI)
│   (Web Service) │
└────────┬────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌─────────┐   ┌──────────┐
    │Postgres│    │ Redis  │    │Pinecone │   │Yelp API  │
    │(Render)│    │(Render)│    │(Cloud)  │   │(External)│
    └────────┘    └────────┘    └─────────┘   └──────────┘
```

---

## Component Breakdown

### 1. Frontend - Netlify Deployment

**Platform:** Netlify
**Framework:** Next.js 16.0.7
**Build Tool:** Turbopack
**Node Version:** 18.x or higher

#### Configuration Files Needed:

**`netlify.toml`**
```toml
[build]
  command = "npm run build"
  publish = ".next"

[build.environment]
  NODE_VERSION = "18"
  NPM_VERSION = "10"

[[redirects]]
  from = "/api/*"
  to = "https://tastebuds-api.onrender.com/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### Environment Variables (Netlify):
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=https://tastebuds-api.onrender.com

# Analytics (optional)
NEXT_PUBLIC_VERCEL_ANALYTICS_ID=your_analytics_id
```

#### Build Settings:
- **Build command:** `npm run build`
- **Publish directory:** `.next`
- **Node version:** 18.x
- **Install command:** `npm install`

#### Pre-Deployment Checklist:
- [ ] Update `package.json` name field to "tastebuds-yelp-companion"
- [ ] Verify all dependencies are in package.json
- [ ] Test production build locally: `npm run build && npm start`
- [ ] Ensure environment variables are set
- [ ] Configure custom domain (if applicable)
- [ ] Enable HTTPS
- [ ] Set up automatic deployments from main branch

---

### 2. Backend API - Render Web Service

**Platform:** Render (Web Service)
**Framework:** FastAPI
**Python Version:** 3.11+
**WSGI Server:** Uvicorn

#### Configuration Files Needed:

**`render.yaml`** (root directory)
```yaml
services:
  - type: web
    name: tastebuds-api
    env: python
    region: oregon
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: tastebuds-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: tastebuds-redis
          type: redis
          property: connectionString
      - key: YELP_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: PINECONE_API_KEY
        sync: false
      - key: PINECONE_ENVIRONMENT
        sync: false
      - key: PINECONE_INDEX_NAME
        value: tastesync-embeddings
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: JWT_ALGORITHM
        value: HS256
      - key: JWT_EXPIRATION_HOURS
        value: 24
      - key: APP_ENV
        value: production
      - key: DEBUG
        value: false
      - key: CORS_ORIGINS
        value: '["https://tastebuds.netlify.app","https://www.tastebuds.com"]'
    healthCheckPath: /health
```

#### Environment Variables (Render Web Service):
```bash
# Database (Auto-configured from Render PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (Auto-configured from Render Redis)
REDIS_URL=redis://red-xxxxx:6379

# External APIs
YELP_API_KEY=your_yelp_api_key
OPENAI_API_KEY=your_openai_api_key

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=tastesync-embeddings

# JWT Auth (Generate secure key)
JWT_SECRET_KEY=your_production_jwt_secret_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# App Config
APP_ENV=production
DEBUG=false
CORS_ORIGINS=["https://tastebuds.netlify.app","https://www.tastebuds.com"]
```

#### Pre-Deployment Checklist:
- [ ] Update CORS origins to include production frontend URL
- [ ] Generate strong JWT secret key (min 32 chars)
- [ ] Verify all environment variables are set
- [ ] Test API health endpoint
- [ ] Set up health check: `/health`
- [ ] Configure auto-deploy from main branch
- [ ] Set instance type (Starter or higher)
- [ ] Enable persistent disk if needed

---

### 3. Database - Render PostgreSQL

**Platform:** Render (PostgreSQL Database)
**Version:** PostgreSQL 15+
**Name:** `tastebuds-db`

#### Database Configuration:
```yaml
databases:
  - name: tastebuds-db
    databaseName: tastesync
    user: tastesync_user
    region: oregon
    plan: starter  # or higher for production
    ipAllowList: []  # Empty for all Render services access
```

#### Database Setup Steps:
1. **Create Database Instance:**
   - Name: `tastebuds-db`
   - Database Name: `tastesync`
   - User: `tastesync_user`
   - Region: Oregon (same as web service)
   - Plan: Starter ($7/month) or higher

2. **Initialize Schema:**
   ```bash
   # Run migrations after deployment
   cd backend
   alembic upgrade head
   ```

3. **Import Initial Data (Optional):**
   ```bash
   python migrate_to_prod.py --import-data --prod-url $DATABASE_URL
   ```

#### Connection Details:
- Internal URL: Auto-provided by Render
- External URL: Available for remote connections
- SSL Mode: Required (verify-full recommended)

#### Pre-Deployment Checklist:
- [ ] Create database instance on Render
- [ ] Note down connection string
- [ ] Configure IP allowlist (or leave empty for Render-only access)
- [ ] Enable automated backups
- [ ] Set up point-in-time recovery (if available)
- [ ] Plan database migration strategy
- [ ] Test connection from local environment

---

### 4. Cache - Render Redis

**Platform:** Render (Redis Instance)
**Version:** Redis 7.x
**Name:** `tastebuds-redis`

#### Redis Configuration:
```yaml
services:
  - type: redis
    name: tastebuds-redis
    region: oregon
    plan: starter  # $7/month
    maxmemoryPolicy: allkeys-lru
    ipAllowList: []
```

#### Redis Usage:
- Taste Twin matching cache
- Leaderboard data (sorted sets)
- Session storage
- API rate limiting
- Restaurant search cache

#### Configuration:
```bash
# Maxmemory policy
maxmemory-policy allkeys-lru

# Persistence (if needed)
save 900 1
save 300 10
save 60 10000

# Disable write blocking on save errors (for development)
stop-writes-on-bgsave-error no
```

#### Pre-Deployment Checklist:
- [ ] Create Redis instance on Render
- [ ] Note down connection string
- [ ] Configure maxmemory policy
- [ ] Set up persistence settings
- [ ] Test connection from backend
- [ ] Configure eviction policy

---

### 5. Vector Database - Pinecone

**Platform:** Pinecone Cloud
**Index Name:** `tastesync-embeddings`
**Dimension:** 1536 (OpenAI ada-002)
**Metric:** Cosine similarity

#### Pinecone Setup:
1. **Create Index:**
   ```python
   import pinecone

   pinecone.init(
       api_key="your_pinecone_api_key",
       environment="gcp-starter"
   )

   pinecone.create_index(
       name="tastesync-embeddings",
       dimension=1536,
       metric="cosine",
       pods=1,
       pod_type="starter"
   )
   ```

2. **Index Configuration:**
   - Name: `tastesync-embeddings`
   - Dimension: 1536
   - Metric: cosine
   - Pod Type: s1.x1 (starter)
   - Replicas: 1

#### Pre-Deployment Checklist:
- [ ] Create Pinecone account
- [ ] Create index with correct dimensions
- [ ] Note API key and environment
- [ ] Test vector upsert/query operations
- [ ] Set up monitoring
- [ ] Configure metadata filtering

---

## External Services & APIs

### 1. Yelp Fusion API
- **Purpose:** Restaurant data, reviews, photos
- **Documentation:** https://www.yelp.com/developers
- **Rate Limits:** 5000 calls/day (free tier)
- **Required:** API Key

**Pre-Deployment:**
- [ ] Obtain Yelp API key
- [ ] Test API endpoints
- [ ] Implement rate limiting
- [ ] Set up error handling for API failures

### 2. OpenAI API
- **Purpose:** TasteDNA embeddings, recommendations
- **Model:** text-embedding-ada-002
- **Rate Limits:** Varies by plan
- **Required:** API Key

**Pre-Deployment:**
- [ ] Obtain OpenAI API key
- [ ] Set up billing
- [ ] Implement token usage tracking
- [ ] Configure embedding model

---

## Deployment Steps (Chronological Order)

### Phase 1: Infrastructure Setup (Day 1)

#### 1.1 Render - Database Setup
```bash
# 1. Create PostgreSQL database on Render
# - Name: tastebuds-db
# - Region: Oregon
# - Plan: Starter or higher

# 2. Note the Internal Database URL
# Format: postgresql://user:pass@host:port/dbname

# 3. Enable automatic backups
```

#### 1.2 Render - Redis Setup
```bash
# 1. Create Redis instance on Render
# - Name: tastebuds-redis
# - Region: Oregon (same as DB)
# - Plan: Starter

# 2. Note the connection URL
# Format: redis://red-xxxxx:6379

# 3. Configure maxmemory-policy: allkeys-lru
```

#### 1.3 Pinecone Setup
```bash
# 1. Create Pinecone account
# 2. Create index:
#    - Name: tastesync-embeddings
#    - Dimension: 1536
#    - Metric: cosine
#    - Pod Type: s1.x1

# 3. Note API key and environment
```

---

### Phase 2: Backend Deployment (Day 1-2)

#### 2.1 Prepare Backend Code
```bash
# 1. Update backend/app/config.py
# - Ensure all env vars are loaded correctly
# - Verify CORS origins include production URLs

# 2. Create render.yaml in project root

# 3. Update requirements.txt if needed

# 4. Test locally with production-like environment
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2.2 Deploy to Render
```bash
# 1. Connect GitHub repository to Render

# 2. Create new Web Service
# - Name: tastebuds-api
# - Region: Oregon
# - Branch: main
# - Build Command: cd backend && pip install -r requirements.txt
# - Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT

# 3. Link database and Redis instances

# 4. Set environment variables (see list above)

# 5. Deploy
```

#### 2.3 Run Database Migrations
```bash
# After first successful deployment:

# Option 1: Via Render Shell
cd backend
alembic upgrade head

# Option 2: Via migration script
python migrate_to_prod.py --prod-url $DATABASE_URL
```

#### 2.4 Verify Backend Deployment
```bash
# Test health endpoint
curl https://tastebuds-api.onrender.com/health

# Test API endpoints
curl https://tastebuds-api.onrender.com/api/v1/restaurants/search?term=pizza&location=Portland

# Check logs on Render dashboard
```

---

### Phase 3: Frontend Deployment (Day 2)

#### 3.1 Prepare Frontend Code
```bash
# 1. Update API URL in frontend
# Create .env.production file:
NEXT_PUBLIC_API_URL=https://tastebuds-api.onrender.com

# 2. Update package.json name
"name": "tastebuds-yelp-companion"

# 3. Test production build locally
npm run build
npm start

# 4. Verify all pages load correctly
```

#### 3.2 Deploy to Netlify
```bash
# Option 1: Via Netlify UI
# 1. Connect GitHub repository
# 2. Configure build settings:
#    - Build command: npm run build
#    - Publish directory: .next
#    - Node version: 18
# 3. Set environment variables
# 4. Deploy

# Option 2: Via Netlify CLI
netlify login
netlify init
netlify deploy --prod
```

#### 3.3 Configure Netlify
```bash
# 1. Set up custom domain (optional)
# 2. Enable HTTPS
# 3. Configure redirects in netlify.toml
# 4. Set up continuous deployment from main branch
# 5. Configure build notifications
```

#### 3.4 Verify Frontend Deployment
```bash
# 1. Open production URL
# 2. Test all major flows:
#    - Registration/Login
#    - TasteDNA quiz
#    - Restaurant search
#    - Taste Twins
#    - Profile

# 3. Check browser console for errors
# 4. Verify API calls are working
# 5. Test on mobile devices
```

---

### Phase 4: Post-Deployment Configuration (Day 3)

#### 4.1 DNS & Domain Setup (Optional)
```bash
# If using custom domain:

# 1. Configure DNS records:
#    - Frontend: CNAME to Netlify
#    - API: CNAME to Render (or use Render subdomain)

# 2. Update environment variables with new domain

# 3. Update CORS origins in backend

# 4. Test with new domain
```

#### 4.2 Monitoring & Analytics
```bash
# 1. Set up Render monitoring
#    - Enable metrics
#    - Configure alerts
#    - Set up log aggregation

# 2. Set up Netlify analytics (optional)

# 3. Configure error tracking (Sentry, etc.)

# 4. Set up uptime monitoring (UptimeRobot, etc.)
```

#### 4.3 Security Hardening
```bash
# 1. Review and rotate secrets
#    - JWT_SECRET_KEY
#    - API keys
#    - Database passwords

# 2. Configure rate limiting on API

# 3. Enable CORS restrictions

# 4. Set up security headers

# 5. Enable HTTPS only

# 6. Configure CSP headers
```

---

## Environment Variables Master List

### Frontend (Netlify)
```bash
NEXT_PUBLIC_API_URL=https://tastebuds-api.onrender.com
```

### Backend (Render)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/tastesync

# Redis
REDIS_URL=redis://red-xxxxx:6379

# External APIs
YELP_API_KEY=your_yelp_api_key
OPENAI_API_KEY=your_openai_api_key

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=tastesync-embeddings

# JWT
JWT_SECRET_KEY=generated_secure_32_char_minimum_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# App
APP_ENV=production
DEBUG=false
CORS_ORIGINS=["https://tastebuds.netlify.app"]
```

---

## Cost Estimation (Monthly)

| Service | Plan | Cost |
|---------|------|------|
| **Netlify** | Free/Starter | $0-$19 |
| **Render (Web Service)** | Starter | $7 |
| **Render (PostgreSQL)** | Starter | $7 |
| **Render (Redis)** | Starter | $7 |
| **Pinecone** | Starter | $0-$70 |
| **OpenAI API** | Usage-based | ~$10-50 |
| **Yelp API** | Free tier | $0 |
| **Total (Estimated)** | | **$31-$160/month** |

---

## Rollback Plan

### Frontend Rollback
```bash
# Via Netlify UI:
# 1. Go to Deploys tab
# 2. Find previous successful deployment
# 3. Click "Publish deploy"

# Via CLI:
netlify rollback
```

### Backend Rollback
```bash
# Via Render UI:
# 1. Go to service dashboard
# 2. Find previous deployment
# 3. Click "Redeploy"

# Via Git:
git revert HEAD
git push origin main  # Triggers auto-deploy
```

### Database Rollback
```bash
# Via Alembic:
cd backend
alembic downgrade -1  # Rollback one migration

# Via Render backup:
# 1. Go to database dashboard
# 2. Restore from backup
```

---

## Monitoring & Health Checks

### Backend Health Endpoint
```bash
GET /health
Response: {"status": "healthy", "database": "connected", "redis": "connected"}
```

### Monitoring Checklist
- [ ] API uptime monitoring
- [ ] Database connection monitoring
- [ ] Redis connection monitoring
- [ ] Error rate tracking
- [ ] Response time tracking
- [ ] API rate limit monitoring
- [ ] Cost monitoring

---

## Success Criteria

### Pre-Launch Checklist
- [ ] All environment variables configured
- [ ] Database migrations completed
- [ ] Redis cache working
- [ ] Pinecone index populated
- [ ] Frontend builds successfully
- [ ] Backend API responding
- [ ] All major features tested
- [ ] Mobile responsiveness verified
- [ ] HTTPS enabled
- [ ] CORS configured correctly
- [ ] Error tracking enabled
- [ ] Backups configured
- [ ] Monitoring set up

### Post-Launch Validation
- [ ] User registration works
- [ ] Login/logout works
- [ ] TasteDNA quiz completes
- [ ] Restaurant search returns results
- [ ] Taste Twins matching works
- [ ] Achievements system functional
- [ ] "Been Here" feature works
- [ ] Profile updates save
- [ ] Mobile experience smooth
- [ ] Performance acceptable (< 3s page load)
- [ ] No console errors
- [ ] API responses < 500ms (p95)

---

## Emergency Contacts & Resources

### Service Dashboards
- **Netlify:** https://app.netlify.com/
- **Render:** https://dashboard.render.com/
- **Pinecone:** https://app.pinecone.io/
- **OpenAI:** https://platform.openai.com/

### Documentation Links
- **Next.js Deployment:** https://nextjs.org/docs/deployment
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/
- **Render Docs:** https://render.com/docs
- **Netlify Docs:** https://docs.netlify.com/

---

## Notes

1. **Free Tier Limitations:**
   - Render free tier has cold starts (services sleep after 15 min inactivity)
   - Consider paid tier for production to avoid cold starts

2. **Database Scaling:**
   - Start with Starter plan ($7/mo)
   - Monitor connection pool usage
   - Upgrade to Standard if needed (more connections, better performance)

3. **Redis Persistence:**
   - Configure RDB snapshots for data persistence
   - Consider AOF for critical data
   - Monitor memory usage

4. **API Rate Limiting:**
   - Implement rate limiting on backend
   - Cache Yelp API responses
   - Monitor API usage to stay within free tier

5. **Security:**
   - Rotate secrets regularly
   - Use environment variables for all secrets
   - Never commit secrets to Git
   - Enable 2FA on all service accounts

---

**Last Updated:** December 7, 2024
**Version:** 1.0
**Author:** TasteBuds Development Team
