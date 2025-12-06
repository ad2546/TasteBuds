# TasteSync Web App

Modern food discovery web application built with Next.js 15, TypeScript, and Tailwind CSS.

## 🚀 Quick Start

\`\`\`bash
npm install
npm run dev
# Open http://localhost:3000
\`\`\`

## 🔗 Backend

- API: http://localhost:8000/api/v1
- Docs: http://localhost:8000/docs

## 📝 Test Account

- Email: alex.chen@example.com
- Password: password123

## 🎨 Add V0 Components

\`\`\`bash
npx shadcn@latest add "YOUR_V0_LINK"
\`\`\`

## 📦 API Usage

\`\`\`tsx
import { api } from '@/lib/api';

const data = await api.login('alex.chen@example.com', 'password123');
const user = await api.getCurrentUser();
const twins = await api.getTwins();
\`\`\`

**Ready to build!** 🎨
