# TasteSync Deployment Guide

This guide walks you through deploying TasteSync for **FREE** using GitHub, Vercel, and Render.

## Prerequisites

- [x] Code pushed to GitHub (https://github.com/ad2546/TasteBuds.git)
- [ ] Vercel account (sign up at vercel.com)
- [ ] Render account (sign up at render.com)
- [ ] API keys ready (Yelp, OpenAI, Pinecone)

---

## Part 1: Deploy Frontend (Next.js) to Vercel

### Option A: Deploy via Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from the root directory
vercel --prod
```

### Option B: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select your GitHub repo: `ad2546/TasteBuds`
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `web`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = (your backend URL - add after Part 2)
6. Click **"Deploy"**

**Your frontend will be live at**: `https://your-project.vercel.app`

---

## Part 2: Deploy Backend (FastAPI) to Render

### Step 1: Create PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `tastesync-db`
   - **Database**: `tastesync`
   - **User**: `tastesync_user`
   - **Region**: Oregon (or closest to you)
   - **Instance Type**: **Free**
4. Click **"Create Database"**
5. Save the **Internal Database URL** (you'll need this)

### Step 2: Create Redis Database (Upstash)

1. Go to https://upstash.com/
2. Create account → Create Redis database
3. Choose **Free tier**
4. Copy the **Redis URL** (format: `redis://...`)

### Step 3: Deploy Backend Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repo: `ad2546/TasteBuds`
3. Configure:
   - **Name**: `tastesync-backend`
   - **Region**: Oregon
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free**

4. **Add Environment Variables** (click "Advanced" → "Add Environment Variable"):

```
POSTGRES_HOST=<from database internal URL>
POSTGRES_PORT=5432
POSTGRES_DB=tastesync
POSTGRES_USER=tastesync_user
POSTGRES_PASSWORD=<from database>
REDIS_URL=<from Upstash>
PINECONE_API_KEY=<your key>
PINECONE_ENVIRONMENT=<your env>
PINECONE_INDEX_NAME=tastesync-embeddings
YELP_API_KEY=<your key>
OPENAI_API_KEY=<your key>
JWT_SECRET_KEY=<generate a secure 32+ char string>
```

5. Click **"Create Web Service"**

**Your backend will be live at**: `https://tastesync-backend.onrender.com`

### Step 4: Run Database Migrations

After the backend deploys:

1. Go to your service → **"Shell"** tab
2. Run migrations:
```bash
cd backend
alembic upgrade head
```

---

## Part 3: Connect Frontend to Backend

1. Go back to Vercel dashboard → Your project → **"Settings"** → **"Environment Variables"**
2. Add:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://tastesync-backend.onrender.com`
3. Go to **"Deployments"** → Click "..." → **"Redeploy"**

---

## Part 4: Setup External Services (Free Tiers)

### Pinecone (Vector Database)
1. Sign up at https://www.pinecone.io/
2. Create a new index:
   - **Name**: `tastesync-embeddings`
   - **Dimensions**: 1536 (for OpenAI embeddings)
   - **Metric**: cosine
3. Copy API key and environment to Render env vars

### Yelp API
1. Get API key from https://www.yelp.com/developers/v3/manage_app
2. Add to Render env vars

### OpenAI API
1. Get API key from https://platform.openai.com/api-keys
2. Add to Render env vars

---

## Your Deployed URLs

✅ **Frontend (Vercel)**: `https://your-project.vercel.app`
✅ **Backend (Render)**: `https://tastesync-backend.onrender.com`
✅ **API Docs**: `https://tastesync-backend.onrender.com/docs`

---

## Important Notes

### Free Tier Limitations

**Render (Backend)**:
- ⚠️ Spins down after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- 750 hours/month free (enough for 1 service)

**Vercel (Frontend)**:
- ✅ No sleep/wake issues
- 100GB bandwidth/month
- Unlimited builds

**PostgreSQL (Render)**:
- ⚠️ Free for 90 days, then expires
- Alternative: Migrate to **Supabase** (free forever) or **Neon** (free tier)

### Keep Your Backend Awake

To prevent cold starts, use a service like **cron-job.org**:
1. Create free account
2. Add job to ping `https://tastesync-backend.onrender.com/health` every 14 minutes

---

## Troubleshooting

### Backend won't start
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` has all dependencies

### Database connection errors
- Verify `POSTGRES_*` env vars match database credentials
- Check if database is in same region as web service

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend CORS settings allow your Vercel domain
- Check browser console for CORS errors

### Cold start issues
- First request after inactivity takes 30+ seconds
- Consider upgrading to Render paid plan ($7/mo) for always-on
- Or use keep-alive service mentioned above

---

## Updating Your Deployment

When you push to GitHub:
- ✅ **Vercel**: Auto-deploys on every push to `main`
- ✅ **Render**: Auto-deploys on every push to `main`

To disable auto-deploy:
- Vercel: Settings → Git → Disable
- Render: Settings → Build & Deploy → Disable

---

## Monitoring

- **Vercel**: Dashboard shows deployment status, logs, and analytics
- **Render**: Dashboard shows logs, metrics, and deployment history
- **Database**: Render shows connection stats

---

## Cost Breakdown (Monthly)

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Vercel | ✅ $0 | $20/mo (Pro) |
| Render | ✅ $0 | $7/mo (always-on) |
| PostgreSQL | ✅ $0 (90 days) | $7/mo |
| Redis (Upstash) | ✅ $0 | $10/mo |
| Pinecone | ✅ $0 | $70/mo |
| **Total** | **$0** | **$114/mo** |

---

## Next Steps

1. [ ] Deploy frontend to Vercel
2. [ ] Deploy backend to Render
3. [ ] Set up external APIs (Yelp, OpenAI, Pinecone)
4. [ ] Test the deployment
5. [ ] Set up keep-alive service (optional)
6. [ ] Add custom domain (optional)

**Happy Deploying! 🚀**
