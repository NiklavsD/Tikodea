# Roadmap: Tikodea v1

**Created:** 2026-01-16
**Milestone:** v1 - TikTok Content Intelligence Platform
**Phases:** 7
**Requirements Mapped:** 21/21

## Milestone Overview

Build a personal intelligence platform that processes TikTok videos into actionable insights via Telegram input, multi-lens LLM analysis, and a chat-like dashboard.

## Phases

### Phase 1: Foundation
**Directory:** `.planning/phases/01-foundation/`
**Status:** Pending
**Research:** Skip (standard patterns)

**Objective:** Project infrastructure, database schema, and API skeleton.

**Delivers:**
- Project scaffolding (Python backend + Next.js frontend)
- SQLite database with Drizzle ORM schema
- Redis connection for job queues
- Environment configuration and secrets management
- Basic API skeleton with health endpoints

**Requirements:** None (infrastructure phase)

**Success Criteria:**
- [ ] Python backend runs with aiogram installed
- [ ] Next.js frontend builds successfully
- [ ] SQLite database initialized with video/analysis tables
- [ ] Redis connection verified
- [ ] Environment variables documented and .env.example created

---

### Phase 2: Telegram Input
**Directory:** `.planning/phases/02-telegram-input/`
**Status:** Pending
**Research:** Skip (aiogram well-documented)

**Objective:** Telegram bot that receives TikTok URLs and queues them for processing.

**Delivers:**
- Telegram bot with `/save [url] [context]` command
- TikTok URL validation
- Video record creation in database
- Job queued for processing
- Confirmation/error messages to user

**Requirements:**
- INPUT-01: User can send TikTok URL to Telegram bot and receive confirmation
- INPUT-02: User can include optional context with URL
- INPUT-03: User receives clear error message on invalid URL or processing failure

**Success Criteria:**
- [ ] Bot responds to `/save` command with TikTok URL
- [ ] Valid URLs create video record and queue job
- [ ] Invalid URLs return helpful error message
- [ ] Context parameter stored with video record
- [ ] Processing status updates sent to user

---

### Phase 3: TikTok Scraping
**Directory:** `.planning/phases/03-tiktok-scraping/`
**Status:** Pending
**Research:** Likely (TikTok anti-bot measures evolve)

**Objective:** Extract transcript and metadata from TikTok videos.

**Delivers:**
- yt-dlp integration for video download
- Supadata API integration for transcript extraction
- Metadata extraction (title, description, hashtags, creator, stats)
- Scraper abstraction layer (replaceable if APIs break)
- Retry logic with exponential backoff
- Dead letter queue for failed scrapes

**Requirements:**
- PROC-01: System extracts transcript from TikTok video (speech-to-text)
- PROC-02: System scrapes metadata: title, description, hashtags, creator, view/like counts

**Success Criteria:**
- [ ] Transcript extracted from standard TikTok videos
- [ ] Metadata captured and stored in database
- [ ] Failed scrapes retry with backoff
- [ ] Permanently failed jobs visible in DLQ
- [ ] Scraper can be swapped without changing callers

---

### Phase 4: LLM Analysis
**Directory:** `.planning/phases/04-llm-analysis/`
**Status:** Pending
**Research:** Likely (prompt engineering for structured 4-lens output)

**Objective:** Run 4 analysis lenses on every video, with vision fallback for non-audio content.

**Delivers:**
- Gemini 2.0 Flash integration
- Batched prompt for all 4 lenses (single API call)
- Structured JSON output parsing
- Investment lens analysis
- Product lens analysis
- Content lens analysis
- Knowledge lens analysis
- Vision fallback: frame extraction + vision LLM for non-audio videos
- Cost tracking per video

**Requirements:**
- PROC-03: System runs Investment lens analysis
- PROC-04: System runs Product lens analysis
- PROC-05: System runs Content lens analysis
- PROC-06: System runs Knowledge lens analysis
- PROC-07: System processes non-audio videos via frame extraction + vision LLM

**Success Criteria:**
- [ ] All 4 lenses produce structured output
- [ ] Batched prompt keeps cost <$0.01/video
- [ ] Vision fallback activates for no-transcript videos
- [ ] Frame extraction limited to 3-5 frames, resized to 512x512
- [ ] Cost per video logged and trackable

---

### Phase 5: Dashboard
**Directory:** `.planning/phases/05-dashboard/`
**Status:** Pending
**Research:** Skip (standard Next.js patterns)

