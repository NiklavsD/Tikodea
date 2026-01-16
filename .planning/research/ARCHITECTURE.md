# Architecture Research

**Domain:** Content Processing Pipeline
**Researched:** 2026-01-16
**Confidence:** HIGH

## Executive Summary

For a single-user TikTok content intelligence platform processing 5-50 videos/week at <10 cents/video, the recommended architecture is a **modular monolith** with queue-based processing. This combines the simplicity of a monolithic deployment with clean separation of concerns.

Key architectural decisions:
- **Monolithic Node.js application** - appropriate for single-user, small scale
- **BullMQ + Redis** for job queuing (scraping, LLM analysis)
- **PostgreSQL with JSONB** for flexible analysis storage
- **SSE (Server-Sent Events)** for real-time dashboard updates
- **Sliding window + summarization** for chat context management

## System Overview

```
                            TIKODEA CONTENT INTELLIGENCE PLATFORM

    +------------------+         +------------------------------------------+
    |   TELEGRAM BOT   |         |              WEB DASHBOARD               |
    |   (Input Layer)  |         |           (Presentation Layer)           |
    +--------+---------+         +----+----------------+-------------------+-+
             |                        |                |                   |
             | TikTok URL             | REST API       | SSE Events        | Chat
             | + Context              |                |                   | Messages
             v                        v                v                   v
    +--------+---------+         +----+----------------+-------------------+-+
    |                  |         |                                           |
    |    API SERVER    +---------+              API SERVER                   |
    |   (Telegraf)     |         |          (Express/Fastify)                |
    |                  |         |                                           |
    +--------+---------+         +--------------------+----------------------+
             |                                        |
             | Add Job                                | Query/Update
             v                                        v
    +--------+----------------------------------------+----------------------+
    |                                                                        |
    |                        BULLMQ JOB QUEUE (Redis)                        |
    |                                                                        |
    |   +------------+    +------------+    +------------+    +------------+ |
    |   |  SCRAPE    |    |  ANALYZE   |    |  NOTIFY    |    |  EXPORT    | |
    |   |   QUEUE    |    |   QUEUE    |    |   QUEUE    |    |   QUEUE    | |
    |   +------------+    +------------+    +------------+    +------------+ |
    |                                                                        |
    +--------+----------------------------------------+----------------------+
             |                                        |
             | Process                                | Process
             v                                        v
    +--------+---------+         +--------------------+----------------------+
    |                  |         |                                           |
    |  SCRAPE WORKER   |         |              LLM WORKER                   |
    |                  |         |                                           |
    | - TikTok API     |         | - Investment Lens    - Product Lens      |
    | - Transcript     |         | - Content Lens       - Knowledge Lens    |
    | - Comments       |         |                                           |
    | - Metadata       |         | (Parallel execution with Claude API)     |
    |                  |         |                                           |
    +--------+---------+         +--------------------+----------------------+
             |                                        |
             | Store                                  | Store
             v                                        v
    +--------+----------------------------------------+----------------------+
    |                                                                        |
    |                     POSTGRESQL DATABASE                                |
    |                                                                        |
    |   +------------+    +------------+    +------------+    +------------+ |
    |   |   videos   |    |  analyses  |    |   chats    |    |  messages  | |
    |   +------------+    +------------+    +------------+    +------------+ |
    |                                                                        |
    +------------------------------------------------------------------------+
```

## Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|---------------|----------------|
| **Telegram Bot** | Receive TikTok URLs, send status updates | Telegraf + webhooks |
| **API Server** | REST endpoints, SSE streaming, chat handling | Express or Fastify |
| **Job Queue** | Decouple processing, handle retries, rate limiting | BullMQ + Redis |
| **Scrape Worker** | Extract video data (transcript, metadata, comments) | Playwright + transcript APIs |
| **LLM Worker** | Run 4 analysis lenses in parallel | Claude API with prompt caching |
| **Database** | Store videos, analyses, chat history | PostgreSQL + Drizzle ORM |
| **Export Service** | Generate .md files from analysis data | md-to-pdf (if PDF needed) |

## Recommended Project Structure

