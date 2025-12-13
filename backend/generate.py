"""AI Generation Client with Groq → Ollama → Local fallback chain."""

import os
import asyncio
import json
import random
import httpx
from typing import Optional, Tuple
from dotenv import load_dotenv

from constants import (
    GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL,
    OLLAMA_BASE_URL, OLLAMA_MODEL, PROVIDER_CHAIN,
    DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS, MAX_RETRIES, RETRY_DELAY
)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)


async def generate_response(
    prompt: str,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    use_legacy: bool = False
) -> Tuple[str, bool, Optional[str]]:
    """
    Generate response using the provider chain: Groq → Ollama → Local.
    
    Args:
        prompt: The prompt to generate content for
        temperature: Generation creativity (0.1-1.0)
        max_tokens: Maximum response length
        use_legacy: Ignored (for compatibility)
        
    Returns:
        Tuple of (content, fallback_used, error_reason)
    """
    
    last_error = None
    
    # Try providers in order: Groq → Ollama → Local
    for provider in PROVIDER_CHAIN:
        try:
            if provider == "groq":
                content = await try_groq_api(prompt, temperature, max_tokens)
                if content:
                    return content, False, None  # Success, no fallback used
            
            elif provider == "ollama":
                content = await try_ollama_api(prompt, temperature, max_tokens)
                if content:
                    return content, False, None  # Success, no fallback used
            
            elif provider == "local":
                content = generate_local_response(prompt, temperature, max_tokens)
                if content:
                    return content, True, "Used local fallback after providers failed"  # Local fallback used
                    
        except Exception as e:
            last_error = str(e)
            print(f"Provider {provider} failed: {last_error}")
            continue
    
    # If all providers failed, return empty with error
    return "", True, f"All providers failed. Last error: {last_error}"


async def try_groq_api(
    prompt: str,
    temperature: float,
    max_tokens: int
) -> Optional[str]:
    """
    Attempt to generate content using Groq API (primary provider).
    Uses the provided API key for llama-3.1-70b-versatile model.
    """
    
    if not GROQ_API_KEY:
        raise Exception("Groq API key not configured")
    
    url = f"{GROQ_BASE_URL}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": max(temperature, 0.1),
        "max_tokens": max_tokens,
        "top_p": 0.9,
        "stream": False
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content and content.strip():
                        return content.strip()
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                else:
                    raise Exception(f"Groq API error: {response.status_code} - {response.text}")
                    
        except httpx.TimeoutException:
            if attempt == MAX_RETRIES - 1:
                raise Exception("Groq API timeout")
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            continue
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise e
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            continue
    
    return None


async def try_ollama_api(
    prompt: str,
    temperature: float,
    max_tokens: int
) -> Optional[str]:
    """
    Attempt to generate content using Ollama local API (secondary provider).
    Assumes Ollama is running locally with llama3 model.
    """
    
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": max(temperature, 0.1),
            "num_predict": max_tokens,
            "top_p": 0.9
        }
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("response", "")
                    if content and content.strip():
                        return content.strip()
                else:
                    raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                    
        except httpx.TimeoutException:
            if attempt == MAX_RETRIES - 1:
                raise Exception("Ollama API timeout")
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            continue
        except httpx.ConnectError:
            # Ollama not running, this is expected
            raise Exception("Ollama server not running")
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise e
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            continue
    
    return None


def generate_local_response(
    prompt: str,
    temperature: float,
    max_tokens: int
) -> str:
    """
    Generate content using intelligent local pattern matching (last resort).
    This provides high-quality, contextual responses without external dependencies.
    """
    
    # Analyze prompt for context and intent
    analysis = analyze_prompt_context(prompt)
    
    # Generate content based on analysis
    content = generate_contextual_content(prompt, analysis, max_tokens)
    
    return content


