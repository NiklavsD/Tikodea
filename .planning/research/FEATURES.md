# Feature Research: Content Intelligence Platform

**Domain:** Content Intelligence / Video-to-Insight / Second Brain
**Researched:** 2026-01-16
**Confidence:** MEDIUM (synthesized from multiple sources; specific to your use case extrapolated)

## Executive Summary

Content intelligence platforms sit at the intersection of three domains: video processing tools (extract data from media), second brain apps (organize and connect knowledge), and research chat interfaces (interact with accumulated knowledge). Your platform's unique value is the multi-lens analysis approach—this is genuinely differentiated in the market.

**Key insight:** The biggest trap in this space is feature bloat. Apps like Evernote and Notion grew so complex they became liabilities. For personal use with 5-50 videos/week, simplicity beats capability. Build for the action loop: Input → Process → Insight → Action.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that are baseline expectations—users will feel frustrated if missing.

| Feature | Why Expected | Complexity | Notes |
|---------|-------------|------------|-------|
| **Quick Capture** | Second brain apps train users to expect frictionless input | LOW | Telegram bot handles this well |
| **Transcript Extraction** | Video content is useless without searchable text | MEDIUM | Core to your pipeline |
| **Search/Find** | Every knowledge tool has instant search | LOW | Full-text across transcripts, tags, notes |
| **Chronological Feed** | Mental model of "timeline" is universal | LOW | Your planned approach is correct |
| **Favorites/Bookmarks** | Users expect to flag important items | LOW | Heart/star icon, consistent language |
| **Video Link Back** | Users need to return to source | LOW | Original TikTok URL always accessible |
| **Basic Tags** | Categorization is expected in any knowledge system | LOW | Auto-generated from TikTok + manual |
| **Mobile-Friendly** | Content often consumed on mobile | MEDIUM | Dashboard must work on phone |
| **Export Capability** | Data portability builds trust | LOW | Markdown export minimum |

### Differentiators (Competitive Advantage)

Features that make your platform uniquely valuable—your moat.

| Feature | Value Proposition | Complexity | Notes |
|---------|------------------|------------|-------|
| **Multi-Lens Analysis** | No tool does 4-perspective breakdown of videos | HIGH | Investment, Product, Content, Knowledge lenses—this is your core innovation |
| **Video-Specific Intelligence** | Generic note apps don't understand video structure | HIGH | Visual processing for non-audio, comment sentiment, hashtag analysis |
| **Context-Aware Capture** | Telegram `/save [context]` ties content to intent | LOW | Captures "why" at moment of discovery—huge for later retrieval |
| **Per-Video Research Chat** | Chat with individual video insights is novel | MEDIUM | Better than general-purpose AI—scoped context |
| **Claude Code Export** | Direct path to action (`.md` plan file) | MEDIUM | No other tool generates dev-ready specs from video insights |
| **Proactive Surfacing** | "Here's what's relevant to your current work" | HIGH | V2+ feature—requires understanding user's projects |
| **Investment Signal Extraction** | Structured data: traction indicators, market size, founder quality | HIGH | Specific schema for investment lens |
| **Content Strategy Extraction** | Hook structure, engagement patterns, viral indicators | MEDIUM | Specific schema for content lens |

### Anti-Features (Commonly Requested, Often Problematic)

Things to deliberately NOT build—common requests that create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|--------------|-----------------|-------------|
| **Complex Folder Hierarchy** | Users think they need organization | Creates decision paralysis; search > folders for personal use | Flat structure + powerful search + tags |
| **Bi-directional Linking / Graph View** | Obsidian popularized this | Overkill for 50 videos/week; maintenance overhead explodes | Simple related videos via tags |
| **Real-time Collaboration** | "Maybe I'll share with team" | Adds massive complexity; you're building for personal use | Export to share, not collaborative editing |
| **Multiple Note Types** | "I need different templates" | Complexity creep; each video is already structured | One video = one consistent schema |
| **Notification Systems** | "Remind me about insights" | Notification fatigue; you control when to engage | No notifications—pull only |
| **Social Features** | "Share my discoveries" | Scope creep; Twitter/X exists for sharing | Export to share externally |
| **Offline Mode (Full)** | "Access anywhere" | Massive complexity for MVP; your videos need processing | Online-only acceptable for v1 |
| **Complex Tag Taxonomies** | "I need hierarchical tags" | Over-organization is the #1 second-brain killer | Flat tags, use sparingly |
| **Custom Analysis Lenses** | "I want to add my own lens" | Scope explosion; 4 lenses already covers most use cases | Fixed lenses v1; evaluate v2 |
| **Automatic Categorization AI** | "Auto-tag everything" | Creates noise; wrong tags worse than no tags | AI suggests, human confirms |
| **Version History** | "Track changes to notes" | Personal use, low value | Not needed |
| **Plugin/Extension System** | "Let me customize" | Obsidian complexity path; you're not building an OS | Fixed features, well-designed |

