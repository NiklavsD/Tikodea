# Stack Research: TikTok Content Intelligence Pipeline

**Domain:** TikTok Content Intelligence Pipeline
**Researched:** 2026-01-16
**Overall Confidence:** HIGH

## Executive Summary

This document provides the recommended technology stack for building Tikodea - a personal TikTok content intelligence platform. The stack is optimized for:
- **Cost efficiency:** <10 cents per video processing
- **Low volume:** 5-50 TikToks/week (personal use)
- **Full-stack simplicity:** Minimal infrastructure, maximum capability

**Primary recommendation:** Python backend with aiogram for Telegram, Next.js for dashboard, SQLite for storage, and Gemini 2.0 Flash for LLM analysis (free tier covers personal use).

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | 3.12+ | Backend runtime | Unified language for Telegram bot, scraping, LLM calls, and job processing. Best library support for TikTok extraction. |
| **Next.js** | 15.x | Web dashboard | App Router with SSE for real-time updates. Excellent chat UI patterns. One framework for frontend + API routes. |
| **SQLite** | 3.51+ | Database | Zero-config, single-file database. JSON1 extension for flexible document storage. Perfect for personal projects. |
| **Redis** | 7.x | Job queue backend | Required for RQ. Lightweight, can run in Docker. Free tier on Upstash if cloud-hosted. |

### TikTok Content Extraction

| Library/Service | Cost | Purpose | When to Use |
|-----------------|------|---------|-------------|
| **Supadata API** | 100 free/month, then ~$0.01/credit | Transcript extraction | PRIMARY: Best for getting existing TikTok captions/transcripts. Use `mode=native` to avoid AI generation costs. |
| **yt-dlp** | Free | Video download | FALLBACK: Download video files when transcript unavailable. Extract for vision analysis or local Whisper. |
| **SocialKit API** | 20 free/month, $13/2000 credits | Comments + metadata | Comments extraction, video stats, engagement data. |

**Extraction Strategy:**
1. Try Supadata first (native transcripts) - 0 cost if transcript exists
2. If no transcript: Download video with yt-dlp, extract frames for vision LLM
3. Comments via SocialKit or Apify ($0.30/1000 comments)

### LLM Providers (Analysis)

| Provider | Model | Input/1M | Output/1M | Use Case |
|----------|-------|----------|-----------|----------|
| **Google** | Gemini 2.0 Flash | $0.10 | $0.40 | PRIMARY: Text analysis. Free tier (100 RPD) covers personal use. |
| **Google** | Gemini 2.0 Flash | $0.10 | $0.40 | VISION: Frame analysis when no transcript. Same model handles multimodal. |
| **OpenAI** | GPT-4o-mini | $0.15 | $0.60 | FALLBACK: If Gemini rate-limited. Slightly more expensive but comparable quality. |
| **DeepSeek** | DeepSeek-R1 | $0.55 | $2.19 | REASONING: Complex analysis requiring chain-of-thought. Cost-effective for deep analysis. |

**Why Gemini 2.0 Flash:**
- Free tier: 100 requests/day, 1M token context
- Multimodal: Same model handles text AND images (video frames)
- Cheapest paid tier: $0.10/1M input (vs $0.15 GPT-4o-mini)
- Native video understanding (can process frames directly)

### Telegram Bot

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **aiogram** | 3.24+ | Telegram bot framework | Modern async framework. Active development. FSM for conversation state. Webhook + polling support. |

**Why aiogram over python-telegram-bot:**
- Fully async (native asyncio)
- Better middleware support
- Cleaner router-based handlers
- More actively maintained in 2025

### Web Dashboard

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **Next.js** | 15.x | React framework | App Router, SSE streaming, API routes. Single deployment unit. |
| **Tailwind CSS** | 4.x | Styling | Utility-first. Fast development. |
| **shadcn/ui** | latest | UI components | Chat-like interfaces, cards, real-time indicators. Copy-paste components. |
| **Tanstack Query** | 5.x | Data fetching | Caching, background refetch, optimistic updates. |

**Real-time Updates:**
Use **Server-Sent Events (SSE)** over WebSockets:
- Simpler implementation in Next.js App Router
- Works with serverless (no persistent connections needed)
- Perfect for one-way updates (processing status, new results)
- Native browser support via EventSource API

### Database

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **SQLite** | 3.51+ | Primary database | JSON1 extension for flexible schemas. Single file backup. No server. |
| **better-sqlite3** | 11.x | Node.js driver | Synchronous API, fastest SQLite driver for Node.js. |
| **Drizzle ORM** | 0.40+ | Type-safe queries | Lightweight ORM. Great TypeScript support. SQL-like syntax. |

**Schema approach:**
- Relational tables for videos, analyses, users
- JSON columns for flexible analysis results
- Full-text search via FTS5 extension for searching insights

### Job Queue

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **RQ (Redis Queue)** | 2.6+ | Background jobs | Simple. Python-native. Perfect for low-volume async processing. |

