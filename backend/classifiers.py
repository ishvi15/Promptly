"""Intent and Sentiment classification utilities."""

from typing import Tuple
import re


# Intent keywords mapping
INTENT_PATTERNS = {
    "promotional": [
        "sell", "buy", "discount", "offer", "deal", "sale", "promo", "launch",
        "product", "service", "brand", "marketing", "advertise", "campaign"
    ],
    "educational": [
        "learn", "teach", "how to", "guide", "tutorial", "explain", "understand",
        "tips", "steps", "lesson", "course", "knowledge", "skill", "training"
    ],
    "inspirational": [
        "inspire", "motivate", "dream", "achieve", "success", "believe", "hope",
        "courage", "strength", "overcome", "journey", "growth", "mindset", "goal"
    ],
    "entertaining": [
        "fun", "funny", "humor", "joke", "laugh", "meme", "entertainment",
        "game", "play", "enjoy", "relax", "comedy", "amusing", "hilarious"
    ],
    "informational": [
        "news", "update", "announce", "report", "fact", "data", "research",
        "study", "analysis", "insight", "trend", "statistics", "information"
    ]
}

# Sentiment keywords mapping
SENTIMENT_PATTERNS = {
    "positive": [
        "great", "amazing", "awesome", "excellent", "love", "happy", "joy",
        "fantastic", "wonderful", "best", "brilliant", "success", "achieve",
        "excited", "thrilled", "grateful", "blessed", "incredible", "perfect"
    ],
    "negative": [
        "bad", "terrible", "awful", "hate", "sad", "angry", "frustrated",
        "disappointed", "worst", "fail", "problem", "issue", "struggle",
        "difficult", "hard", "challenge", "pain", "stress", "worry"
    ],
    "neutral": [
        "think", "consider", "maybe", "perhaps", "could", "might", "should",
        "would", "information", "fact", "data", "report", "update", "news"
    ]
}


def predict_intent(text: str) -> str:
    """
    Classify the intent of the input text.
    
    Args:
        text: Input text to classify
        
    Returns:
        Classified intent category
    """
    text_lower = text.lower()
    scores = {}
    
    for intent, keywords in INTENT_PATTERNS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[intent] = score
    
    if max(scores.values()) == 0:
        return "informational"
    
    return max(scores, key=scores.get)


def predict_sentiment(text: str) -> str:
    """
    Analyze the sentiment of the input text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Sentiment classification (positive, negative, neutral)
    """
    text_lower = text.lower()
    scores = {"positive": 0, "negative": 0, "neutral": 0}
    
    for sentiment, keywords in SENTIMENT_PATTERNS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[sentiment] = score
    
    # If no strong signals, default to neutral
    if max(scores.values()) == 0:
        return "neutral"
    
    # Negative takes precedence if equal to positive
    if scores["negative"] >= scores["positive"] and scores["negative"] > 0:
        return "negative"
    elif scores["positive"] > scores["negative"]:
        return "positive"
    
    return "neutral"


def analyze_text(text: str) -> Tuple[str, str]:
    """
    Perform both intent and sentiment analysis.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (intent, sentiment)
    """
    intent = predict_intent(text)
    sentiment = predict_sentiment(text)
    return intent, sentiment