---

## Feature Dependencies

```
Input Layer
    |
    v
[Telegram Bot] --> [TikTok Scraper] --> [Processing Pipeline]
                                              |
                    +-------------------------+
                    |                         |
                    v                         v
            [Transcript]              [Visual Analysis]
                    |                         |
                    +------------+------------+
                                 |
                                 v
                    [Multi-Lens Analysis Engine]
                         |    |    |    |
            +------------+    |    |    +------------+
            |                 |    |                 |
            v                 v    v                 v
       [Investment]    [Product]  [Content]    [Knowledge]
            |                 |    |                 |
            +--------+--------+----+--------+--------+
                     |                       |
                     v                       v
              [Storage Layer]        [Search Index]
                     |                       |
                     +----------+------------+
                                |
                                v
                         [Dashboard]
                              |
            +-----------------+-----------------+
            |                 |                 |
            v                 v                 v
       [Feed View]     [Video Detail]    [Claude Export]
            |                 |
            v                 v
       [Favorites]     [Research Chat]
```

**Critical Path:** Telegram → Scraper → Transcript → Analysis → Storage → Dashboard

**Parallel Work Possible:**
- Dashboard UI can be built while scraper is developed
- Research chat can be added after basic video detail page works
- Export can be added once storage schema is stable

---

## MVP Definition

### v1.0 Launch With (Essential)

- [ ] **Telegram Bot Input** — Core capture mechanism; `/save [url]` with optional context
- [ ] **TikTok Scraping** — Transcript, description, hashtags, basic metadata
- [ ] **Multi-Lens Analysis** — All 4 lenses (Investment, Product, Content, Knowledge) on every video
- [ ] **Video Detail Page** — Display all extracted data and analysis; one video per page
- [ ] **Chronological Feed** — Simple timeline of processed videos
- [ ] **Favorites Toggle** — Mark important videos; filter to favorites
- [ ] **Full-Text Search** — Search across transcripts, analysis, and tags
- [ ] **Basic Tags** — Auto-extracted hashtags + manual tag add
- [ ] **Source Link** — Always link back to original TikTok

**Why this scope:** Delivers core value loop (capture → process → insight) without complexity. Every feature here directly supports finding and extracting value from TikTok videos.

### v1.x Add After Validation (Post-Launch)

| Feature | Trigger to Add |
|---------|----------------|
| **Per-Video Research Chat** | Users want to ask questions about specific videos |
| **Visual Processing** | Users submit non-audio videos and need visual analysis |
| **Comment Sentiment** | Users want deeper engagement signals |
| **Claude Code Export** | Users want to act on insights programmatically |
| **Bulk Import** | Users have backlog of saved TikToks to process |
| **Related Videos** | Users want to see thematically similar content |

**Rationale:** These enhance the core loop but aren't essential for initial value. Build when specific user need emerges.

### v2+ Future Consideration (Defer)

| Feature | Why Defer |
|---------|-----------|
| **Cross-Video Synthesis** | "What patterns do I see across all my videos?" — Requires substantial data and complex prompting |
| **Proactive Insights** | "Surface relevant past videos for current project" — Needs understanding of user's active work |
| **API Access** | Build integrations with other tools — Personal use doesn't need this |
| **Multi-Platform** | YouTube Shorts, Instagram Reels — Adds complexity; TikTok-specific is your niche |
| **Team Features** | Sharing, permissions, collaborative annotation — Contradicts personal-use simplicity |
| **Custom Lenses** | User-defined analysis frameworks — Scope explosion risk |
| **Analytics Dashboard** | "Show me my consumption patterns" — Nice-to-have, not core value |

