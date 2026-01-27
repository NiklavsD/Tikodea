# Tikodea

**TikTok Intelligence Platform** - Transform TikTok videos into structured ideas, research, and business opportunities.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🎯 What is Tikodea?

Tikodea turns passive TikTok consumption into actionable intelligence. Send a TikTok link via Telegram, and Tikodea automatically:

- 📝 **Extracts** transcripts, metadata, and engagement data
- 🤖 **Analyzes** through 4 specialized AI lenses
- 💡 **Identifies** business opportunities, investment signals, and learning insights
- 💬 **Enables** interactive research through a chat-based dashboard

Every TikTok video becomes a potential business idea, investment signal, or learning opportunity.

## ✨ Key Features

### Multi-Lens AI Analysis

Every video is analyzed through 4 specialized lenses:

1. **💰 Investment Lens** - Stock plays, market timing signals, trend predictions
2. **📦 Product Lens** - Dropshipping viability, recreatability, market size
3. **🎬 Content Lens** - Reposting potential, AI recreation opportunities
4. **📚 Knowledge Lens** - Skills to learn, trends to track, tech to explore

### Smart Scraping with Fallbacks

Resilient multi-method scraping ensures you always get data:

```
Priority Chain:
1. Supadata API    → Transcripts (100/month FREE)
2. ScrapTik API    → Rich metadata (50/month FREE)
3. oEmbed API      → Basic metadata (unlimited FREE)
4. URL parsing     → Minimal fallback (always works)
```

**Current Success Rate**: 87.5% (7/8 data fields) using entirely free APIs

### Telegram Bot Interface

- 🔗 Send TikTok links directly to your bot
- 📝 Add context with your message for better analysis
- ⚡ Automatic processing and analysis
- 🔔 Get notified when complete

### Interactive Dashboard

- 📊 Chronological feed of all processed videos
- 💬 Chat interface for deeper research on each video
- ⭐ Favorite videos for quick access
- 📥 Export actionable ideas directly to Claude Code

## 🏗️ Architecture

```
┌─────────────────┐
│  Telegram Bot   │  ← User sends TikTok URL
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Scraper API   │  ← Multi-method fallback strategy
├─────────────────┤
│  • Supadata     │  (transcripts)
│  • ScrapTik     │  (metadata)
│  • oEmbed       │  (fallback)
│  • URL Parser   │  (minimal)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Analyzer   │  ← 4-lens analysis via OpenRouter
├─────────────────┤
│  • Investment   │
│  • Product      │
│  • Content      │
│  • Knowledge    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │  ← SQLite storage
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │  ← Next.js + React
└─────────────────┘
```

## 🚀 Tech Stack

**Backend:**
- Python 3.12+ with FastAPI
- SQLAlchemy (SQLite database)
- httpx (API requests)
- Redis (task queue)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

**Integrations:**
- Telegram Bot API
- OpenRouter (LLM: Gemini 2.0 Flash)
- Supadata API (video transcripts)
- ScrapTik/RapidAPI (TikTok metadata)
- IPRoyal (rotating proxies)

## 📦 Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Redis server
- Telegram Bot Token ([create one](https://t.me/botfather))
- OpenRouter API key ([get one](https://openrouter.ai/))
- Supadata API key ([get one](https://supadata.ai/))
- RapidAPI key ([optional](https://rapidapi.com/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/NiklavsD/Tikodea.git
cd Tikodea
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
cd ../frontend
npm install
```

5. **Start services**

Terminal 1 - Backend:
```bash
cd backend
uvicorn api:app --reload
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Terminal 3 - Telegram Bot:
```bash
cd backend
python bot.py
```

## 🔧 Configuration

### API Keys Required

Add these to your `.env` file:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_openrouter_key
SUPADATA_API_KEY=your_supadata_key

# Optional (enhances scraping)
RAPIDAPI_KEY=your_rapidapi_key
PROXY_URL=your_proxy_url

# Infrastructure
REDIS_URL=redis://localhost:6379
DATABASE_URL=file:./tikodea.db
```

### Quota Monitoring

Check your API usage:
```bash
cd backend
python check_quota.py
```

Output:
```
==================================================
ScrapTik API Quota Status
==================================================
Used:      12/50 requests
Remaining: 38 requests
Progress:  24.0%

[#########-------------------------------] 24.0%

[OK] Healthy: 38 requests available
==================================================
```

## 🧪 Testing

### Test Scraper with Real URL

```bash
cd backend
python test_scraping.py
```

### Run Backend Tests

```bash
cd backend
pytest
```

### Run Frontend Tests

```bash
cd frontend
npm test
```

## 📊 Current Status

### ✅ Completed (v1)

- [x] Telegram bot for receiving TikTok links
- [x] Multi-method scraping with fallbacks
- [x] Transcript extraction (Supadata)
- [x] Metadata scraping (oEmbed + URL parsing)
- [x] 4-lens LLM analysis (OpenRouter/Gemini)
- [x] SQLite database with video storage
- [x] API quota tracking system
- [x] Basic test suite

### 🚧 In Progress

- [ ] Frontend dashboard (Next.js)
- [ ] Interactive chat per video
- [ ] ScrapTik endpoint configuration (view/like counts)
- [ ] Visual frame extraction for photo slideshows

### 📋 Planned (v2)

- [ ] Video favoriting
- [ ] Claude Code export (.md plan files)
- [ ] Search and filtering
- [ ] Bulk video processing
- [ ] Performance optimizations

## 💡 Usage Example

1. **Send a TikTok link** to your Telegram bot:
```
https://www.tiktok.com/@user/video/123456789
Optional context: This is about food safety claims
```

2. **Bot processes the video**:
- Extracts transcript and metadata
- Runs 4-lens AI analysis
- Stores results in database

3. **View in dashboard**:
- See full transcript
- Read investment opportunities
- Explore product ideas
- Identify content recreation potential
- Learn from extracted knowledge

4. **Interactive research**:
- Chat with AI about the video
- Ask follow-up questions
- Export actionable ideas

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Supadata](https://supadata.ai/) - Video transcript API
- [ScrapTik](https://scraptik.com/) - TikTok scraping API
- [OpenRouter](https://openrouter.ai/) - LLM API aggregation
- [IPRoyal](https://iproyal.com/) - Proxy services

## 📧 Contact

- GitHub: [@NiklavsD](https://github.com/NiklavsD)
- Project: [Tikodea](https://github.com/NiklavsD/Tikodea)

---

**Note**: This project is for educational and personal use. Respect TikTok's terms of service and content creators' rights.
