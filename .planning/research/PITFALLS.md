# Pitfalls Research: TikTok Content Intelligence Platform

**Domain:** TikTok Content Intelligence (Scraping + LLM Analysis + Telegram Bot + Dashboard)
**Researched:** 2026-01-16
**Confidence:** HIGH (verified with official docs and multiple sources)

---

## Critical Pitfalls

### Pitfall 1: TikTok Anti-Bot Detection Evolving Faster Than Your Scraper

**What goes wrong:**
Your scraper works for 2 weeks, then suddenly returns empty responses or gets IP-banned. TikTok's anti-bot systems in 2026 combine TLS fingerprinting, behavioral analysis, IP reputation scoring, and JavaScript challenges. Bypassing one layer is not enough.

**Why it happens:**
- Using outdated libraries (Puppeteer-stealth was discontinued Feb 2025 and Cloudflare specifically detects its patterns now)
- Datacenter IPs get flagged immediately; residential IPs that previously triggered blocks carry low trust scores
- Behavioral patterns give you away: requesting 50 pages in 10 seconds, navigating in perfectly sequential order, no mouse movement or scroll pauses
- Geographic inconsistencies between IP location and browser timezone raise flags

**How to avoid:**
1. Use modern stealth tools: Camoufox, Nodriver, or SeleniumBase UC Mode (not Puppeteer-stealth)
2. Implement human-like delays: random pauses (2-8 seconds), occasional "wrong" scrolls, mouse movement simulation
3. Use residential proxies, not datacenter IPs
4. For personal use at 5-50 videos/week: consider using yt-dlp which handles TikTok well
5. Build scraper as a replaceable module - expect to update it quarterly

**Warning signs:**
- Increasing empty responses
- CAPTCHAs appearing more frequently
- 403/429 responses spiking
- Same code working on one machine but not another (fingerprint issue)

**Phase to address:** Phase 1 (Scraping Foundation) - Build with abstraction layer that can swap implementations

---

### Pitfall 2: Vision LLM Costs Explode with Naive Frame Extraction

**What goes wrong:**
Processing a 60-second TikTok at 1 frame/second with Claude Sonnet costs ~$0.22 per video in vision tokens alone. At 50 videos/week, that is $11/week just for vision - blowing past the <10 cents/video budget on vision alone.

**Why it happens:**
- Naive uniform frame sampling extracts frames that are 90% redundant (same scene, same person talking)
- Each frame at 1280x720 consumes ~1,229 tokens
- No frame deduplication - sending nearly identical frames
- Using expensive models (Opus/Sonnet) for visual analysis that Haiku could handle
- Not leveraging TikTok's existing transcripts/captions

**How to avoid:**
1. **Transcript-first strategy**: Extract TikTok's auto-generated captions via yt-dlp (`--write-auto-subs`) - this is FREE
2. **Smart frame selection**: Only extract frames at scene changes, not uniform intervals
3. **Resolution reduction**: Resize to 512x512 or smaller (~350 tokens vs 1,229)
4. **Frame budget**: Hard limit of 3-5 key frames per video
5. **Model tiering**: Use Haiku ($1/M input) for visual description, Sonnet only for analysis
6. **Skip vision when transcript is rich**: Many TikToks are talking-head videos where transcript is sufficient

**Warning signs:**
- API costs per video exceeding $0.05
- Processing time per video exceeding 30 seconds
- Vision tokens dominating your usage dashboard

**Phase to address:** Phase 2 (LLM Pipeline) - Design frame selection strategy before building

---

### Pitfall 3: LLM Token Costs Compound Through Poor Prompt Design

**What goes wrong:**
Each of your 4 analysis "lenses" sends the full transcript + description + tags + comments, multiplying input tokens by 4x. Verbose prompts with redundant instructions add 500+ tokens per call. Output tokens (3-5x more expensive) spiral because you did not constrain response format.

**Why it happens:**
- Copy-pasting prompts without optimization
- Not using structured output (JSON) to constrain response length
- Repeating context across multiple lens calls instead of batching
- Using few-shot examples when zero-shot works
- Not leveraging prompt caching (90% savings on repeated context)