**Objective:** Web dashboard showing processed videos with all analysis data.

**Delivers:**
- Chronological feed of processed videos
- Video detail page with all 4 lens analyses
- Responsive/mobile-friendly design
- Full-text search across transcripts, tags, analysis
- Favorites toggle and filter
- Tag display (auto-extracted + manual add)
- Source link to original TikTok
- SSE for real-time processing updates

**Requirements:**
- DASH-01: User can view chronological feed of processed videos
- DASH-02: User can view video detail page with all scraped data and 4-lens analysis
- DASH-03: Dashboard is mobile-friendly (responsive design)
- DISC-01: User can search across transcripts, tags, and analysis results
- DISC-02: User can favorite/unfavorite videos and filter to favorites
- DISC-03: System auto-extracts tags from TikTok hashtags; user can add manual tags
- DISC-04: User can click to open original TikTok video URL

**Success Criteria:**
- [ ] Feed displays videos newest-first with thumbnails
- [ ] Video detail shows transcript + all 4 analyses
- [ ] Dashboard usable on mobile (< 768px width)
- [ ] Search returns relevant videos within 500ms
- [ ] Favorites toggle works with visual feedback
- [ ] Tags clickable for filtering
- [ ] Source link opens TikTok in new tab

---

### Phase 6: Research Chat
**Directory:** `.planning/phases/06-research-chat/`
**Status:** Pending
**Research:** Skip (standard chat pattern with scoped context)

**Objective:** Per-video chat interface for researching video content further.

**Delivers:**
- Chat input on video detail page
- Conversation history per video
- Context injection (transcript + all lens analyses)
- LLM-powered responses about video content
- Chat history persistence

**Requirements:**
- DASH-04: User can chat with video context to research further (per-video research chat)

**Success Criteria:**
- [ ] Chat input appears on video detail page
- [ ] Questions answered using video context
- [ ] Conversation history persists across sessions
- [ ] Context stays scoped to current video
- [ ] Response time < 3 seconds

---

### Phase 7: Export
**Directory:** `.planning/phases/07-export/`
**Status:** Pending
**Research:** Skip (template generation)

**Objective:** Export video analyses for external use.

**Delivers:**
- Copy any text/analysis to clipboard
- Full video analysis as Markdown file download
- Claude Code .md plan file generation from video insights

**Requirements:**
- EXPO-01: User can copy any text/analysis to clipboard
- EXPO-02: User can export full video analysis as Markdown file
- EXPO-03: User can generate Claude Code .md plan file from video insights

**Success Criteria:**
- [ ] Copy button on all text sections with feedback
- [ ] Markdown export includes all video data and analyses
- [ ] Claude Code export generates structured .md file
- [ ] Export files have meaningful filenames

---

## Phase Dependencies

```
Phase 1 (Foundation)
    │
    ▼
Phase 2 (Telegram Input)
    │
    ▼
Phase 3 (TikTok Scraping)
    │
    ▼
Phase 4 (LLM Analysis)
    │
    ▼
Phase 5 (Dashboard)
    │
    ├──────────────────┐
    ▼                  ▼
Phase 6            Phase 7
(Research Chat)    (Export)
```

**Notes:**
- Phases 1-5 are strictly sequential
- Phases 6 and 7 can be developed in parallel after Phase 5
- Phase 3 has highest risk (TikTok anti-bot); surfaces early intentionally

## Research Flags

| Phase | Research Needed | Reason |
|-------|-----------------|--------|
| 1 | Skip | Standard project setup patterns |
| 2 | Skip | aiogram is mature with excellent docs |
| 3 | **Likely** | TikTok anti-bot measures; Supadata reliability |
| 4 | **Likely** | Prompt engineering for structured 4-lens output |
| 5 | Skip | Standard Next.js dashboard patterns |
| 6 | Skip | Standard chat pattern with scoped context |
| 7 | Skip | Template generation |

## Requirement Coverage

| Category | Requirements | Mapped |
|----------|--------------|--------|
| Input | 3 | 3 ✓ |
| Processing | 7 | 7 ✓ |
| Dashboard | 4 | 4 ✓ |
| Discovery | 4 | 4 ✓ |
| Export | 3 | 3 ✓ |
| **Total** | **21** | **21 ✓** |

---
*Roadmap created: 2026-01-16*
*Ready for: `/gsd:progress` or `/gsd:plan-phase 1`*
