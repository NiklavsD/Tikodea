"""LLM-powered video analysis - Phase 4 implementation."""
import json
from typing import Optional, List
import google.generativeai as genai
from config import get_settings

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.google_ai_api_key)


def get_model():
    """Get Gemini model instance."""
    return genai.GenerativeModel("gemini-2.0-flash-exp")


def analyze_video(
    transcript: Optional[str],
    title: Optional[str],
    description: Optional[str],
    hashtags: Optional[List[str]],
    context: Optional[str] = None,
) -> dict:
    """
    Run 4-lens analysis on video content.

    Returns dict with keys: investment, product, content, knowledge
    """
    model = get_model()

    # Build content context
    content_parts = []
    if title:
        content_parts.append(f"Title: {title}")
    if description:
        content_parts.append(f"Description: {description}")
    if hashtags:
        content_parts.append(f"Hashtags: {', '.join(['#' + h for h in hashtags])}")
    if transcript:
        content_parts.append(f"Transcript: {transcript}")
    if context:
        content_parts.append(f"User Context: {context}")

    content = "\n\n".join(content_parts)

    if not content.strip():
        return {
            "investment": {"error": "No content to analyze"},
            "product": {"error": "No content to analyze"},
            "content": {"error": "No content to analyze"},
            "knowledge": {"error": "No content to analyze"},
        }

    prompt = f"""Analyze this TikTok video content through 4 different lenses. Return a JSON object with exactly these keys: investment, product, content, knowledge.

VIDEO CONTENT:
{content}

ANALYSIS LENSES:

1. INVESTMENT LENS (key: "investment")
Analyze for investment/trading signals:
- traction_indicators: List of growth/momentum signals
- market_signals: Market trends or timing opportunities
- red_flags: Warning signs or risks
- opportunity_score: 1-10 rating
- summary: 2-3 sentence investment thesis

2. PRODUCT LENS (key: "product")
Analyze for product/business opportunities:
- problem_solved: What problem does this address?
- solution_approach: How is it being solved?
- recreatability: How easy to replicate (easy/medium/hard)
- market_size: Estimated market (small/medium/large)
- monetization_potential: Revenue opportunities
- summary: 2-3 sentence product opportunity

3. CONTENT LENS (key: "content")
Analyze for content creation insights:
- hook_structure: How does it grab attention?
- engagement_techniques: What keeps viewers watching?
- format_pattern: Video format/style used
- viral_indicators: Why might this spread?
- replication_tips: How to create similar content
- summary: 2-3 sentence content strategy

4. KNOWLEDGE LENS (key: "knowledge")
Extract learnings and insights:
- key_facts: Important facts or data points
- frameworks: Mental models or frameworks mentioned
- actionable_insights: What can be applied immediately
- related_topics: Connected areas to explore
- credibility_assessment: How trustworthy is this info
- summary: 2-3 sentence knowledge takeaway

Return ONLY valid JSON, no markdown formatting or code blocks."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean up potential markdown formatting
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        if text.startswith("json"):
            text = text[4:]

        return json.loads(text)
    except json.JSONDecodeError as e:
        return {
            "investment": {"error": f"JSON parse error: {e}"},
            "product": {"error": f"JSON parse error: {e}"},
            "content": {"error": f"JSON parse error: {e}"},
            "knowledge": {"error": f"JSON parse error: {e}"},
        }
    except Exception as e:
        return {
            "investment": {"error": str(e)},
            "product": {"error": str(e)},
            "content": {"error": str(e)},
            "knowledge": {"error": str(e)},
        }


def chat_with_video(video, message: str) -> str:
    """
    Chat about a specific video's content and analysis.
    """
    model = get_model()

    # Build context from video
    context_parts = [
        f"Title: {video.title}" if video.title else None,
        f"Creator: {video.creator}" if video.creator else None,
        f"Description: {video.description}" if video.description else None,
        f"Transcript: {video.transcript}" if video.transcript else None,
        f"Investment Analysis: {json.dumps(video.investment_analysis)}" if video.investment_analysis else None,
        f"Product Analysis: {json.dumps(video.product_analysis)}" if video.product_analysis else None,
        f"Content Analysis: {json.dumps(video.content_analysis)}" if video.content_analysis else None,
        f"Knowledge Analysis: {json.dumps(video.knowledge_analysis)}" if video.knowledge_analysis else None,
    ]
    context = "\n\n".join([p for p in context_parts if p])

    prompt = f"""You are a research assistant helping analyze a TikTok video. Use the video context below to answer the user's question.

VIDEO CONTEXT:
{context}

USER QUESTION: {message}

Provide a helpful, concise answer based on the video content and analysis. If the question isn't answerable from the context, say so."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating response: {e}"
