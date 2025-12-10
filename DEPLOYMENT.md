# TasteBuds Deployment Guide

## ✅ Code Pushed to GitHub

Your latest changes have been successfully pushed to:
**https://github.com/ad2546/TasteBuds**

Commit: `cafebd7` - Fix mobile UI and navigation issues

---

## 🚀 Deployment Options

You have two deployment configurations ready:

### Option 1: Netlify (Frontend Only - Recommended for Quick Deploy)

**Status**: ✅ Configuration file exists (`netlify.toml`)

**Steps to Deploy**:

1. **Go to Netlify**: https://app.netlify.com/
2. **Click** "Add new site" → "Import an existing project"
3. **Connect GitHub**: Select your repository `ad2546/TasteBuds`
4. **Configure**:
   - Build command: `npm install && npm run build`
   - Publish directory: `.next`
   - Node version: 20
5. **Add Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```
6. **Deploy**: Click "Deploy site"

**Result**: Your frontend will be live at `https://[your-site-name].netlify.app`

---

### Option 2: Render (Full Stack - Backend + Database)

**Status**: ✅ Configuration file exists (`render.yaml`)

**Steps to Deploy**:

1. **Go to Render**: https://dashboard.render.com/
2. **Click** "New" → "Blueprint"
3. **Connect GitHub**: Select your repository `ad2546/TasteBuds`
4. **Render will automatically**:
   - Create a PostgreSQL database (`tastesync-db`)
   - Deploy the FastAPI backend (`tastesync-backend`)
   - Set up environment variables

5. **Add Required Environment Variables** (in Render Dashboard):
   - `REDIS_URL`: Get from Redis provider (e.g., Upstash)
   - `PINECONE_API_KEY`: Your Pinecone API key
   - `PINECONE_ENVIRONMENT`: Your Pinecone environment
   - `PINECONE_INDEX_NAME`: Your Pinecone index name
   - `YELP_API_KEY`: Your Yelp Fusion API key
   - `OPENAI_API_KEY`: Your OpenAI API key

6. **Deploy Frontend on Netlify**: Follow Option 1 above, using your Render backend URL

**Result**:
- Backend: `https://tastesync-backend.onrender.com`
- Frontend: `https://[your-site-name].netlify.app`

---

## 🔑 Environment Variables Needed

### Backend (Render):
```bash
# Database (Auto-configured by Render)
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

# Required - Add manually
REDIS_URL=
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=
PINECONE_INDEX_NAME=
YELP_API_KEY=
OPENAI_API_KEY=

# Auto-generated
JWT_SECRET_KEY=
```

### Frontend (Netlify):
```bash
NEXT_PUBLIC_API_URL=https://tastesync-backend.onrender.com
```

---

## 📝 Quick Deploy Checklist

- [x] Code pushed to GitHub
- [ ] Sign up for Netlify (https://app.netlify.com/)
- [ ] Sign up for Render (https://dashboard.render.com/)
- [ ] Get API keys:
  - [ ] Yelp Fusion API: https://www.yelp.com/developers
  - [ ] OpenAI API: https://platform.openai.com/api-keys
  - [ ] Pinecone: https://www.pinecone.io/
  - [ ] Redis (Upstash): https://upstash.com/
- [ ] Deploy backend to Render
- [ ] Deploy frontend to Netlify
- [ ] Test the live application

---

## 🛠️ Alternative: Vercel (Frontend Alternative)

If you prefer Vercel over Netlify:

1. Go to https://vercel.com/
2. Import your GitHub repository
3. Configure:
   - Framework: Next.js
   - Build command: `npm run build`
   - Environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

---

## 📱 Testing Your Deployment

Once deployed, test these features:
- [ ] User registration and login
- [ ] Quiz completion
- [ ] Taste DNA generation
- [ ] Finding taste twins
- [ ] Restaurant search
- [ ] Date night suggestions
- [ ] Mobile responsiveness
- [ ] Bottom navigation bar

---

## 🔄 Continuous Deployment

Both Netlify and Render support automatic deployments:
- Any push to `main` branch will trigger a new deployment
- Preview deployments available for pull requests

---

## 💡 Tips

1. **Free Tier Limits**:
   - Render: Backend may spin down after 15 min of inactivity
   - Netlify: 100GB bandwidth/month
   - Consider upgrading for production use

2. **Database Backup**:
   - Render's free PostgreSQL has automatic backups
   - Export your data regularly

3. **Monitoring**:
   - Check Render logs for backend errors
   - Use Netlify's analytics for frontend metrics

---

## 🆘 Troubleshooting

**Frontend can't connect to backend?**
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify backend is running on Render
- Check CORS settings in backend

**Backend startup errors?**
- Verify all environment variables are set
- Check Render logs for specific errors
- Ensure database is connected

**Database connection issues?**
- Check database credentials in Render dashboard
- Verify PostgreSQL is running
- Run migrations if needed

---

## 📞 Support

- Netlify Docs: https://docs.netlify.com/
- Render Docs: https://render.com/docs/
- GitHub Issues: https://github.com/ad2546/TasteBuds/issues
