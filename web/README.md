# TasteSync

AI-powered restaurant discovery app built for the Yelp Hackathon. Creates personalized Taste DNA Profiles and matches users with Taste Twins—people with similar culinary preferences.

## Features

- **Taste DNA Quiz**: 2-minute onboarding quiz to generate your unique food personality profile
- **Taste Twin Matching**: Find users with similar taste preferences using vector similarity
- **Feeling Lucky**: One-tap AI-powered restaurant recommendations with explanations
- **Date Night Mode**: Find compatible restaurants for two people
- **Reverse Image Search**: Upload food photos to find similar restaurants
- **Gamification**: Challenges, leaderboards, and shareable taste cards

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis
- **Vector DB**: Pinecone (for taste embeddings)
- **AI/ML**: PyTorch, LangChain, scikit-learn

### Web Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **State Management**: React Context

### Mobile
- **Framework**: React Native (Expo)
- **State Management**: Zustand
- **Navigation**: React Navigation
- **UI**: Custom components with React Native Reanimated

### External APIs
- Yelp Fusion API (restaurants, reviews, photos)
- OpenAI API (explainability via LangChain)

## Project Structure

```
TasteSync/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── ai/                # ML models & embeddings
│   │   ├── db/                # Database connections
│   │   └── core/              # Security, exceptions
│   ├── requirements.txt
│   └── alembic/               # Database migrations
│
├── web/                       # Next.js Web App
│   ├── src/
│   │   ├── app/               # App router pages
│   │   ├── components/        # React components
│   │   └── lib/               # Utilities & API client
│   └── package.json
│
├── mobile/                    # React Native App
│   ├── src/
│   │   ├── screens/           # App screens
│   │   ├── components/        # Reusable components
│   │   ├── navigation/        # Navigation config
│   │   ├── services/          # API client
│   │   ├── store/             # Zustand stores
│   │   └── types/             # TypeScript types
│   └── package.json
│
└── docs/                      # Documentation
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis
- Expo CLI (for mobile)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp ../.env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Web Frontend Setup

```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev
# Open http://localhost:3000
```

### Mobile Setup

```bash
cd mobile

# Install dependencies
npm install

# Start Expo
npx expo start
```

## Environment Variables

Create a `.env` file in the root directory:

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=tastesync
POSTGRES_USER=tastesync_user
POSTGRES_PASSWORD=your_password

# Redis
REDIS_URL=redis://localhost:6379/0

# Pinecone (Vector DB)
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_env
PINECONE_INDEX_NAME=tastesync-embeddings

# Yelp API
YELP_API_KEY=your_yelp_api_key

# OpenAI (for LangChain)
OPENAI_API_KEY=your_openai_key

# JWT
JWT_SECRET_KEY=your_secret_key_min_32_chars
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Taste DNA
- `GET /api/v1/taste-dna/quiz` - Get quiz questions
- `POST /api/v1/taste-dna/quiz/submit` - Submit quiz answers
- `GET /api/v1/taste-dna/profile` - Get TasteDNA profile

### Taste Twins
- `GET /api/v1/twins` - Get user's taste twins
- `POST /api/v1/twins/refresh` - Refresh twin matching

### Discovery
- `GET /api/v1/discovery/lucky` - Feeling Lucky recommendation
- `GET /api/v1/discovery/compare` - Compare 3 options
- `GET /api/v1/discovery/trending` - Trending among twins

### Restaurants
- `GET /api/v1/restaurants/search` - Search restaurants
- `GET /api/v1/restaurants/{id}` - Get restaurant details
- `POST /api/v1/restaurants/{id}/save` - Save restaurant

## Test Account

- Email: alex.chen@example.com
- Password: password123

## API Usage (Web Frontend)

```tsx
import { api } from '@/lib/api';

const data = await api.login('alex.chen@example.com', 'password123');
const user = await api.getCurrentUser();
const twins = await api.getTwins();
```

## Demo Flow

1. **Onboarding**: User registers and completes Taste DNA quiz
2. **Profile Reveal**: Animated reveal of TasteDNA card with metrics
3. **Twin Matching**: Display Taste Twin count and similarity
4. **Discovery**: Use "Feeling Lucky" to get AI-powered recommendations
5. **Detail View**: View restaurant with Yelp data and explanation
6. **Gamification**: Complete challenges and climb leaderboard

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions using free hosting services (Vercel + Render).

## License

MIT License - Built for Yelp Hackathon
