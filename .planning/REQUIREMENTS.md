# Requirements: Tikodea

**Defined:** 2026-01-16
**Core Value:** Turn passive TikTok consumption into structured, actionable intelligence — every video becomes a potential business idea, investment signal, or learning opportunity.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Input (Telegram Bot)

- [ ] **INPUT-01**: User can send TikTok URL to Telegram bot and receive confirmation
- [ ] **INPUT-02**: User can include optional context with URL (`/save [url] [context]`)
- [ ] **INPUT-03**: User receives clear error message on invalid URL or processing failure

### Processing (Scraping + Analysis)

- [ ] **PROC-01**: System extracts transcript from TikTok video (speech-to-text)
- [ ] **PROC-02**: System scrapes metadata: title, description, hashtags, creator, view/like counts
- [ ] **PROC-03**: System runs Investment lens analysis (traction indicators, market signals, red flags)
- [ ] **PROC-04**: System runs Product lens analysis (problem/solution, recreatability, market size)
- [ ] **PROC-05**: System runs Content lens analysis (hook structure, viral indicators, format patterns)
- [ ] **PROC-06**: System runs Knowledge lens analysis (key facts, frameworks, actionable insights)
- [ ] **PROC-07**: System processes non-audio videos via frame extraction + vision LLM

### Dashboard

- [ ] **DASH-01**: User can view chronological feed of processed videos
- [ ] **DASH-02**: User can view video detail page with all scraped data and 4-lens analysis
- [ ] **DASH-03**: Dashboard is mobile-friendly (responsive design)
- [ ] **DASH-04**: User can chat with video context to research further (per-video research chat)

### Discovery & Organization

- [ ] **DISC-01**: User can search across transcripts, tags, and analysis results
- [ ] **DISC-02**: User can favorite/unfavorite videos and filter to favorites
- [ ] **DISC-03**: System auto-extracts tags from TikTok hashtags; user can add manual tags
- [ ] **DISC-04**: User can click to open original TikTok video URL

### Export

- [ ] **EXPO-01**: User can copy any text/analysis to clipboard
- [ ] **EXPO-02**: User can export full video analysis as Markdown file
- [ ] **EXPO-03**: User can generate Claude Code .md plan file from video insights

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Enhanced Input

- **INPUT-04**: User can paste multiple URLs in one message (bulk import)
- **INPUT-05**: User can forward TikTok shares directly to bot

### Enhanced Processing

- **PROC-08**: System extracts comment sentiment and engagement signals

### Enhanced Dashboard

- **DASH-05**: Cross-video synthesis ("What patterns across my videos?")
- **DASH-06**: Proactive insights ("Relevant to your current work")

### Advanced Features

- **ADV-01**: API access for integrations
- **ADV-02**: Multi-platform support (YouTube Shorts, Instagram Reels)
- **ADV-03**: Custom analysis lenses (user-defined frameworks)
- **ADV-04**: Analytics dashboard (consumption patterns)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Complex folder hierarchy | Search > folders for personal use; creates decision paralysis |
| Bi-directional linking / Graph view | Overkill for 50 videos/week; maintenance overhead |
| Real-time collaboration | Personal use only; contradicts simplicity goal |
| Notification systems | Notification fatigue; pull-only is sufficient |
| Social features / sharing | Twitter/X exists; export covers sharing needs |
| Offline mode | Requires processing; online-only acceptable |
| Multiple note types / templates | One consistent schema per video |
| Plugin/extension system | Fixed features, well-designed |
| Dedicated TikTok account integration | Technically fragile; Telegram bot is sufficient |
| Mobile app | Web dashboard is mobile-friendly |
| Workflow management (tasks, reminders) | View-only dashboard; user acts elsewhere |

## Traceability

Which phases cover which requirements. Updated by create-roadmap.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INPUT-01 | Phase 2: Telegram Input | Pending |
| INPUT-02 | Phase 2: Telegram Input | Pending |
| INPUT-03 | Phase 2: Telegram Input | Pending |
| PROC-01 | Phase 3: TikTok Scraping | Pending |
| PROC-02 | Phase 3: TikTok Scraping | Pending |
| PROC-03 | Phase 4: LLM Analysis | Pending |
| PROC-04 | Phase 4: LLM Analysis | Pending |
| PROC-05 | Phase 4: LLM Analysis | Pending |
| PROC-06 | Phase 4: LLM Analysis | Pending |
| PROC-07 | Phase 4: LLM Analysis | Pending |
| DASH-01 | Phase 5: Dashboard | Pending |
| DASH-02 | Phase 5: Dashboard | Pending |
| DASH-03 | Phase 5: Dashboard | Pending |
| DASH-04 | Phase 6: Research Chat | Pending |
| DISC-01 | Phase 5: Dashboard | Pending |
| DISC-02 | Phase 5: Dashboard | Pending |
| DISC-03 | Phase 5: Dashboard | Pending |
| DISC-04 | Phase 5: Dashboard | Pending |
| EXPO-01 | Phase 7: Export | Pending |
| EXPO-02 | Phase 7: Export | Pending |
| EXPO-03 | Phase 7: Export | Pending |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 21 ✓
- Unmapped: 0

---
*Requirements defined: 2026-01-16*
*Last updated: 2026-01-16 after initial definition*
