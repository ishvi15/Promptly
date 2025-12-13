"""Prompt construction utilities for content generation."""

from typing import List


# Platform-specific templates
PLATFORM_TEMPLATES = {
    "General": {
        "style": "clear, engaging, and well-structured",
        "format": "Use paragraphs with clear flow. Include an introduction, main points, and conclusion.",
        "tone": "professional yet approachable",
        "requirements": [
            "Start with a compelling opening statement",
            "Develop ideas with supporting details",
            "End with a memorable takeaway or call-to-action"
        ]
    },
    "Instagram": {
        "style": "casual, authentic, and visually descriptive",
        "format": "Short punchy sentences. Use line breaks for readability. Include 3-5 relevant hashtags at the end.",
        "tone": "friendly, relatable, and engaging",
        "requirements": [
            "Start with a scroll-stopping hook",
            "Tell a micro-story or share a relatable moment",
            "Include a clear call-to-action (save, share, comment)",
            "Use emojis strategically for visual appeal",
            "End with relevant hashtags"
        ]
    },
    "LinkedIn": {
        "style": "professional, insightful, and value-driven",
        "format": "Start with a bold statement or question. Use short paragraphs. Include bullet points for key takeaways.",
        "tone": "authoritative yet personable, thought-leadership focused",
        "requirements": [
            "Open with a hook that speaks to professional challenges",
            "Share a personal experience or industry insight",
            "Provide actionable takeaways or lessons",
            "End with a question to encourage discussion",
            "Keep it under 1300 characters for optimal engagement"
        ]
    },
    "YouTube Script": {
        "style": "conversational, energetic, and structured",
        "format": "Include [HOOK], [INTRO], [MAIN CONTENT], [OUTRO] sections. Write for spoken delivery.",
        "tone": "enthusiastic, clear, and personality-driven",
        "requirements": [
            "[HOOK]: Grab attention in first 5 seconds with a question or bold claim",
            "[INTRO]: Briefly explain what viewers will learn/gain",
            "[MAIN CONTENT]: Break into 3-5 key points with clear transitions",
            "[OUTRO]: Summarize key points, include CTA for like/subscribe/comment",
            "Write in conversational spoken language, not formal prose"
        ]
    }
}


def build_prompt(
    user_text: str,
    platform: str,
    intent: str,
    sentiment: str,
    documents: List[str],
    max_tokens: int = 256
) -> str:
    """
    Build a high-quality prompt for content generation.
    
    Args:
        user_text: User's content idea or topic
        platform: Target platform for content
        intent: Classified intent of the input
        sentiment: Sentiment analysis result
        documents: Retrieved reference documents
        max_tokens: Maximum tokens for generation
        
    Returns:
        Constructed prompt string
    """
    template = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES["General"])
    
    # Build context from retrieved documents
    context_section = "\n".join([f"- {doc}" for doc in documents])
    
    # Build requirements section
    requirements_section = "\n".join([f"• {req}" for req in template["requirements"]])
    
    prompt = f"""You are an expert content creator specializing in {platform} content.

TASK: Create {platform} content based on the following:

TOPIC/IDEA: {user_text}

DETECTED INTENT: {intent}
DETECTED SENTIMENT: {sentiment}

REFERENCE INSIGHTS:
{context_section}

PLATFORM REQUIREMENTS:
Style: {template["style"]}
Format: {template["format"]}
Tone: {template["tone"]}

SPECIFIC REQUIREMENTS:
{requirements_section}

CRITICAL RULES:
1. Create ORIGINAL, platform-optimized content
2. DO NOT use generic filler phrases
3. DO NOT mention AI or that you are an assistant
4. MUST include specific hooks, structure, and CTAs
5. Make it ready to publish immediately
6. Match the {sentiment} sentiment and {intent} intent

Generate the content now:"""

    return prompt


def get_fallback_content(
    user_text: str,
    platform: str,
    intent: str,
    sentiment: str
) -> str:
    """
    Generate fallback content when API fails.
    
    Args:
        user_text: User's content idea
        platform: Target platform
        intent: Classified intent
        sentiment: Detected sentiment
        
    Returns:
        Fallback content string
    """
    template = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES["General"])
    
    if platform == "Instagram":
        return f"""✨ {user_text.title()}

Here's something worth thinking about today...

{user_text}

The journey matters more than the destination. Every step forward counts.

💬 What's your take? Drop a comment below!

#motivation #growth #mindset #inspiration #journey"""

    elif platform == "LinkedIn":
        return f"""I've been thinking about {user_text.lower()}...

Here's what I've learned:

→ Start with curiosity
→ Embrace the learning curve
→ Share your insights with others

The best professionals aren't those who know everything—they're the ones who never stop learning.

What's been your experience with this? I'd love to hear your thoughts. 👇"""

    elif platform == "YouTube Script":
        return f"""[HOOK]
What if I told you that {user_text.lower()} could change everything?

[INTRO]
Hey everyone! Today we're diving deep into {user_text}.

[MAIN CONTENT]
Let's break this down into three key points...

Point 1: Understanding the basics
Point 2: Practical application
Point 3: Taking it to the next level

[OUTRO]
That's a wrap on today's video! If you found this helpful, smash that like button and subscribe for more content like this. Drop a comment below with your thoughts!"""

    else:
        return f"""{user_text.title()}

This topic deserves attention because it impacts how we think and act.

Key takeaways:
• Understanding leads to better decisions
• Small steps create big changes
• Sharing knowledge multiplies its value

What are your thoughts on this? Let's continue the conversation."""