---

## Feature Details by Category

### 1. Input Features

**Current Plan:** Telegram bot with `/save [url] [optional context]`

**Table Stakes:**
- Accept TikTok URLs (various formats)
- Confirmation message on successful queue
- Error message on failure (invalid URL, processing error)

**Enhancements (v1.x):**
- Bulk paste (multiple URLs in one message)
- Forward TikTok shares directly
- Context prompt: "What are you researching?" if no context provided

**Anti-Features:**
- Browser extension (complexity for personal use)
- Mobile app (Telegram is sufficient)
- Email input (over-engineering)

### 2. Processing Features

**Current Plan:** Scrape + transcript + multi-lens analysis

**Table Stakes:**
- Transcript extraction (speech-to-text)
- Basic metadata (title, description, hashtags, creator)
- Processing status feedback

**Differentiators:**
- 4-lens analysis with structured output
- Visual analysis for non-audio content
- Context parameter integration into analysis

**Anti-Features:**
- Real-time processing (async queue is fine for personal use)
- User-configurable processing options (fixed pipeline is simpler)

### 3. Analysis Lenses

**Investment Lens:**
- Traction indicators (views, engagement, growth claims)
- Market size signals
- Founder/team quality indicators
- Business model observations
- Red flags

**Product Lens:**
- Problem being solved
- Solution approach
- User experience observations
- Technical implementation hints
- Competitive positioning

**Content Lens:**
- Hook structure and timing
- Engagement techniques
- Format patterns
- Viral indicators
- Creator style notes

**Knowledge Lens:**
- Key facts and claims
- Frameworks and mental models
- Actionable insights
- Related topics
- Source credibility

### 4. Dashboard Features

**Current Plan:** Chat-like interface, chronological feed, per-video pages

**Table Stakes:**
- Responsive design (works on mobile)
- Fast loading (<2s for feed)
- Clean, uncluttered interface

**Feed View:**
- Chronological default (newest first)
- Favorites filter
- Tag filter
- Search integration
- Thumbnail + title + date + tags preview

**Video Detail Page:**
- All 4 lens analyses displayed
- Original transcript
- Metadata (creator, date, stats)
- Tags (auto + manual)
- Favorite toggle
- Source link to TikTok
- Research chat (v1.x)

**Anti-Features:**
- Dashboard customization (fixed layout is fine)
- Multiple view modes (one layout, well-designed)
- Widget system (over-engineering)

### 5. Research Chat (v1.x)

**Value:** Ask questions about a specific video's content and analysis

**Interface:**
- Chat input at bottom of video detail page
- Conversation history for that video
- Context: transcript + all lens analyses

**Example Queries:**
- "What's the investment thesis here?"
- "How could I replicate this content strategy?"
- "What are the product risks?"
- "Summarize in 3 bullets"

**Anti-Features:**
- Cross-video chat (too complex for v1)
- Persistent memory across sessions (session-based is fine)
- Voice input (typing is sufficient)

### 6. Export Features

**Current Plan:** Claude Code export for `.md` plan files

**Table Stakes:**
- Copy to clipboard (any text)
- Markdown export (full video analysis)

**Differentiator:**
- Claude Code export: Generate structured `.md` file suitable for Claude Code's `/gsd:define-requirements` or similar workflows

**Export Schema:**
```markdown
# [Video Title] - Insights Export

**Source:** [TikTok URL]
**Processed:** [Date]
**Context:** [User's original context]

## Investment Perspective
[Structured content]

## Product Perspective
[Structured content]

## Content Perspective
[Structured content]

## Knowledge Perspective
[Structured content]

## Suggested Next Steps
[AI-generated action items]
```

**Anti-Features:**
- Multiple export formats (Markdown is universal)
- Integration API (personal use)
- Scheduled exports (manual is fine)

---

## UX Principles from Research

### From Second Brain Apps

