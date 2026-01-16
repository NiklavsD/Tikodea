# Project Research Summary

**Project:** Tikodea
**Domain:** TikTok Content Intelligence Platform
**Researched:** 2026-01-16
**Confidence:** HIGH

## Executive Summary

Tikodea is a content processing pipeline that extracts TikTok video content (transcript, metadata, comments) and runs it through 4 specialized analysis lenses (Investment, Product, Content, Knowledge). The recommended stack is a **Python backend** (aiogram for Telegram, RQ for job queues) with a **Next.js dashboard** and **SQLite** for storage.

**Key insight:** The <10 cents/video budget is easily achievable. Gemini 2.0 Flash's free tier (100 requests/day) covers personal use entirely. Even paid, costs are ~$0.01/video. The multi-lens analysis is genuinely differentiated — no existing tool offers 4-perspective breakdown of video content.

**Critical risk:** TikTok scraping. Third-party transcript APIs (Supadata) may be unreliable. Mitigation: yt-dlp as fallback + vision LLM for no-transcript videos. Build scraper as replaceable module.

## Key Findings

### Recommended Stack

**Core technologies:**
- **Gemini 2.0 Flash**: $0.10/$0.40 per 1M tokens — cheapest multimodal LLM, handles text AND vision
- **aiogram 3.24+**: Modern async Telegram bot framework, actively maintained
- **Next.js 15 + SSE**: Dashboard with real-time updates, simpler than WebSockets
- **SQLite + Drizzle ORM**: Zero-config database with JSON columns, perfect for personal use
- **RQ (Redis Queue)**: Simple Python job queue, built-in scheduling

**Cost breakdown per video:**
| Component | Cost |
|-----------|------|
| Gemini Flash (free tier) | $0.00 |
| Gemini Flash (paid, 4 lenses) | ~$0.003 |
| Vision fallback (5 frames) | ~$0.004 |
| **Total** | **<$0.01** |

### Expected Features

**Must have (table stakes):**
- Quick capture via Telegram
- Transcript extraction
- Full-text search
- Chronological feed with favorites
- Source link back to TikTok

**Should have (competitive):**
- Multi-lens analysis (Investment, Product, Content, Knowledge) — core differentiator
- Context parameter with captures
- Per-video research chat (v1.x)
- Claude Code export

**Defer (v2+):**
- Cross-video synthesis
- Proactive insights
- Multi-platform (YouTube Shorts, Reels)

### Architecture Approach

Modular monolith with queue-based processing. Single Node.js/Python application with BullMQ/RQ handling async jobs.

**Major components:**
1. **Telegram Bot** — Receive URLs, send status updates
2. **Scrape Worker** — Extract video data via yt-dlp + Supadata
3. **LLM Worker** — Run 4 lenses in parallel via Gemini/Claude
4. **Dashboard** — Next.js with SSE for real-time updates
5. **Database** — SQLite with JSON columns for flexible analysis storage

### Critical Pitfalls

1. **TikTok anti-bot detection** — Use yt-dlp (handles TikTok well), build scraper as replaceable module
2. **Vision LLM cost explosion** — Transcript-first strategy, max 3-5 frames, resize to 512x512
3. **LLM token multiplication** — Single batched prompt for all 4 lenses, not 4 separate calls
4. **Telegram webhook chaos** — Use polling in dev, webhook with proper SSL in prod
5. **No dead letter queue** — Implement DLQ from day one for failed job visibility

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation
**Rationale:** Everything depends on database and infrastructure
**Delivers:** Project setup, database schema, Redis connection, API skeleton
**Addresses:** API key security (PITFALLS), schema indexing (PITFALLS)
**Avoids:** Hardcoded configuration, missing .gitignore

### Phase 2: Telegram Input
**Rationale:** Need to get data into the system before processing
**Delivers:** Telegram bot receiving URLs, video records in DB, jobs queued
**Uses:** aiogram 3.24+
**Avoids:** Webhook configuration chaos (use polling for dev)

### Phase 3: TikTok Scraping
**Rationale:** Need video content before analysis
**Delivers:** Transcript extraction, metadata, comments scraping
**Uses:** yt-dlp + Supadata API
**Avoids:** Anti-bot detection (random delays, abstraction layer)
**Implements:** Retry with exponential backoff, DLQ for failed scrapes

### Phase 4: LLM Analysis
**Rationale:** Core value proposition
**Delivers:** 4-lens analysis pipeline, parallel execution, cost tracking
**Uses:** Gemini 2.0 Flash (or Claude Haiku for budget)
**Avoids:** Token multiplication (batched prompts), vision cost explosion (transcript-first)

### Phase 5: Dashboard
**Rationale:** Display layer needs data to display
**Delivers:** Video list, video detail, SSE real-time updates, favorites
**Uses:** Next.js 15, Tailwind, shadcn/ui
**Avoids:** Over-engineering (start with polling, add real-time if needed)

### Phase 6: Research Chat
**Rationale:** Builds on existing analysis, adds interactivity
**Delivers:** Per-video chat, context management, history storage
**Avoids:** Context window explosion (rolling window, summarization)

### Phase 7: Export
**Rationale:** Output layer, needs everything else complete
**Delivers:** Markdown export, Claude Code .md plan files
**Uses:** Template system

### Phase Ordering Rationale

- **Sequential dependencies:** Each phase requires the previous (can't analyze without scraping, can't display without data)
- **Risk mitigation:** Scraping (highest risk) comes early so issues surface before building dependent features
- **Cost validation:** LLM analysis phase includes cost tracking to validate <10¢/video target early
- **Complexity graduation:** Simple features first (input, scraping), complex features later (chat, export)

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 3 (Scraping):** TikTok's anti-bot measures evolve; may need to evaluate Supadata alternatives
- **Phase 4 (LLM):** Prompt engineering for structured 4-lens output; test batched vs separate calls

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Foundation):** Well-documented setup patterns
- **Phase 2 (Telegram):** aiogram is mature, excellent docs
- **Phase 5 (Dashboard):** Standard Next.js patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Gemini pricing verified, aiogram well-established |
| Features | MEDIUM | Multi-lens is novel; no direct comparables |
| Architecture | HIGH | Monolith + queues proven pattern |
| Pitfalls | HIGH | Verified with official docs and real incident reports |

**Overall confidence:** HIGH

### Gaps to Address

- **TikTok transcript API reliability:** Test Supadata with real URLs before committing
- **Gemini free tier limits:** May need to batch 4 lenses into single prompt to stay under 100 RPD
- **Vision frame selection:** No production-ready library for adaptive frame selection; may need custom implementation

## Sources

### Primary (HIGH confidence)
- [Google Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing) — LLM costs
- [Supadata TikTok API](https://supadata.ai/tiktok-transcript-api) — Transcript extraction
- [aiogram Documentation](https://docs.aiogram.dev/) — Telegram bot framework
- [BullMQ Documentation](https://docs.bullmq.io/) — Job queue patterns

### Secondary (MEDIUM confidence)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp) — TikTok download fallback
- [Scrapfly TikTok Guide](https://scrapfly.io/blog/posts/how-to-scrape-tiktok-python-json) — Scraping patterns
- [Telegram Core Bots FAQ](https://core.telegram.org/bots/faq) — Rate limits

### Tertiary (LOW confidence)
- [SocialKit TikTok APIs](https://www.socialkit.dev/) — Comments extraction (needs validation)

---
*Research completed: 2026-01-16*
*Ready for: `/gsd:define-requirements`*