**How to avoid:**
1. **Single-pass multi-lens**: One prompt that returns all 4 analyses, not 4 separate calls
2. **Structured output**: Request JSON with specific fields - prevents rambling responses
3. **Prompt compression**: Remove redundant instructions, test minimal prompts first
4. **Prompt caching**: Structure prompts with static instructions at top, dynamic content at bottom
5. **Model routing**: Use Haiku for extraction tasks, Sonnet for analysis
6. **Output token limits**: Explicitly set max_tokens to prevent verbose responses

**Cost calculation for budget:**
- Target: <$0.10/video total
- With transcript (~500 tokens) + 3 frames (~1,000 tokens) + prompt (~200 tokens) = ~1,700 input tokens
- At Haiku rates ($1/M): $0.0017 input
- Output ~500 tokens at $5/M: $0.0025
- Total per call: ~$0.004 - leaves room for 4 lens passes or one combined pass

**Warning signs:**
- Monthly API bill growing faster than video count
- Average tokens per video exceeding 5,000 input
- Output tokens exceeding input tokens

**Phase to address:** Phase 2 (LLM Pipeline) - Design prompt architecture before implementation

---

### Pitfall 4: Telegram Webhook Configuration Chaos

**What goes wrong:**
Bot works perfectly in development (polling mode), then fails silently in production (webhook mode). Errors get swallowed - you do not know the bot is broken until users complain. Or worse: bot responds twice, webhook conflicts with polling, SSL certificate issues.

**Why it happens:**
- Cannot use polling and webhook simultaneously - Telegram rejects this
- Webhook requires valid SSL certificate (self-signed needs special handling)
- Only ports 443, 80, 88, 8443 supported for webhooks
- Port 443 requires root/admin permissions or reverse proxy
- Flask/Express webhook endpoints silently swallow errors unlike polling mode