```
src/
├── index.ts                 # Application entry point
├── config/
│   ├── env.ts              # Environment variables
│   ├── redis.ts            # Redis connection config
│   └── database.ts         # PostgreSQL connection
│
├── db/
│   ├── schema.ts           # Drizzle schema definitions
│   ├── migrations/         # Database migrations
│   └── client.ts           # Database client instance
│
├── telegram/
│   ├── bot.ts              # Telegraf bot setup
│   ├── handlers/
│   │   ├── link.ts         # Handle TikTok URL messages
│   │   └── status.ts       # Handle status queries
│   └── middleware/
│       └── auth.ts         # Single-user validation
│
├── api/
│   ├── server.ts           # Express/Fastify setup
│   ├── routes/
│   │   ├── videos.ts       # Video CRUD endpoints
│   │   ├── chat.ts         # Chat message endpoints
│   │   ├── export.ts       # Export generation endpoints
│   │   └── events.ts       # SSE endpoint
│   └── middleware/
│       └── errors.ts       # Error handling
│
├── queue/
│   ├── setup.ts            # BullMQ queue definitions
│   ├── workers/
│   │   ├── scrape.ts       # Scraping worker
│   │   ├── analyze.ts      # LLM analysis worker
│   │   └── notify.ts       # Notification worker
│   └── jobs/
│       ├── scrape.ts       # Scrape job definition
│       └── analyze.ts      # Analysis job definition
│
├── services/
│   ├── scraper/
│   │   ├── tiktok.ts       # TikTok scraping logic
│   │   ├── transcript.ts   # Transcript extraction
│   │   └── retry.ts        # Retry with exponential backoff
│   │
│   ├── llm/
│   │   ├── client.ts       # Claude API client
│   │   ├── lenses/
│   │   │   ├── investment.ts
│   │   │   ├── product.ts
│   │   │   ├── content.ts
│   │   │   └── knowledge.ts
│   │   ├── orchestrator.ts # Parallel lens execution
│   │   └── context.ts      # Context window management
│   │
│   ├── chat/
│   │   ├── service.ts      # Chat logic
│   │   └── history.ts      # History summarization
│   │
│   └── export/
│       ├── markdown.ts     # Markdown generation
│       └── templates/      # Export templates
│
├── events/
│   ├── emitter.ts          # Event emitter setup
│   └── types.ts            # Event type definitions
│
└── types/
    ├── video.ts            # Video types
    ├── analysis.ts         # Analysis types
    └── chat.ts             # Chat types
```

## Data Flow

### Video Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VIDEO PROCESSING PIPELINE                           │
└─────────────────────────────────────────────────────────────────────────────┘

User sends TikTok URL via Telegram
                │
                ▼
┌───────────────────────────┐
│     1. TELEGRAM BOT       │ Validate URL, extract video ID
│        (Telegraf)         │ Store initial record (status: pending)
└───────────────────────────┘
                │
                │ Add to scrape queue
                ▼
┌───────────────────────────┐
│     2. SCRAPE QUEUE       │ Job: { videoId, url, userId }
│        (BullMQ)           │ Retry: 3 attempts, exponential backoff
└───────────────────────────┘
                │
                │ Worker processes
                ▼
┌───────────────────────────┐
│     3. SCRAPE WORKER      │ Extract: transcript, description,
│    (Playwright + APIs)    │ tags, comments, metadata
└───────────────────────────┘
                │
                │ On success: add to analyze queue
                │ On failure: update status, notify user
                ▼
┌───────────────────────────┐
│     4. ANALYZE QUEUE      │ Job: { videoId, scrapedData }
│        (BullMQ)           │ Priority: normal
└───────────────────────────┘
                │
                │ Worker processes
                ▼
┌───────────────────────────┐     ┌──────────────────────────────────────┐
│     5. LLM WORKER         │────▶│  PARALLEL LENS EXECUTION             │
│    (Claude API)           │     │                                      │
│                           │     │  ┌──────────┐  ┌──────────┐          │
│  Uses prompt caching for  │     │  │Investment│  │ Product  │          │
│  system prompts (90%      │     │  │  Lens    │  │   Lens   │          │
│  cost reduction)          │     │  └──────────┘  └──────────┘          │
│                           │     │                                      │
│  All 4 lenses run in      │     │  ┌──────────┐  ┌──────────┐          │
│  parallel (Promise.all)   │     │  │ Content  │  │Knowledge │          │
│                           │     │  │  Lens    │  │   Lens   │          │
└───────────────────────────┘     │  └──────────┘  └──────────┘          │
                │                 └──────────────────────────────────────┘
                │ Store results
                ▼
