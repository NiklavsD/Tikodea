# Tikodea

## What This Is

A personal intelligence platform that processes TikTok videos into actionable insights. Send a TikTok link via Telegram, and Tikodea scrapes the content, runs it through multiple analytical lenses (investment, product, content, knowledge), and presents structured opportunities on a chat-like dashboard where you can research further.

## Core Value

Turn passive TikTok consumption into structured, actionable intelligence — every video becomes a potential business idea, investment signal, or learning opportunity.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Telegram bot to receive TikTok links with optional context parameter
- [ ] TikTok scraping: transcript, description, tags, comments
- [ ] Visual processing: frame extraction + vision LLM for non-audio videos and photo slideshows
- [ ] Multi-lens LLM analysis running all lenses on every video:
  - Investment lens (stock plays, shorts, market timing)
  - Product lens (recreatability, dropshipping viability, market size)
  - Content lens (AI recreation potential, reposting opportunity)
  - Knowledge lens (skills to learn, trends to track, tech to explore)
- [ ] Chat-like dashboard interface (each video = own page with all data, visuals, metrics)
- [ ] Interactive chat on each video page to research further or update insights
- [ ] Chronological feed of all processed videos
- [ ] Favorite functionality for videos
- [ ] Claude Code export: button to write .md plan file for actionable ideas

### Out of Scope

- Dedicated TikTok account integration — technically fragile, Telegram bot is primary
- Multi-user support — personal use only
- Workflow management (tasks, reminders, Notion export) — view-only dashboard
- Mobile app — web dashboard sufficient

## Context

- Personal tool for extracting value from TikTok browsing
- Focus areas: products, services, AI, automation, coding, finance, trends, skills
- Each processed video should enable: understanding where money is made, investment opportunities, product recreation potential, content repurposing opportunities, knowledge extraction
- Claude Code integration allows acting on ideas directly

## Constraints

- **Cost**: <10 cents per video processing (affects LLM model choices)
- **Volume**: 5-50 TikToks per week
- **Tech stack**: Open — whatever works best for solo development

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Telegram bot as primary input | TikTok automation is fragile and frequently blocked | — Pending |
| All lenses on every video | User wants comprehensive analysis, not routing complexity | — Pending |
| Chat-like UI per video | Matches mental model of LLM interfaces, enables research continuation | — Pending |
| View-only dashboard | Keeps scope focused, user acts elsewhere | — Pending |
| Claude Code file export | Simpler than CLI integration, still actionable | — Pending |

---
*Last updated: 2026-01-16 after initialization*