def analyze_prompt_context(prompt: str) -> dict:
    """Analyze prompt to understand context, intent, and generate appropriate content."""
    
    prompt_lower = prompt.lower()
    
    analysis = {
        "content_type": "general",
        "intent": "informational",
        "platform": "general",
        "style": "professional",
        "tone": "neutral",
        "keywords": extract_keywords(prompt_lower),
        "question_type": identify_question_type(prompt_lower),
        "complexity": assess_complexity(prompt),
        "audience": "general"
    }
    
    # Determine content type and platform
    if any(word in prompt_lower for word in ["instagram", "ig", "story", "post", "feed", "photo"]):
        analysis["content_type"] = "social"
        analysis["platform"] = "instagram"
        analysis["style"] = "visual"
        analysis["tone"] = "enthusiastic"
    elif any(word in prompt_lower for word in ["linkedin", "professional", "career", "business", "workplace", "networking"]):
        analysis["content_type"] = "professional"
        analysis["platform"] = "linkedin"
        analysis["style"] = "formal"
        analysis["tone"] = "thoughtful"
    elif any(word in prompt_lower for word in ["youtube", "video", "script", "tutorial", "vlog"]):
        analysis["content_type"] = "video"
        analysis["platform"] = "youtube"
        analysis["style"] = "conversational"
        analysis["tone"] = "engaging"
    elif any(word in prompt_lower for word in ["twitter", "tweet", "thread"]):
        analysis["content_type"] = "social"
        analysis["platform"] = "twitter"
        analysis["style"] = "concise"
        analysis["tone"] = "witty"
    
    # Determine intent
    if any(word in prompt_lower for word in ["how to", "guide", "tutorial", "steps"]):
        analysis["intent"] = "instructional"
    elif any(word in prompt_lower for word in ["idea", "suggestion", "recommend"]):
        analysis["intent"] = "creative"
    elif any(word in prompt_lower for word in ["explain", "what is", "define"]):
        analysis["intent"] = "educational"
    
    return analysis


def extract_keywords(text: str) -> list:
    """Extract relevant keywords from the prompt."""
    
    keywords = []
    keyword_patterns = {
        "business": ["business", "company", "startup", "entrepreneur", "profit"],
        "technology": ["tech", "software", "app", "digital", "ai", "coding"],
        "lifestyle": ["life", "health", "fitness", "wellness", "mindfulness"],
        "creative": ["art", "design", "creative", "music", "writing", "photography"],
        "education": ["learn", "study", "education", "skill", "knowledge", "course"],
        "personal": ["personal", "life", "family", "relationship", "self"]
    }
    
    for category, words in keyword_patterns.items():
        if any(word in text for word in words):
            keywords.append(category)
    
    return keywords


def identify_question_type(text: str) -> str:
    """Identify the type of question or request."""
    
    if any(phrase in text for phrase in ["how to", "step by step", "tutorial"]):
        return "how_to"
    elif any(phrase in text for phrase in ["what is", "define", "explain"]):
        return "what_is"
    elif any(phrase in text for phrase in ["why", "reason", "because"]):
        return "why"
    elif any(phrase in text for phrase in ["when", "time", "schedule"]):
        return "when"
    elif any(phrase in text for phrase in ["where", "location", "place"]):
        return "where"
    else:
        return "general"


def assess_complexity(prompt: str) -> str:
    """Assess the complexity level of the request."""
    
    word_count = len(prompt.split())
    
    if word_count < 10:
        return "simple"
    elif word_count < 25:
        return "moderate"
    else:
        return "complex"


def generate_contextual_content(prompt: str, analysis: dict, max_tokens: int) -> str:
    """Generate content based on comprehensive prompt analysis."""
    
    # Platform-specific content generation
    if analysis["platform"] == "instagram":
        return generate_instagram_content(prompt, analysis, max_tokens)
    elif analysis["platform"] == "linkedin":
        return generate_linkedin_content(prompt, analysis, max_tokens)
    elif analysis["platform"] == "youtube":
        return generate_youtube_content(prompt, analysis, max_tokens)
    elif analysis["platform"] == "twitter":
        return generate_twitter_content(prompt, analysis, max_tokens)
    else:
        return generate_general_content(prompt, analysis, max_tokens)


def generate_instagram_content(prompt: str, analysis: dict, max_tokens: int) -> str:
    """Generate Instagram-optimized content."""
    
    templates = {
        "visual": [
            "✨ {content}\n\n📸 Perfect shot! What do you think? 👇",
            "🌟 {content}\n\nDouble tap if you agree! 💯",
            "💫 {content}\n\nSave this for later! 📌"
        ],
        "enthusiastic": [
            "🚀 {content}\n\nTag someone who needs to see this! 👥",
            "🔥 {content}\n\nShare your thoughts below! 💬",
            "⭐ {content}\n\nWhich part resonates with you? 🤔"
        ]
    }
    
    style = analysis.get("style", "visual")
    template = random.choice(templates.get(style, templates["visual"]))
    
    specific_content = generate_specific_content(prompt, "instagram", max_tokens - 50)
    
    return template.format(content=specific_content)


def generate_linkedin_content(prompt: str, analysis: dict, max_tokens: int) -> str:
    """Generate LinkedIn-optimized professional content."""
    
    templates = [
        "💼 {content}\n\nWhat are your thoughts on this? I'd love to hear your perspective in the comments.\n\n#ProfessionalGrowth #Leadership #Business",
        "🚀 {content}\n\nKey takeaways:\n• {takeaway1}\n• {takeaway2}\n• {takeaway3}\n\nWhat's been your experience with this? Share below! 👇",
        "📈 {content}\n\nThis reminds me of the importance of continuous learning and adaptation in today's fast-paced business environment.\n\nWhat strategies have worked best for you?"
    ]
    
    template = random.choice(templates)
    specific_content = generate_specific_content(prompt, "linkedin", max_tokens - 80)
    takeaways = generate_takeaways(prompt, analysis)
    
    return template.format(
        content=specific_content,
        takeaway1=takeaways[0] if len(takeaways) > 0 else "Strategic thinking drives results",
        takeaway2=takeaways[1] if len(takeaways) > 1 else "Consistency builds trust",
        takeaway3=takeaways[2] if len(takeaways) > 2 else "Innovation creates opportunities"
    )


