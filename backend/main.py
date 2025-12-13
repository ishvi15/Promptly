"""FastAPI application for Promptly content generation."""

import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


from models import GenerateRequest, GenerateResponse
from classifiers import analyze_text
from retriever import retrieve_documents
from prompt_builder import build_prompt, get_fallback_content
from generate import generate_response, check_provider_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("🚀 Promptly API starting up...")
    yield
    print("👋 Promptly API shutting down...")


app = FastAPI(
    title="Promptly API",
    description="AI-powered content generation platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Promptly API", "version": "1.0.0"}



@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/providers/status")
async def provider_status():
    """Check the status of all AI providers."""
    try:
        status = await check_provider_status()
        return {
            "status": "ok",
            "providers": status,
            "primary_provider": "groq",
            "fallback_provider": "ollama",
            "local_fallback": "available"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "providers": {
                "groq": False,
                "ollama": False,
                "local": True
            }
        }


@app.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """
    Generate platform-optimized content.
    
    Pipeline:
    1. Analyze text for intent and sentiment
    2. Retrieve relevant documents
    3. Build optimized prompt
    4. Call HuggingFace model
    5. Return result with metadata
    """
    start_time = time.time()
    
    try:
        # Step 1: Analyze intent and sentiment
        intent, sentiment = analyze_text(request.text)
        
        # Step 2: Retrieve relevant documents
        documents = retrieve_documents(request.text, top_k=3)
        
        # Step 3: Build the prompt
        prompt = build_prompt(
            user_text=request.text,
            platform=request.platform,
            intent=intent,
            sentiment=sentiment,
            documents=documents,
            max_tokens=request.max_tokens
        )
        
        # Step 4: Generate content
        content, fallback_used, error_reason = await generate_response(
            prompt=prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            use_legacy=request.use_legacy
        )
        
        # Step 5: Handle fallback if needed
        if fallback_used or not content:
            content = get_fallback_content(
                user_text=request.text,
                platform=request.platform,
                intent=intent,
                sentiment=sentiment
            )
            fallback_used = True
        
        # Calculate time taken
        time_taken = round(time.time() - start_time, 2)
        
        return GenerateResponse(
            content=content,
            intent=intent,
            sentiment=sentiment,
            documents=documents,
            time_taken=time_taken,
            fallback_used=fallback_used,
            reason=error_reason
        )
        
    except Exception as e:
        # Emergency fallback
        time_taken = round(time.time() - start_time, 2)
        intent, sentiment = "informational", "neutral"
        
        fallback_content = get_fallback_content(
            user_text=request.text,
            platform=request.platform,
            intent=intent,
            sentiment=sentiment
        )
        
        return GenerateResponse(
            content=fallback_content,
            intent=intent,
            sentiment=sentiment,
            documents=[],
            time_taken=time_taken,
            fallback_used=True,
            reason=f"Internal error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