**How to avoid:**
1. **Development**: Use polling (simpler, no SSL needed)
2. **Production**: Use webhook with proper SSL (Let's Encrypt via nginx reverse proxy)
3. **Use secret path**: `https://yourdomain.com/webhook/{bot_token}` - Telegram recommends this
4. **Explicit error handling**: Wrap webhook handler in try/catch, log all errors
5. **Health check endpoint**: Separate `/health` endpoint to verify bot is running
6. **Webhook verification**: After setting, call `getWebhookInfo` to confirm

**Warning signs:**
- Bot works locally but not in production
- No error logs despite bot not responding
- `getWebhookInfo` returns empty or error
- Users report intermittent responses

**Phase to address:** Phase 4 (Telegram Bot) - Set up webhook infrastructure correctly from start

---

### Pitfall 5: Telegram Rate Limits and Flood Control

**What goes wrong:**
You send a video analysis result (which might include several messages for different lenses), hit the rate limit, get 429 errors, retry immediately, get IP-banned for 30 seconds or even 900 seconds.

**Why it happens:**
- 2025 API changes: per-chat rate limiting is now 1 message per 3 seconds for groups
- Global limit: 30 messages/second per bot token
- Retrying before `retry_after` window resets the timer (doubles the wait)
- Multiple serverless instances multiplying effective rate
- Not knowing that `answerCallbackQuery` does NOT count against rate limit

**How to avoid:**
1. **Respect `retry_after` exactly**: Add 10-25% jitter to prevent thundering herd
2. **Single response strategy**: Combine all lens results into ONE message, not 4 separate messages
3. **Queue outgoing messages**: Redis-backed rate limiter if scaling beyond single process
4. **Use `answerCallbackQuery` immediately**: Does not count against limits, improves UX
5. **Batch media**: Use `sendMediaGroup` instead of multiple `sendPhoto`

**Warning signs:**
- HTTP 429 errors in logs
- Users seeing "loading" spinner for 15+ seconds
- Bot responses arriving out of order

**Phase to address:** Phase 4 (Telegram Bot) - Implement rate-aware message sending

---

### Pitfall 6: Dashboard Over-Engineering with Real-Time Overkill

**What goes wrong:**
You build WebSocket real-time updates for a dashboard that one person uses 5-50 times per week. The complexity adds bugs, the infrastructure adds cost, and the user does not even notice because they are not staring at the dashboard waiting for updates.

**Why it happens:**
- Assuming "modern" means "real-time everything"
- Following enterprise patterns for personal tools
- React useEffect dependency arrays causing infinite re-renders (Cloudflare DDoS'd themselves this way in 2025)
- Premature optimization for scale that will never come

**How to avoid:**
1. **Polling-first for personal use**: Simple `setInterval` fetch every 30 seconds is fine for single user
2. **Optimistic UI**: Show "processing" state immediately, poll for completion
3. **SSG over SSR**: Static generation with client-side data fetching beats server-side rendering for dashboards
4. **Memoization discipline**: Use `React.memo`, `useMemo` for chart components (reduced re-renders by 70% in one case study)
5. **Virtualization for lists**: If showing 100+ videos, use react-window

**Warning signs:**
- Multiple WebSocket connections in dev tools
- Dashboard slower than expected despite few videos
- useEffect running continuously in React DevTools

**Phase to address:** Phase 5 (Dashboard) - Start simple, add real-time only if needed

---

### Pitfall 7: Chat Context Window Explosion

**What goes wrong:**
Your "interactive research" feature accumulates conversation history. After 10 exchanges, you are sending 50,000+ tokens of context per message. Costs spike, responses slow down, and eventually the model starts "forgetting" earlier context due to truncation you did not notice.

**Why it happens:**
- Naive full-context retention until token limit
- Truncation happens invisibly - chat history looks complete but model only sees recent tokens
- Including full video analyses in every follow-up message
- Not implementing conversation summarization or compression

**How to avoid:**
1. **Conversation budgeting**: Hard limit of 10 exchanges before prompting "start new conversation"
2. **Rolling window**: Keep last N messages only, summarize older ones
3. **Reference, don't repeat**: Store video analyses separately, reference by ID in conversation
4. **Clear context regularly**: Offer "reset conversation" button
5. **Static instructions at top**: Put system prompt at start, dynamic history at end
6. **Token counting**: Display approximate token count to user

**Warning signs:**
- Response latency increasing with conversation length
- API costs per conversation exceeding costs for initial analysis
- Model giving inconsistent answers about earlier videos

**Phase to address:** Phase 6 (Interactive Research) - Design context management strategy upfront

---

### Pitfall 8: Database Schema Without Indexing Strategy

**What goes wrong:**
Queries that filter by video URL, date range, or search terms take 15+ seconds because you forgot to add indexes. Or worse: you add indexes on every column, bloating storage and slowing writes.

**Why it happens:**
- Assuming PostgreSQL will "figure it out"
- Not testing with realistic data volumes
- Creating indexes after the fact without `CONCURRENTLY` (locks table)
- Missing composite indexes for common query patterns

**How to avoid:**
1. **Index WHERE/JOIN/ORDER BY columns**: video_url, created_at, user_id
2. **Composite indexes for common queries**: `(user_id, created_at DESC)` for "my recent videos"
3. **Use `CREATE INDEX CONCURRENTLY`**: Prevents table locks in production
4. **Monitor with `pg_stat_user_indexes`**: Find unused indexes for removal
5. **Partial indexes**: `WHERE status = 'completed'` if you only query completed videos

**Schema recommendation for Tikodea:**
```sql
-- Essential indexes
CREATE INDEX idx_videos_url ON videos(tiktok_url);
CREATE INDEX idx_videos_created ON videos(created_at DESC);
CREATE INDEX idx_analyses_video ON analyses(video_id);
CREATE INDEX idx_conversations_video ON conversations(video_id, created_at DESC);
```

**Warning signs:**
- Query times increasing with data volume
- Sequential scans in `EXPLAIN ANALYZE` output
- Database CPU spiking during searches

**Phase to address:** Phase 3 (Data Layer) - Define indexes with schema, not after

---

### Pitfall 9: Storing Video Files in Database

**What goes wrong:**
You store TikTok video blobs in PostgreSQL. Database size balloons, backups take hours, queries slow down, and you are paying database storage rates ($0.10/GB) instead of object storage rates ($0.023/GB).

**Why it happens:**
- Simplicity of single data store
- Not wanting to manage S3/blob storage
- Assuming small scale does not matter

**How to avoid:**
1. **Object storage for videos**: S3, Cloudflare R2 (free egress), or local filesystem
2. **Database stores metadata only**: URL to video, not video itself
3. **Consider not storing videos at all**: For personal use, re-download from TikTok if needed
4. **If caching locally**: Store in filesystem with database reference
5. **Lifecycle policies**: Auto-delete cached videos after 30 days

**Cost comparison (50 videos/week, avg 5MB each):**
- PostgreSQL: ~1GB/month = $0.10/month + backup overhead
- S3: ~1GB/month = $0.023/month
- R2: ~1GB/month = FREE (no egress charges)
- Not storing: $0

**Warning signs:**
- Database backup times increasing
- Database size growing faster than expected
- Slow queries unrelated to video content

**Phase to address:** Phase 3 (Data Layer) - Design storage strategy before building

---

### Pitfall 10: Job Queue Without Dead Letter Queue

**What goes wrong:**
A malformed TikTok URL causes your scraper to throw an error. The job retries infinitely, blocking other jobs. Or: the job fails silently and you never know videos were not processed. Or: you fix the bug but have no way to reprocess the failed jobs.

**Why it happens:**
- Not implementing retry limits
- Not distinguishing transient errors (network timeout) from permanent errors (invalid URL)
- Not storing failed jobs for later inspection
- Not implementing idempotency (reprocessing might duplicate data)

**How to avoid:**
1. **Retry with exponential backoff**: 3-5 attempts with 2^n * 1000ms delays
2. **Dead letter queue**: After max retries, move to DLQ for inspection
3. **Error classification**: Network errors = retry; validation errors = DLQ immediately
4. **BullMQ `UnrecoverableError`**: Throws directly to failed state, no retries
5. **Idempotent handlers**: Use video URL as unique key, upsert not insert
6. **DLQ monitoring**: Alert when DLQ has items, review before reprocessing

**BullMQ example:**
```typescript
// Permanent failure - skip retries
if (isValidationError(error)) {
  throw new UnrecoverableError('Invalid TikTok URL format');
}
// Transient failure - allow retry
throw error;
```

**Warning signs:**
- Jobs stuck in "active" state indefinitely
- Same video appearing multiple times in database
- No visibility into what failed and why

**Phase to address:** Phase 2 (Pipeline) - Implement DLQ from day one

---

### Pitfall 11: API Key Exposure in Repository

**What goes wrong:**
You commit `.env` file or hardcode API keys in source code. Even if you remove them later, they persist in git history. In 2025, 15% of all exposed secrets in git repos were cloud infrastructure secrets.

**Why it happens:**
- Forgetting to add `.env` to `.gitignore`
- Hardcoding keys "temporarily" for testing
- CI/CD pipelines printing environment variables in logs
- Not using separate keys for dev/prod

**How to avoid:**
1. **Add `.env` to `.gitignore` FIRST**: Before creating the file
2. **Use `.env.example`**: Template with placeholder values, committed to repo
3. **Environment separation**: Different API keys for dev, staging, production
4. **Secret scanning**: Use pre-commit hooks (gitleaks, detect-secrets)
5. **Key rotation**: Rotate keys every 90 days
6. **Backend proxy for client apps**: Never expose keys to frontend

**.gitignore must include:**
```
.env
.env.local
.env.*.local
*.pem
credentials.json
```

**Warning signs:**
- API keys visible in GitHub search
- Unexpected API charges from unknown sources
- Automated security alerts from GitHub

**Phase to address:** Phase 1 - Set up `.gitignore` before any code

---

### Pitfall 12: TikTok Terms of Service Violations

**What goes wrong:**
You build the tool, share it publicly, TikTok sends a cease-and-desist. Or: your IP gets permanently banned. For a personal tool processing 5-50 videos/week, this is unlikely, but scaling or sharing changes the risk profile.

**Why it happens:**
- TikTok's Terms of Service explicitly prohibit unauthorized scraping
- Computer Fraud and Abuse Act (CFAA) could apply to bypassing technical restrictions
- Public sharing of scraping tools draws attention
- Commercial use triggers legal review

**How to avoid:**
1. **Personal use only**: Do not commercialize or share publicly
2. **Minimal footprint**: 5-50 videos/week is invisible; 5000/day is detectable
3. **No redistribution**: Do not rehost TikTok content
4. **Use yt-dlp**: Well-established tool with large user base
5. **Consider official Research API**: If you ever want to scale/publish

**Risk assessment for Tikodea:**
- Personal use, 5-50 videos/week, single user: LOW risk
- Sharing tool publicly: MEDIUM risk
- Commercial use: HIGH risk

**Warning signs:**
- Account suspension notices
- IP bans becoming permanent
- Legal communications from TikTok/ByteDance

**Phase to address:** All phases - Stay within personal use boundaries

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Single LLM call per lens | Simpler prompt design | 4x token costs | Never - design batched prompts from start |
| Polling instead of webhook | No SSL setup | Constant server load | Development only |
| Store videos in database | Single data store | Bloated backups, slow queries | Never for video files |
| No retry logic | Faster initial development | Lost jobs, manual reprocessing | Never - implement day one |
| Full context in every message | Simpler conversation code | Cost explosion, context truncation | Never - design context management |
| Uniform frame extraction | Simpler video processing | Vision cost explosion | Only if budget allows $0.20+/video |
| No indexes | Faster initial migrations | Query degradation with scale | Only for MVP with <100 videos |
| Hardcoded configuration | Quick setup | Environment switching pain | Development only |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| TikTok + yt-dlp | Not handling rate limits | Add random delays (2-8s) between downloads |
| TikTok + Playwright | Using default browser profile | Create fresh profile per session |
| Claude API + Images | Sending full-resolution frames | Resize to 512x512 or smaller |
| Claude API + Streaming | Not handling partial responses | Accumulate chunks, handle connection drops |
| Telegram + Webhooks | Using HTTP instead of HTTPS | Always use HTTPS with valid cert |
| Telegram + Long messages | Sending 5000+ char messages | Split into multiple messages or use documents |
| PostgreSQL + JSONB | Indexing entire JSONB column | Use GIN index on specific paths |
| BullMQ + Redis | Using same Redis for cache and queue | Separate instances or namespaces |
| React + API calls | useEffect with object dependencies | Memoize dependencies or use primitive values |
| Next.js + SSR | SSR for authenticated dashboard | Use CSR with proper loading states |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| N+1 queries for analyses | Dashboard takes 10s+ to load | Eager load analyses with videos | >20 videos |
| Unbatched LLM calls | $0.50+ per video | Single batched prompt | Immediately - budget constraint |
| Full video download for transcript | 30s+ per video processing | Extract captions only first | Immediately - UX issue |
| No connection pooling | Database connection errors | Use PgBouncer or Prisma pooling | >10 concurrent requests |
| Synchronous frame extraction | Bot timeout while processing | Background job with status updates | Videos >30s |
| Unvirtualized video list | Browser freezes | react-window for long lists | >50 videos |
| Missing database vacuuming | Queries slow over time | Schedule regular VACUUM | >1000 records |

---

## "Looks Done But Isn't" Checklist

- [ ] **Scraper works**: Test with videos that have: no captions, disabled comments, private accounts, region-locked content
- [ ] **LLM handles edge cases**: Test with: empty transcripts, non-English content, very short videos (<5s)
- [ ] **Telegram bot is robust**: Test with: rapid repeated messages, very long URLs, invalid URLs, network disconnection
- [ ] **Dashboard performs**: Test with: 100+ videos loaded, rapid navigation, browser refresh mid-load
- [ ] **Error handling complete**: Verify: all API errors logged, user sees friendly messages not stack traces
- [ ] **Secrets secured**: Verify: `.env` in `.gitignore`, no keys in git history, different keys for dev/prod
- [ ] **Job queue resilient**: Test: kill worker mid-job (should recover), invalid job data (should DLQ)
- [ ] **Rate limits handled**: Test: rapid Telegram messages, API rate limit responses
- [ ] **Context managed**: Test: 20+ message conversation (should not explode costs)
- [ ] **Data persisted correctly**: Verify: database restore works, video references resolve

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| TikTok anti-bot detection | Phase 1 (Scraping) | Test scraper isolation, swap implementation |
| Vision LLM costs | Phase 2 (LLM Pipeline) | Track tokens per video, alert if >5000 |
| Prompt token costs | Phase 2 (LLM Pipeline) | Measure single vs batched prompt costs |
| Telegram webhook config | Phase 4 (Bot) | `getWebhookInfo` returns valid URL |
| Telegram rate limits | Phase 4 (Bot) | No 429 errors in logs under normal use |
| Dashboard over-engineering | Phase 5 (Dashboard) | Start with polling, measure if real-time needed |
| Chat context explosion | Phase 6 (Research) | Token count per conversation logged |
| Database indexing | Phase 3 (Data Layer) | `EXPLAIN ANALYZE` on common queries |
| Video blob storage | Phase 3 (Data Layer) | Database size remains under 100MB |
| DLQ missing | Phase 2 (Pipeline) | Failed jobs visible, reprocessable |
| API key exposure | Phase 1 (Setup) | `git log -p | grep -i "api_key"` returns nothing |
| TikTok ToS risk | All phases | Stay personal-use, <50 videos/week |

---

## Sources

### PRIMARY (HIGH confidence)
- [TikTok: How We Combat Scraping](https://www.tiktok.com/privacy/blog/how-we-combat-scraping/en) - Official TikTok anti-scraping measures
- [Scrapfly: How to Scrape TikTok 2026](https://scrapfly.io/blog/posts/how-to-scrape-tiktok-python-json) - Current scraping techniques
- [BullMQ Documentation: Retrying Failing Jobs](https://docs.bullmq.io/guide/retrying-failing-jobs) - Official retry patterns
- [BullMQ: Going to Production](https://docs.bullmq.io/guide/going-to-production) - Production best practices
- [Telegram Core: Bots FAQ](https://core.telegram.org/bots/faq) - Official rate limits
- [grammY: Flood Limits](https://grammy.dev/advanced/flood) - Telegram flood control guide
- [Claude Docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision) - Image token calculation
- [Claude Docs: Pricing](https://docs.claude.com/en/docs/about-claude/pricing) - Current API pricing

### SECONDARY (MEDIUM confidence)
- [Koombea: LLM Cost Optimization Guide](https://ai.koombea.com/blog/llm-cost-optimization) - Cost reduction strategies
- [Glukhov: Cost-Effective LLM Applications](https://www.glukhov.org/post/2025/11/cost-effective-llm-applications/) - Token optimization
- [Medium: Postgres Indexing Mistakes](https://medium.com/@ArkProtocol1/postgres-indexing-mistakes-i-see-in-every-codebase-c5d02bbcb941) - Common PostgreSQL pitfalls
- [GitGuardian: API Key Security](https://blog.gitguardian.com/secrets-api-management/) - Secrets management
- [Tilburg.ai: Context Window Management](https://tilburg.ai/2025/03/context-window-management/) - LLM context strategies
- [Hostman: Polling vs Webhook](https://hostman.com/tutorials/difference-between-polling-and-webhook-in-telegram-bots/) - Telegram bot deployment

### TERTIARY (LOW confidence - needs validation)
- [Medium: PostgreSQL Bad Schema Design](https://medium.com/@ThreadSafeDiaries/postgresql-wont-save-you-from-bad-schema-design-even-in-2025-f499334101a2) - Schema war stories
- [Medium: Dead Letter Queues](https://medium.com/@vinay.georgiatech/dead-letter-queues-and-retry-queues-the-safety-net-for-distributed-systems-b961c718e6a0) - DLQ patterns
- Cloudflare self-DDoS incident via useEffect (reported in SDxCentral) - React re-render cautionary tale