1. **"Feels like an extension of your mind, not a chore"** — If organizing takes effort, users abandon
2. **"3-point summary over 10 pages"** — Distill to actionable, bite-sized output
3. **"Search beats folders"** — Full-text search > complex hierarchy for personal use
4. **"Tags for context, not taxonomy"** — Ask "Where do I want to see this again?" not "What category?"

### From Research Chat Interfaces (Perplexity/ChatGPT)

1. **Citations matter** — Show source (original TikTok, specific part of transcript)
2. **Context-aware follow-ups** — Chat should understand what video you're discussing
3. **Scoped context is powerful** — Per-video chat beats general knowledge base chat

### From Video Analysis Tools

1. **Transcription is foundational** — Everything else builds on accurate text
2. **Multi-format output** — Bullet points for scanning, narrative for understanding
3. **Quick insights first** — Summary before deep analysis

### From Bookmarking/Favorites

1. **Consistent language** — Don't mix "favorite," "bookmark," "save"
2. **Visual feedback** — Immediate confirmation when favorited
3. **One-tap access** — Favorites should be single click/tap away

---

## Complexity Estimates

| Feature | Effort | Risk | Notes |
|---------|--------|------|-------|
| Telegram Bot | LOW | LOW | Straightforward API |
| TikTok Scraping | MEDIUM | MEDIUM | Anti-scraping measures may require updates |
| Transcript Extraction | MEDIUM | LOW | Use established APIs |
| Multi-Lens Analysis | HIGH | MEDIUM | Prompt engineering + structured output |
| Visual Processing | HIGH | MEDIUM | Requires vision model integration |
| Dashboard Feed | LOW | LOW | Standard web app |
| Video Detail Page | LOW | LOW | Display layer |
| Search | MEDIUM | LOW | Full-text indexing |
| Favorites | LOW | LOW | Boolean toggle |
| Research Chat | MEDIUM | MEDIUM | Context management, conversation state |
| Claude Export | LOW | LOW | Template generation |

---

## Sources

### Primary (HIGH confidence)
- [Forte Labs - Tagging Guide](https://fortelabs.com/blog/a-complete-guide-to-tagging-for-personal-knowledge-management/) - Tagging best practices
- [Zapier - Obsidian vs Notion](https://zapier.com/blog/obsidian-vs-notion/) - Feature comparison, what matters
- [UX Planet - Favorites Design](https://uxplanet.org/how-to-design-better-favorites-d1fe8f204a1) - UX patterns

### Secondary (MEDIUM confidence)
- [ClickUp - Second Brain Apps 2025](https://clickup.com/blog/second-brain-apps/) - Feature expectations
- [Sprout Social - TikTok Analytics](https://sproutsocial.com/insights/tiktok-analytics-tools/) - Video analysis features
- [Collabnix - Perplexity Review 2025](https://collabnix.com/perplexity-ai-review-2025-the-complete-guide-to-pros-cons-and-user-experience/) - Research chat interface
- [Document360 - KM Challenges](https://document360.com/blog/knowledge-management-challenges/) - Anti-patterns
- [XDA - Outdated Productivity Apps](https://www.xda-developers.com/productivity-apps-that-are-officially-too-outdated-in-2025/) - Feature bloat problems

### Tertiary (LOW confidence - needs validation)
- [AgencyGDT - TikTok Summarizer](https://agencygdt.com/tiktok-summarizer/) - TikTok-specific tools
- [Tribe AI - Context-Aware Memory](https://www.tribe.ai/applied-ai/beyond-the-bubble-how-context-aware-memory-systems-are-changing-the-game-in-2025) - Chat memory features

---

## Metadata

**Confidence breakdown:**
- Table stakes: HIGH — Well-established patterns across tools
- Differentiators: MEDIUM — Multi-lens analysis is novel; no direct comparables
- Anti-features: HIGH — Consistent patterns of over-engineering problems
- MVP scope: MEDIUM — Based on project context; may need adjustment

**Research gaps:**
- Specific TikTok scraping legal/technical constraints (needs technical spike)
- Exact multi-lens prompt engineering (needs prototyping)
- Claude Code export format requirements (needs Claude Code docs review)

**Valid until:** 2026-02-16 (30 days - stable domain)