**Why RQ over Celery:**
- Zero configuration (just Redis)
- Simpler API (just `queue.enqueue(func, args)`)
- Built-in scheduling (since RQ 2.5)
- Perfect for <1000 jobs/day
- Dashboard via rq-dashboard

**Job types:**
1. `scrape_tiktok` - Extract content from URL
2. `analyze_video` - Run 4-lens LLM analysis
3. `extract_frames` - Vision processing for no-transcript videos

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **Docker Compose** | Local dev environment | Redis, optional PostgreSQL for scaling later |
| **uv** | Python package manager | Fast, modern. Replaces pip + venv + poetry |
| **pnpm** | Node.js package manager | Fast, disk-efficient |
| **Ruff** | Python linting/formatting | All-in-one, fast |
| **Biome** | JS/TS linting/formatting | Fast alternative to ESLint + Prettier |

---

## Installation

### Python Backend (Telegram + Processing)

```bash
# Create project with uv
uv init tikodea-backend
cd tikodea-backend

# Add dependencies
uv add aiogram redis rq httpx google-generativeai openai yt-dlp

# Development tools
uv add --dev ruff pytest
```

### Next.js Dashboard

```bash
# Create Next.js app
pnpm create next-app@latest tikodea-dashboard --typescript --tailwind --app --src-dir

cd tikodea-dashboard

# Add dependencies
pnpm add better-sqlite3 drizzle-orm @tanstack/react-query
pnpm add -D drizzle-kit @types/better-sqlite3

# UI components (shadcn)
pnpm dlx shadcn@latest init
pnpm dlx shadcn@latest add card button input scroll-area
```

### Infrastructure

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|------------------------|
| SQLite | PostgreSQL | Need multi-user access, >100GB data, or advanced querying. Overkill for personal project. |
| RQ | Celery | Need complex workflows, multiple brokers, or >10k jobs/day. Too heavy for this use case. |
| aiogram | python-telegram-bot | Team already knows it. Otherwise aiogram is more modern. |
| Next.js | FastAPI + React | Prefer separate frontend/backend. Adds deployment complexity. |
| Gemini Flash | Claude Haiku | Need better reasoning. Claude 3 Haiku is $0.25/$1.25 vs Gemini's $0.10/$0.40. |
| SSE | WebSockets | Need bidirectional real-time (multiplayer, collaborative editing). SSE simpler for dashboards. |
| Supadata | Apify | Need bulk scraping, multiple accounts. Apify more robust at scale but complex. |
| yt-dlp | Playwright | Need to render JavaScript-heavy pages. yt-dlp handles most TikTok cases. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **MongoDB** | Overkill for personal project. Adds operational complexity. | SQLite with JSON columns |
| **Kubernetes** | Way too complex for single-user app. | Docker Compose or single VPS |
| **Kafka** | Enterprise message queue. Massive overkill. | Redis + RQ |
| **Claude 3.5 Sonnet/Opus** | $3-15/1M tokens. Will blow budget on 4-lens analysis. | Gemini Flash or GPT-4o-mini |
| **GPT-4o (full)** | $5/$15 per 1M. Too expensive for multiple analysis passes. | GPT-4o-mini or Gemini Flash |
| **AWS Lambda** | Cold starts, complex deployment for Python. | Simple VPS or Railway |
| **TikTok Official API** | Requires business verification, limited data access, no transcripts. | Supadata + yt-dlp |
| **Whisper self-hosted** | GPU costs ($276+/month minimum) exceed API costs at low volume. | OpenAI Whisper API or Deepgram |
| **Bull/BullMQ** | Node.js only. Your backend is Python. | RQ (Python-native) |

---

## Cost Analysis

### Per-Video Processing Cost

**Scenario:** 1 TikTok video, 60 seconds, with transcript available

| Step | Tokens/Resources | Cost |
|------|------------------|------|
| Supadata transcript | 1 credit (native mode) | $0.00 (free tier) |
| SocialKit comments | 1 credit | $0.00 (free tier) |
| LLM Analysis (4 lenses) | ~8,000 input + ~4,000 output tokens | See below |

**LLM Cost Breakdown (4-lens analysis):**

| Provider | Input Cost | Output Cost | Total |
|----------|------------|-------------|-------|
| Gemini 2.0 Flash (free) | $0.00 | $0.00 | **$0.00** |
| Gemini 2.0 Flash (paid) | $0.0008 | $0.0016 | **$0.0024** |
| GPT-4o-mini | $0.0012 | $0.0024 | **$0.0036** |

**With Vision (no transcript, 10 frames):**

| Step | Cost |
|------|------|
| yt-dlp download | $0.00 |
| Frame extraction (10 frames, ~1290 tokens each) | 12,900 tokens |
| Gemini 2.0 Flash vision | ~$0.0013 input |
| Text analysis (4 lenses) | ~$0.0024 |
| **Total with vision** | **~$0.0037** |

### Monthly Cost Estimate