┌───────────────────────────┐
│     6. DATABASE           │ Update video record
│    (PostgreSQL)           │ Store analysis results (JSONB)
└───────────────────────────┘
                │
                │ Emit event
                ▼
┌───────────────────────────┐
│     7. NOTIFY WORKER      │ Send Telegram message: "Video analyzed!"
│                           │ Push SSE event to dashboard
└───────────────────────────┘
                │
                ▼
        Dashboard updates via SSE
        User sees new video with analysis
```

### Chat Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CHAT INTERACTION FLOW                             │
└─────────────────────────────────────────────────────────────────────────────┘

User sends message in dashboard chat
                │
                ▼
┌───────────────────────────┐
│     1. CHAT ENDPOINT      │ POST /api/videos/:id/chat
│        (REST API)         │ { message: "..." }
└───────────────────────────┘
                │
                │ Load context
                ▼
┌───────────────────────────┐
│  2. CONTEXT PREPARATION   │ - Video metadata + analysis summaries
│                           │ - Recent chat history (sliding window)
│  Token budget: ~8K        │ - Summarized older history (if exists)
│  Video context: ~2K       │ - System prompt with lens results
│  Chat history: ~4K        │
│  User message: ~2K        │
└───────────────────────────┘
                │
                │ Call LLM
                ▼
┌───────────────────────────┐
│     3. CLAUDE API         │ Stream response back
│    (with caching)         │ Use prompt caching for video context
└───────────────────────────┘
                │
                │ Stream + store
                ▼
┌───────────────────────────┐
│     4. RESPONSE           │ - Stream to client via SSE
│                           │ - Store message pair in DB
│                           │ - Update analysis if insights found
└───────────────────────────┘
                │
                │ Check context size
                ▼
┌───────────────────────────┐
│  5. CONTEXT MANAGEMENT    │ If history > threshold:
│                           │   Summarize older messages
│                           │   Store summary, prune raw messages
└───────────────────────────┘
```

## Database Schema

```sql
-- Videos table: Core video metadata
CREATE TABLE videos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tiktok_id       VARCHAR(64) UNIQUE NOT NULL,
    url             TEXT NOT NULL,
    status          VARCHAR(32) NOT NULL DEFAULT 'pending',
    -- status: pending | scraping | analyzing | complete | failed

    -- Scraped metadata
    title           TEXT,
    description     TEXT,
    author          VARCHAR(128),
    author_id       VARCHAR(64),
    tags            TEXT[],
    duration        INTEGER,              -- seconds
    view_count      INTEGER,
    like_count      INTEGER,
    comment_count   INTEGER,
    share_count     INTEGER,

    -- Scraped content
    transcript      TEXT,
    comments        JSONB,                -- [{author, text, likes, timestamp}]

    -- User-provided context
    user_context    TEXT,                 -- Optional context from Telegram

    -- Processing metadata
    scraped_at      TIMESTAMPTZ,
    analyzed_at     TIMESTAMPTZ,
    error_message   TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Analyses table: LLM analysis results per lens
CREATE TABLE analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id        UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    lens            VARCHAR(32) NOT NULL,
    -- lens: investment | product | content | knowledge

    -- Analysis results (JSONB for flexibility)
    result          JSONB NOT NULL,
    -- Structure varies by lens but typically includes:
    -- {
    --   summary: string,
    --   insights: string[],
    --   score: number,
    --   tags: string[],
    --   details: {...lens-specific}
    -- }

    -- LLM metadata
    model           VARCHAR(64),
    tokens_input    INTEGER,
    tokens_output   INTEGER,
    cost_cents      NUMERIC(10,4),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(video_id, lens)
);

-- Chats table: Chat sessions per video
CREATE TABLE chats (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id        UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

    -- Context management
    summary         TEXT,                 -- Summarized older history
    summary_at      TIMESTAMPTZ,          -- When summary was created

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(video_id)                      -- One chat per video
);

-- Messages table: Individual chat messages
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id         UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role            VARCHAR(16) NOT NULL, -- user | assistant
    content         TEXT NOT NULL,

    -- For assistant messages
    tokens_input    INTEGER,
    tokens_output   INTEGER,
    cost_cents      NUMERIC(10,4),

    -- For context management
    summarized      BOOLEAN DEFAULT FALSE, -- Included in summary?

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created ON videos(created_at DESC);
CREATE INDEX idx_analyses_video ON analyses(video_id);
CREATE INDEX idx_messages_chat ON messages(chat_id, created_at);
CREATE INDEX idx_messages_unsummarized ON messages(chat_id)
    WHERE summarized = FALSE;

-- GIN index for JSONB queries
CREATE INDEX idx_analyses_result ON analyses USING GIN(result);
```

