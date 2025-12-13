"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Optional


class GenerateRequest(BaseModel):
    """Request model for content generation."""
    text: str = Field(..., min_length=1, description="The user's content idea or topic")
    platform: str = Field(default="General", description="Target platform for content")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Generation temperature")
    max_tokens: int = Field(default=256, ge=50, le=1024, description="Maximum tokens to generate")
    use_legacy: bool = Field(default=False, description="Use legacy API endpoint")


class GenerateResponse(BaseModel):
    """Response model for generated content."""
    content: str = Field(..., description="The generated content")
    intent: str = Field(..., description="Classified intent of the input")
    sentiment: str = Field(..., description="Sentiment analysis result")
    documents: List[str] = Field(default_factory=list, description="Retrieved reference documents")
    time_taken: float = Field(..., description="Processing time in seconds")
    fallback_used: bool = Field(default=False, description="Whether fallback was used")
    reason: Optional[str] = Field(default=None, description="Fallback reason if applicable")