| Volume | Gemini Free Tier | Gemini Paid | GPT-4o-mini |
|--------|------------------|-------------|-------------|
| 10 videos/week | $0.00 | $0.10 | $0.15 |
| 25 videos/week | $0.00 | $0.24 | $0.36 |
| 50 videos/week | $0.00 | $0.48 | $0.72 |

**Verdict:** At 50 videos/week, you stay well under $1/month with Gemini paid tier, or $0 with free tier.

### Infrastructure Costs

| Service | Free Tier | Paid |
|---------|-----------|------|
| Railway (hosting) | $5/month credit | ~$5-10/month |
| Upstash Redis | 10k commands/day free | $0.20/100k commands |
| Vercel (dashboard) | Hobby tier free | - |
| **Total Infrastructure** | **$0-5/month** | **$5-15/month** |

---

## Architecture Overview

```
[Telegram Bot]                    [Web Dashboard]
     |                                  |
     v                                  v
[aiogram] -----> [Redis/RQ] <----- [Next.js API]
     |               |                  |
     v               v                  v
[Supadata]     [RQ Workers]        [SQLite DB]
[yt-dlp]           |
                   v
            [Gemini Flash API]
                   |
                   v
              [Analysis Results]
                   |
                   v
              [SQLite DB] <----> [Dashboard UI]
```

**Flow:**
1. User sends TikTok link via Telegram
2. aiogram bot enqueues `scrape_tiktok` job
3. RQ worker extracts content (Supadata -> yt-dlp fallback)
4. Worker enqueues `analyze_video` job
5. Analysis runs 4 lenses via Gemini Flash
6. Results stored in SQLite
7. Dashboard shows real-time updates via SSE
8. User can ask follow-up questions in chat interface

---

## Sources

### TikTok Scraping
- [Supadata TikTok Transcript API](https://supadata.ai/tiktok-transcript-api) - Free API with 100 requests/month
- [SocialKit TikTok APIs](https://www.socialkit.dev/blog/best-tiktok-data-apis-2025) - Comments, stats, transcripts
- [Apify TikTok Scraper](https://apify.com/clockworks/tiktok-scraper) - Bulk scraping alternative
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp) - Video download fallback

### LLM Pricing
- [IntuitionLabs LLM Pricing Comparison 2025](https://intuitionlabs.ai/articles/llm-api-pricing-comparison-2025) - Comprehensive pricing data
- [Google Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing) - Official Gemini pricing
- [OpenAI API Pricing](https://platform.openai.com/docs/pricing) - Official OpenAI pricing
- [DataCamp Vision Language Models 2026](https://www.datacamp.com/blog/top-vision-language-models) - VLM comparison

### Telegram Bot
- [aiogram Documentation](https://docs.aiogram.dev/) - Official docs
- [aiogram GitHub](https://github.com/aiogram/aiogram) - Latest version 3.24

### Web Dashboard
- [Next.js SSE Tutorial](https://damianhodgkiss.com/tutorials/real-time-updates-sse-nextjs) - SSE implementation guide
- [SSE Comeback 2025](https://portalzine.de/sses-glorious-comeback-why-2025-is-the-year-of-server-sent-events/) - Why SSE over WebSockets

### Database & Queue
- [RQ Documentation](https://python-rq.org/) - Simple Python job queue
- [Drizzle ORM SQLite](https://orm.drizzle.team/docs/get-started-sqlite) - TypeScript ORM
- [SQLite JSON Functions](https://www.sqlite.org/json1.html) - JSON1 extension docs

### Transcription (Fallback)
- [OpenAI Whisper Pricing](https://brasstranscripts.com/blog/openai-whisper-api-pricing-2025-self-hosted-vs-managed) - $0.006/min
- [Deepgram Pricing](https://deepgram.com/pricing) - $0.0077/min, $200 free credits

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| LLM Pricing | HIGH | Verified against official pricing pages (OpenAI, Google) |
| TikTok Extraction | MEDIUM | APIs may change; Supadata/SocialKit are third-party services |
| Telegram Bot | HIGH | aiogram is well-established, actively maintained |
| Dashboard Stack | HIGH | Next.js + SSE is standard pattern for real-time dashboards |
| Database | HIGH | SQLite is proven for personal/low-volume apps |
| Job Queue | HIGH | RQ is mature, well-documented |
| Cost Estimates | MEDIUM | Based on current pricing; API costs can change |

---

## Open Questions

1. **Supadata reliability:** Third-party service for TikTok transcripts. Need fallback strategy if service changes.
   - Mitigation: yt-dlp + vision LLM as backup

2. **Gemini free tier limits:** 100 RPD may be tight if doing 4 analysis passes per video.
   - Mitigation: Batch analysis into single prompt, or use paid tier (~$0.50/month)

3. **TikTok anti-bot measures:** yt-dlp may require periodic updates.
   - Mitigation: Keep yt-dlp updated, have API fallback (Apify)

---

## Metadata

**Research date:** 2026-01-16
**Valid until:** 2026-02-16 (30 days - LLM pricing changes frequently)
**Researcher:** Claude Code (GSD Research Agent)