### Drizzle Schema Definition

```typescript
// db/schema.ts
import { pgTable, uuid, varchar, text, integer,
         boolean, timestamp, jsonb, numeric, uniqueIndex } from 'drizzle-orm/pg-core';

export const videos = pgTable('videos', {
  id: uuid('id').primaryKey().defaultRandom(),
  tiktokId: varchar('tiktok_id', { length: 64 }).unique().notNull(),
  url: text('url').notNull(),
  status: varchar('status', { length: 32 }).notNull().default('pending'),

  // Scraped metadata
  title: text('title'),
  description: text('description'),
  author: varchar('author', { length: 128 }),
  authorId: varchar('author_id', { length: 64 }),
  tags: text('tags').array(),
  duration: integer('duration'),
  viewCount: integer('view_count'),
  likeCount: integer('like_count'),
  commentCount: integer('comment_count'),
  shareCount: integer('share_count'),

  // Scraped content
  transcript: text('transcript'),
  comments: jsonb('comments').$type<CommentData[]>(),

  // User context
  userContext: text('user_context'),

  // Processing
  scrapedAt: timestamp('scraped_at', { withTimezone: true }),
  analyzedAt: timestamp('analyzed_at', { withTimezone: true }),
  errorMessage: text('error_message'),

  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
});

export const analyses = pgTable('analyses', {
  id: uuid('id').primaryKey().defaultRandom(),
  videoId: uuid('video_id').notNull().references(() => videos.id, { onDelete: 'cascade' }),
  lens: varchar('lens', { length: 32 }).notNull(),
  result: jsonb('result').notNull().$type<AnalysisResult>(),
  model: varchar('model', { length: 64 }),
  tokensInput: integer('tokens_input'),
  tokensOutput: integer('tokens_output'),
  costCents: numeric('cost_cents', { precision: 10, scale: 4 }),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  videoLensUnique: uniqueIndex('video_lens_unique').on(table.videoId, table.lens),
}));

// Type definitions
interface CommentData {
  author: string;
  text: string;
  likes: number;
  timestamp: string;
}

interface AnalysisResult {
  summary: string;
  insights: string[];
  score?: number;
  tags: string[];
  details: Record<string, unknown>;
}
```

## Integration Points

| Service | Integration Pattern | Notes |
|---------|-------------------|-------|
| **Telegram** | Webhooks (production) / Long polling (dev) | Telegraf handles both; webhooks scale better |
| **TikTok Scraping** | Playwright + third-party transcript APIs | No official API; use Supadata or similar for transcripts |
| **Claude API** | Direct REST with prompt caching | Cache system prompts and video context |
| **Redis** | BullMQ connection | Separate from cache; maxmemory-policy: noeviction |
| **PostgreSQL** | Drizzle ORM | Type-safe queries with JSONB support |
| **Dashboard** | SSE for updates | Simpler than WebSockets for one-way updates |