def generate_youtube_content(prompt: str, analysis: dict, max_tokens: int) -> str:
    """Generate YouTube video script content."""
    
    templates = [
        "🎬 YouTube Script: {topic}\n\n🎯 Introduction:\nWelcome back to the channel! Today we're diving into {content}\n\n📝 Main Points:\n• {point1}\n• {point2}\n• {point3}\n\n🎯 Call to Action:\nDon't forget to like, subscribe, and hit the notification bell!",
        "🔥 In this video: {content}\n\n⏰ Timestamps:\n00:00 - Introduction\n01:30 - Main content\n04:00 - Key takeaways\n05:30 - Conclusion\n\n💬 Let me know in the comments what you'd like to see next!"
    ]
    
    template = random.choice(templates)
    points = generate_video_points(prompt, analysis)
    
    return template.format(
        topic=prompt[:50],
        content=generate_specific_content(prompt, "youtube", max_tokens - 60),
        point1=points[0] if len(points) > 0 else "Understanding the fundamentals",
        point2=points[1] if len(points) > 1 else "Practical application",
        point3=points[2] if len(points) > 2 else "Advanced techniques"
    )


def generate_twitter_content(prompt: str, analysis: dict, max_tokens: int) -> str:
    """Generate Twitter-optimized concise content."""
    
    templates = [
        "🧵 Thread: {content}\n\n1/{line1}\n\n2/{line2}\n\n3/{line3}\n\nRT if this resonates! 🔄",
        "💡 Quick insight: {content}\n\nSometimes the simplest approach is the most effective. What's your experience with this? 👇",
        "🎯 {content}\n\nKey principle: {principle}\n\nWhat's your take on this?"
    ]
    
    template = random.choice(templates)
    
    return template.format(
        content=generate_specific_content(prompt, "twitter", 200),
        line1="Understanding the core concept",
        line2="Practical implementation",
        line3="Long-term benefits",
        principle="Consistency beats perfection"
    )


def generate_general_content(prompt: str, analysis: dict, max_tokens: int) -> str:
    """Generate general-purpose content."""
    
    templates = [
        "Here's some thoughtful content about '{topic}':\n\n{content}\n\nI hope this provides value and sparks some interesting discussions!",
        "Regarding '{topic}', here's what I think:\n\n{content}\n\nWhat are your thoughts on this approach?",
        "Content idea for '{topic}':\n\n{content}\n\nFeel free to adapt this to your specific needs and style!"
    ]
    
    template = random.choice(templates)
    specific_content = generate_specific_content(prompt, "general", max_tokens)
    
    return template.format(
        topic=prompt[:30],
        content=specific_content
    )


def generate_specific_content(prompt: str, content_type: str, max_tokens: int) -> str:
    """Generate specific content based on prompt and type."""
    
    prompt_lower = prompt.lower()
    clean_prompt = clean_prompt_text(prompt)
    
    if content_type == "instagram":
        return generate_instagram_specific(clean_prompt, prompt_lower)
    elif content_type == "linkedin":
        return generate_linkedin_specific(clean_prompt, prompt_lower)
    elif content_type == "youtube":
        return generate_youtube_specific(clean_prompt, prompt_lower)
    elif content_type == "twitter":
        return generate_twitter_specific(clean_prompt, prompt_lower)
    else:
        return generate_general_specific(clean_prompt, prompt_lower)


def clean_prompt_text(prompt: str) -> str:
    """Clean and normalize prompt text."""
    
    cleaned = prompt.lower()
    cleaned = cleaned.replace("how to", "").replace("what is", "").replace("tell me", "")
    cleaned = cleaned.replace("help me", "").replace("give me", "").replace("show me", "")
    cleaned = cleaned.strip()
    
    return cleaned


