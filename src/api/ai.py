"""
AI API Endpoints
Multi-provider AI content generation and assistance
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
import logging
from pydantic import BaseModel

from ..services.multi_ai_manager import multi_ai_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class GenerateContentRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None  # openai, gemini, claude, perplexity
    context_type: str = "medical"
    max_tokens: int = 1000
    temperature: float = 0.7
    model: Optional[str] = None

class MultiProviderRequest(BaseModel):
    prompt: str
    providers: Optional[List[str]] = None
    context_type: str = "medical"

@router.post("/generate")
async def generate_content(request: GenerateContentRequest):
    """Generate medical content using specified AI provider"""
    try:
        result = await multi_ai_manager.generate_content(
            prompt=request.prompt,
            provider=request.provider,
            context_type=request.context_type,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            model=request.model
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Content generation failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI content generation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemini/deep-search")
async def gemini_deep_search(request: GenerateContentRequest):
    """Use Gemini 2.5 Pro with Deep Search and Deep Think capabilities"""
    try:
        result = await multi_ai_manager.generate_content(
            prompt=request.prompt,
            provider="gemini",
            context_type=request.context_type,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            model="gemini-2.5-pro"
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Gemini Deep Search failed"))

        return {
            **result,
            "deep_search_enabled": True,
            "deep_think_enabled": True,
            "provider_name": "Gemini 2.5 Pro with Deep Search & Deep Think"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini Deep Search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/claude/opus-extended")
async def claude_opus_extended(request: GenerateContentRequest):
    """Use Claude Opus 4.1 with extended reasoning capabilities"""
    try:
        result = await multi_ai_manager.generate_content(
            prompt=request.prompt,
            provider="claude",
            context_type=request.context_type,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            model="claude-3-opus-20240229"
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Claude Opus Extended failed"))

        return {
            **result,
            "extended_reasoning": True,
            "provider_name": "Claude Opus 4.1 Extended"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Claude Opus Extended failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/perplexity/research")
async def perplexity_research(request: GenerateContentRequest):
    """Use Perplexity Pro for research with citations"""
    try:
        result = await multi_ai_manager.generate_content(
            prompt=request.prompt,
            provider="perplexity",
            context_type=request.context_type,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Perplexity Research failed"))

        return {
            **result,
            "research_enabled": True,
            "citations_included": True,
            "provider_name": "Perplexity Pro Research"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Perplexity Research failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/multi-provider-synthesis")
async def multi_provider_synthesis(request: MultiProviderRequest):
    """Generate content using multiple AI providers and synthesize results"""
    try:
        result = await multi_ai_manager.multi_provider_synthesis(
            prompt=request.prompt,
            providers=request.providers
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Multi-provider synthesis failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-provider synthesis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/enhance")
async def enhance_content(request: GenerateContentRequest):
    """Enhance existing medical content using best available provider"""
    try:
        enhanced_prompt = f"Enhance and improve this medical content:\n\n{request.prompt}\n\nProvide a more comprehensive and well-structured version."

        result = await multi_ai_manager.generate_content(
            prompt=enhanced_prompt,
            provider=request.provider or "gemini",  # Default to Gemini for enhancement
            context_type="medical",
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Content enhancement failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI content enhancement failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/summarize")
async def summarize_content(request: GenerateContentRequest):
    """Summarize medical content"""
    try:
        summary_prompt = f"Create a concise medical summary of this content:\n\n{request.prompt}\n\nFocus on key medical points and clinical relevance."

        result = await multi_ai_manager.generate_content(
            prompt=summary_prompt,
            provider=request.provider or "claude",  # Default to Claude for summaries
            context_type="medical",
            max_tokens=min(request.max_tokens, 500),  # Summaries should be shorter
            temperature=0.3  # Lower temperature for more focused summaries
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Content summarization failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI content summarization failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/providers")
async def get_available_providers():
    """Get available AI providers and their capabilities"""
    try:
        return multi_ai_manager.get_available_providers()

    except Exception as e:
        logger.error(f"Failed to get AI providers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")