### External Service Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SERVICE MAP                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   TELEGRAM   │     │   TIKTOK     │     │   CLAUDE     │
│     API      │     │   (scraping) │     │     API      │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ Bot updates        │ Video data         │ LLM inference
       │ (webhooks)         │ (Playwright)       │ (prompt caching)
       │                    │                    │
       │                    │ Transcripts        │
       │                    │ (Supadata API)     │
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                           TIKODEA APPLICATION                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌──────────────┐     ┌──────────────┐
│    REDIS     │     │  POSTGRESQL  │
│   (BullMQ)   │     │  (Drizzle)   │
└──────────────┘     └──────────────┘
```

## Build Order

Building the system in dependency order ensures each component has what it needs.

### Phase 1: Foundation (No dependencies)

```
┌─────────────────────────────────────────────────┐
│  PHASE 1: FOUNDATION                            │
│                                                 │
│  1. Project setup (TypeScript, ESLint, etc.)   │
│  2. Database schema + migrations               │
│  3. Basic API server skeleton                  │
│  4. Redis connection for BullMQ                │
│                                                 │
│  Deliverable: Empty but running application    │
└─────────────────────────────────────────────────┘
```

**Why first:** Everything else depends on database and infrastructure.

### Phase 2: Input (Depends on Phase 1)

```
┌─────────────────────────────────────────────────┐
│  PHASE 2: INPUT LAYER                           │
│                                                 │
│  1. Telegram bot setup (Telegraf)              │
│  2. URL validation + video ID extraction       │
│  3. Create video record in DB                  │
│  4. Add job to scrape queue                    │
│                                                 │
│  Deliverable: Can receive URLs, creates jobs   │
└─────────────────────────────────────────────────┘
```

**Why second:** Need to get data into the system before processing it.

### Phase 3: Scraping (Depends on Phase 2)

```
┌─────────────────────────────────────────────────┐
│  PHASE 3: SCRAPING PIPELINE                     │
│                                                 │
│  1. Scrape worker setup                        │
│  2. TikTok metadata extraction                 │
│  3. Transcript retrieval (API integration)     │
│  4. Comments extraction                        │
│  5. Retry logic with exponential backoff       │
│  6. Update video record with scraped data      │
│                                                 │
│  Deliverable: Can scrape and store video data  │
└─────────────────────────────────────────────────┘
```

**Why third:** Need video content before running analysis.

### Phase 4: Analysis (Depends on Phase 3)

```
┌─────────────────────────────────────────────────┐
│  PHASE 4: LLM ANALYSIS                          │
│                                                 │
│  1. Claude API client with prompt caching      │
│  2. Analysis worker setup                      │
│  3. Four lens implementations                  │
│  4. Parallel execution orchestrator            │
│  5. Store analysis results                     │
│  6. Cost tracking                              │
│                                                 │
│  Deliverable: Full video analysis pipeline     │
└─────────────────────────────────────────────────┘
```

**Why fourth:** Core value proposition; depends on scraped content.

### Phase 5: Dashboard (Depends on Phase 4)

```
┌─────────────────────────────────────────────────┐
│  PHASE 5: WEB DASHBOARD                         │
│                                                 │
│  1. Video list API                             │
│  2. Video detail API (with analyses)           │
│  3. SSE endpoint for real-time updates         │
│  4. React/Next.js frontend                     │
│  5. Video page with analysis display           │
│                                                 │
│  Deliverable: Can view videos and analyses     │
└─────────────────────────────────────────────────┘
```

**Why fifth:** Display layer; needs data to display.

### Phase 6: Chat (Depends on Phase 5)

```
┌─────────────────────────────────────────────────┐
│  PHASE 6: CHAT INTERFACE                        │
│                                                 │
│  1. Chat API endpoints                         │
│  2. Context preparation (video + history)      │
│  3. Message streaming                          │
│  4. History storage                            │
│  5. Context window management                  │
│  6. Summarization for long conversations       │
│                                                 │
│  Deliverable: Interactive chat per video       │
└─────────────────────────────────────────────────┘
```

**Why sixth:** Builds on existing analysis; adds interactivity.

### Phase 7: Export (Depends on Phase 6)

```
┌─────────────────────────────────────────────────┐
│  PHASE 7: EXPORT SYSTEM                         │
│                                                 │
│  1. Markdown template system                   │
│  2. Export generation endpoint                 │
│  3. Multiple format support (.md, optional PDF)│
│  4. Claude Code .md plan file format           │
│                                                 │
│  Deliverable: Export analyses to files         │
└─────────────────────────────────────────────────┘
```

**Why last:** Output layer; needs everything else complete.

### Dependency Graph

```
         ┌───────────────┐
         │  Foundation   │
         │   (Phase 1)   │
         └───────┬───────┘
                 │
         ┌───────▼───────┐
         │    Input      │
         │   (Phase 2)   │
         └───────┬───────┘
                 │
         ┌───────▼───────┐
         │   Scraping    │
         │   (Phase 3)   │
         └───────┬───────┘
                 │
         ┌───────▼───────┐
         │   Analysis    │
         │   (Phase 4)   │
         └───────┬───────┘
                 │
         ┌───────▼───────┐
         │   Dashboard   │
         │   (Phase 5)   │
         └───────┬───────┘
                 │
         ┌───────▼───────┐
         │     Chat      │
         │   (Phase 6)   │
         └───────┬───────┘
                 │
         ┌───────▼───────┐
         │    Export     │
         │   (Phase 7)   │
         └───────────────┘