def generate_instagram_specific(clean_prompt: str, original: str) -> str:
    """Generate Instagram-specific content."""
    
    if any(word in original for word in ["food", "recipe", "cooking", "meal"]):
        return "🍽️ Absolutely delicious! This recipe looks amazing and perfect for sharing your culinary journey. The colors and presentation are on point! 📸✨ #foodie #cooking #yummy #homemade"
    
    elif any(word in original for word in ["travel", "vacation", "trip", "adventure"]):
        return "✈️ Wanderlust captured perfectly! This destination looks absolutely incredible. The scenery and vibes are everything! 🌍📸 Perfect for inspiring your next adventure! #travel #wanderlust #adventure #explore"
    
    elif any(word in original for word in ["fitness", "workout", "gym", "exercise"]):
        return "💪 Strong and determined! This workout routine is perfect for reaching your fitness goals. Consistency is key! 🔥💯 #fitness #workout #motivation #strong"
    
    elif any(word in original for word in ["business", "entrepreneur", "startup"]):
        return "🚀 Building something amazing! Every step forward in entrepreneurship counts. Keep pushing towards your dreams! 💼✨ #entrepreneur #business #startup #hustle"
    
    else:
        return f"✨ Beautiful moment captured! This content is perfect for your Instagram feed and has great engagement potential. The composition and energy are spot on! 💫📸"


def generate_linkedin_specific(clean_prompt: str, original: str) -> str:
    """Generate LinkedIn-specific professional content."""
    
    return f"""I recently reflected on '{clean_prompt[:50]}...' and wanted to share some insights with this amazing network.

Key observations:
• Strategic thinking and planning are crucial for long-term success
• Continuous learning and adaptation drive professional growth
• Building strong relationships amplifies individual capabilities
• Innovation often comes from challenging conventional approaches

In today's rapidly evolving business landscape, those who embrace change and continuously develop their skills tend to outperform their peers. What strategies have worked best for you in navigating complex challenges?

I'd love to hear different perspectives from this community. Please share your thoughts and experiences below! 👇

#ProfessionalDevelopment #Leadership #BusinessStrategy #GrowthMindset"""


def generate_youtube_specific(clean_prompt: str, original: str) -> str:
    """Generate YouTube-specific content."""
    
    return f"""🎬 Hey everyone! Today we're diving into '{clean_prompt[:50]}...'

In this comprehensive guide, you'll learn:

✅ Step-by-step breakdown of the fundamentals
✅ Pro tips and advanced techniques
✅ Common mistakes to avoid
✅ Real-world applications and examples

Whether you're just starting out or looking to level up your skills, this video has something valuable for everyone.

💡 Don't forget to hit that like button if this content helps you, and subscribe for more tutorials like this!

🎯 Drop a comment below and let me know:
• What's your biggest challenge with this topic?
• What would you like me to cover next?

Your feedback helps me create better content for you!"""


def generate_twitter_specific(clean_prompt: str, original: str) -> str:
    """Generate Twitter-specific concise content."""
    
    return f"💡 Quick insight about '{clean_prompt[:40]}...': Sometimes the most effective approach is also the simplest. Focus on fundamentals, build consistency, and results will follow. What's your experience with this? 👇"


def generate_general_specific(clean_prompt: str, original: str) -> str:
    """Generate general-purpose content."""
    
    return f"""Here's a comprehensive take on '{clean_prompt[:50]}...':

• Breaking down complex concepts into digestible parts
• Providing practical, actionable insights
• Focusing on real-world applications and examples
• Emphasizing the importance of continuous improvement

This approach has proven effective across various domains and can be adapted to suit different contexts and goals. The key is to start with a solid foundation and build upon it systematically.

Remember: Progress, not perfection, is what leads to meaningful results. 🌟"""


def generate_takeaways(prompt: str, analysis: dict) -> list:
    """Generate key takeaways based on prompt analysis."""
    
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ["business", "entrepreneur", "startup"]):
        return [
            "Strategic planning drives sustainable growth",
            "Customer focus is paramount for success",
            "Adaptability is crucial in dynamic markets"
        ]
    elif any(word in prompt_lower for word in ["technology", "software", "ai"]):
        return [
            "Continuous learning keeps skills relevant",
            "User experience should guide development",
            "Security and scalability must be priorities"
        ]
    else:
        return [
            "Understanding fundamentals builds strong foundation",
            "Consistent practice leads to mastery",
            "Adaptation and learning drive progress"
        ]


def generate_video_points(prompt: str, analysis: dict) -> list:
    """Generate video script points."""
    
    return [
        "Setting clear objectives and expectations",
        "Providing step-by-step guidance and examples",
        "Encouraging interaction and community building"
    ]


async def check_provider_status() -> dict:
    """Check the status of all providers."""
    
    status = {
        "groq": False,
        "ollama": False,
        "local": True  # Local is always available
    }
    
    # Check Groq
    try:
        test_content = await try_groq_api("Hello", 0.7, 10)
        status["groq"] = bool(test_content)
    except Exception:
        status["groq"] = False
    
    # Check Ollama
    try:
        test_content = await try_ollama_api("Hello", 0.7, 10)
        status["ollama"] = bool(test_content)
    except Exception:
        status["ollama"] = False
    
    return status