```

## Cost Optimization Architecture

Target: <10 cents per video

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COST OPTIMIZATION STRATEGY                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 1. PROMPT CACHING (90% savings on cached tokens)                         │
│                                                                          │
│    System prompts for each lens: ~2000 tokens x 4 = 8000 tokens         │
│    Without caching: $0.024/video (input only)                           │
│    With caching:    $0.0024/video (90% reduction)                       │
│                                                                          │
│    Implementation:                                                       │
│    - Cache system prompts with cache_control header                     │
│    - Set TTL to 1 hour (videos processed in batches)                    │
│    - Cache video context for chat (reused across messages)              │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 2. MODEL SELECTION                                                       │
│                                                                          │
│    Analysis: Claude 3.5 Sonnet ($3/$15 per MTok)                        │
│    - Good balance of quality and cost                                   │
│    - 4 lenses x ~2K output = 8K tokens = $0.12 output                   │
│                                                                          │
│    Chat: Claude 3.5 Haiku ($0.25/$1.25 per MTok)                        │
│    - Faster, cheaper for interactive use                                │
│    - ~500 token responses = negligible cost                             │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 3. PARALLEL EXECUTION (latency, not cost)                                │
│                                                                          │
│    All 4 lenses run simultaneously via Promise.all                      │
│    - Same total tokens, faster completion                               │
│    - ~5 seconds instead of ~20 seconds sequential                       │
└──────────────────────────────────────────────────────────────────────────┘

Estimated cost per video:
┌────────────────────┬─────────────────┬──────────────┐
│ Component          │ Tokens          │ Cost         │
├────────────────────┼─────────────────┼──────────────┤
│ Input (cached)     │ ~12K (90% hit)  │ ~$0.004      │
│ Input (uncached)   │ ~2K fresh       │ ~$0.006      │
│ Output (4 lenses)  │ ~8K             │ ~$0.12       │
├────────────────────┼─────────────────┼──────────────┤
│ TOTAL              │ ~22K            │ ~$0.08-0.10  │
└────────────────────┴─────────────────┴──────────────┘

Note: Chat interactions add ~$0.001-0.005 per message using Haiku
```

## Error Handling Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ERROR HANDLING STRATEGY                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ SCRAPING ERRORS                                                          │
│                                                                          │
│ Retry strategy:                                                          │
│   - 3 attempts with exponential backoff (1s, 2s, 4s)                    │
│   - Add jitter to prevent thundering herd                               │
│   - On final failure: mark video as 'failed', store error               │
│                                                                          │
│ Specific handlers:                                                       │
│   - 429 Rate Limited: Check Retry-After header, wait                    │
│   - 404 Not Found: Mark as 'not_found', notify user                     │
│   - Timeout: Retry with longer timeout                                  │
│   - Network Error: Retry immediately once                               │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ LLM ERRORS                                                               │
│                                                                          │
│ Retry strategy:                                                          │
│   - 2 attempts for transient errors                                     │
│   - Exponential backoff with jitter                                     │
│                                                                          │
│ Specific handlers:                                                       │
│   - 429 Rate Limited: Wait per Retry-After                              │
│   - 500/503: Retry after 5 seconds                                      │
│   - Context too long: Truncate transcript, retry                        │
│   - Partial lens failure: Save successful lenses, retry failed          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ QUEUE ERRORS (BullMQ)                                                    │
│                                                                          │
│ Built-in handling:                                                       │
│   - Stalled jobs: Automatically retried after 30s                       │
│   - Failed jobs: Moved to failed queue with error                       │
│   - Graceful shutdown: Complete active jobs before exit                 │
│                                                                          │
│ Monitoring:                                                              │
│   - Error event handler for logging                                     │
│   - Job lifecycle events for status updates                             │
└──────────────────────────────────────────────────────────────────────────┘
```

## Real-Time Updates Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REAL-TIME UPDATE STRATEGY                           │
│                                                                             │
│  Recommendation: Server-Sent Events (SSE)                                   │
│                                                                             │
│  Why SSE over WebSocket:                                                    │
│  - One-way updates (server → client) are sufficient                        │
│  - Simpler implementation                                                   │
│  - Auto-reconnection built-in                                              │
│  - Works over HTTP/2                                                       │
│  - No need for Socket.IO complexity                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Event Types:
┌────────────────────┬─────────────────────────────────────────────────────┐
│ Event              │ Payload                                             │
├────────────────────┼─────────────────────────────────────────────────────┤
│ video:created      │ { videoId, url, status: 'pending' }                │
│ video:scraping     │ { videoId, status: 'scraping' }                    │
│ video:scraped      │ { videoId, status: 'scraped', metadata: {...} }    │
│ video:analyzing    │ { videoId, status: 'analyzing' }                   │
│ video:complete     │ { videoId, status: 'complete', analyses: [...] }   │
│ video:failed       │ { videoId, status: 'failed', error: '...' }        │
│ chat:message       │ { videoId, chatId, message: {...} }                │
└────────────────────┴─────────────────────────────────────────────────────┘

Implementation:
┌──────────────────────────────────────────────────────────────────────────┐
│ // Server: SSE endpoint                                                  │
│ app.get('/api/events', (req, res) => {                                  │
│   res.setHeader('Content-Type', 'text/event-stream');                   │
│   res.setHeader('Cache-Control', 'no-cache');                           │
│   res.setHeader('Connection', 'keep-alive');                            │
│                                                                          │
│   const sendEvent = (event, data) => {                                  │
│     res.write(`event: ${event}\n`);                                     │
│     res.write(`data: ${JSON.stringify(data)}\n\n`);                     │
│   };                                                                     │
│                                                                          │
│   // Subscribe to internal event emitter                                │
│   eventEmitter.on('video:*', sendEvent);                                │
│   req.on('close', () => eventEmitter.off('video:*', sendEvent));        │
│ });                                                                      │
└──────────────────────────────────────────────────────────────────────────┘
```

## Sources

### Primary (HIGH confidence)
- [BullMQ Official Documentation](https://docs.bullmq.io/) - Queue patterns, production guidelines
- [Drizzle ORM Documentation](https://orm.drizzle.team/docs/column-types/pg) - JSONB column types, schema design
- [Anthropic Pricing Documentation](https://platform.claude.com/docs/en/about-claude/pricing) - Prompt caching details

### Secondary (MEDIUM confidence)
- [Scalable Telegram Bot with Node.js, BullMQ](https://medium.com/@pushpesh0/building-a-scalable-telegram-bot-with-node-js-bullmq-and-webhooks-6b0070fcbdfc) - Telegram + queue architecture
- [SSE vs WebSockets vs Long Polling 2025](https://dev.to/haraf/server-sent-events-sse-vs-websockets-vs-long-polling-whats-best-in-2025-5ep8) - Real-time update comparison
- [LLM Cost Optimization](https://www.glukhov.org/post/2025/11/cost-effective-llm-applications/) - Token optimization strategies
- [Multi-Step LLM Chains Best Practices](https://www.deepchecks.com/orchestrating-multi-step-llm-chains-best-practices/) - LLM orchestration patterns
- [Anthropic Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) - Parallel subagent patterns
- [Monolith vs Microservices 2025](https://dev.to/prateekbka/monolith-vs-microservices-making-the-right-architectural-choice-in-2025-4a27) - Architecture decision framework
- [Drizzle ORM PostgreSQL Best Practices 2025](https://gist.github.com/productdevbook/7c9ce3bbeb96b3fabc3c7c2aa2abc717) - Schema patterns
- [TikTok Scraping Guide 2025](https://decodo.com/blog/scrape-tiktok) - Scraping architecture
- [TikTok Rate Limits](https://developers.tiktok.com/doc/tiktok-api-v2-rate-limit) - Official rate limit documentation

### Tertiary (LOW confidence - needs validation)
- [TikTok Transcript APIs](https://supadata.ai/tiktok-transcript-api) - Third-party transcript services (verify pricing/reliability)
- [LLM Chat History Summarization](https://mem0.ai/blog/llm-chat-history-summarization-guide-2025) - Context window management patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Overall Architecture | HIGH | Monolith with queues is well-established pattern |
| Queue Processing | HIGH | BullMQ is battle-tested, official docs comprehensive |
| Database Schema | HIGH | PostgreSQL + JSONB is standard for flexible analysis storage |
| Real-time Updates | HIGH | SSE is appropriate for one-way server-push |
| LLM Orchestration | MEDIUM | Parallel execution pattern is standard; cost estimates need validation |
| TikTok Scraping | MEDIUM | Official APIs limited; third-party transcript APIs may be unreliable |
| Chat Context Management | MEDIUM | Patterns are established but implementation details vary |
| Cost per Video | LOW | Estimate based on 2025 pricing; actual costs depend on transcript length and analysis depth |
