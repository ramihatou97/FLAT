"""
Content Integration API Endpoints
=================================

API endpoints for integrating content from both API calls and web interface extractions.
Ensures uniform content processing regardless of source method.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional, Dict, Any
import logging
from pydantic import BaseModel
from enum import Enum
import json

from ..services.content_integration_service import (
    content_integration_service,
    ContentType,
    ContentSource,
    IntegratedContent
)

logger = logging.getLogger(__name__)
router = APIRouter()

class WebContentImport(BaseModel):
    """Model for importing content from web interfaces"""
    content: str
    provider: str  # gemini, claude, openai, perplexity
    source_interface: str  # ai_studio, claude_ai, chatgpt, perplexity
    content_type: ContentType
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    features_used: Optional[List[str]] = []
    conversation_context: Optional[str] = None

class BatchContentImport(BaseModel):
    """Model for batch content import"""
    content_items: List[WebContentImport]

class ContentSearchRequest(BaseModel):
    """Model for content search requests"""
    query: str
    content_type: Optional[ContentType] = None
    provider: Optional[str] = None
    source: Optional[ContentSource] = None
    max_results: int = 20

@router.post("/import/web-content")
async def import_web_content(request: WebContentImport):
    """
    Import content extracted from AI provider web interfaces

    This endpoint allows users to import content they've generated using:
    - Gemini AI Studio (with Deep Search & Deep Think)
    - Claude.ai (with extended reasoning)
    - ChatGPT (with Code Interpreter, DALL-E, etc.)
    - Perplexity (with real-time search)

    The content is processed and integrated with the same standards as API content.
    """
    try:
        logger.info(f"🔄 Importing web content from {request.provider} via {request.source_interface}")

        # Enhance metadata with web-specific information
        enhanced_metadata = request.metadata.copy()
        enhanced_metadata.update({
            "import_source": "web_interface",
            "source_interface": request.source_interface,
            "features_used": request.features_used,
            "conversation_context": request.conversation_context,
            "manual_extraction": True
        })

        # Integrate the content
        integrated_content = await content_integration_service.integrate_web_content(
            content=request.content,
            provider=request.provider,
            source_interface=request.source_interface,
            metadata=enhanced_metadata,
            content_type=request.content_type
        )

        return {
            "success": True,
            "message": f"Content imported and integrated from {request.provider}",
            "content_id": integrated_content.id,
            "integration_details": {
                "medical_concepts_found": len(integrated_content.medical_concepts),
                "confidence_score": integrated_content.confidence_score,
                "content_type": integrated_content.content_type,
                "tags": integrated_content.tags,
                "references_count": len(integrated_content.references)
            },
            "content": integrated_content.dict()
        }

    except Exception as e:
        logger.error(f"Web content import failed: {e}")
        raise HTTPException(status_code=500, detail=f"Content import failed: {str(e)}")

@router.post("/import/batch")
async def batch_import_content(request: BatchContentImport):
    """
    Batch import multiple content items from various sources

    Useful for importing entire conversation histories or multiple
    research outputs from different AI providers.
    """
    try:
        logger.info(f"📦 Batch importing {len(request.content_items)} content items")

        # Convert to integration format
        content_items = []
        for item in request.content_items:
            content_items.append({
                "content": item.content,
                "provider": item.provider,
                "source_interface": item.source_interface,
                "content_type": item.content_type.value,
                "metadata": {
                    **item.metadata,
                    "title": item.title,
                    "features_used": item.features_used,
                    "conversation_context": item.conversation_context
                },
                "extraction_method": "web"
            })

        # Batch integrate
        integrated_items = await content_integration_service.batch_integrate_content(content_items)

        return {
            "success": True,
            "message": f"Batch imported {len(integrated_items)} content items",
            "imported_count": len(integrated_items),
            "failed_count": len(request.content_items) - len(integrated_items),
            "content_ids": [item.id for item in integrated_items],
            "summary": {
                "total_medical_concepts": sum(len(item.medical_concepts) for item in integrated_items),
                "average_confidence": sum(item.confidence_score for item in integrated_items) / len(integrated_items) if integrated_items else 0,
                "content_types": list(set(item.content_type for item in integrated_items)),
                "providers": list(set(item.provider for item in integrated_items))
            }
        }

    except Exception as e:
        logger.error(f"Batch content import failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch import failed: {str(e)}")

@router.post("/import/file")
async def import_content_file(
    file: UploadFile = File(...),
    provider: str = Form(...),
    content_type: ContentType = Form(...),
    source_interface: str = Form(...)
):
    """
    Import content from files (e.g., exported conversations, saved responses)

    Supports various file formats:
    - JSON (exported conversations)
    - TXT (plain text content)
    - MD (markdown content)
    """
    try:
        logger.info(f"📁 Importing content file: {file.filename}")

        # Read file content
        content_bytes = await file.read()

        if file.filename.endswith('.json'):
            # Parse JSON content
            try:
                data = json.loads(content_bytes.decode('utf-8'))
                content = data.get('content', str(data))
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON file format")
        else:
            # Plain text content
            content = content_bytes.decode('utf-8')

        # Import the content
        import_request = WebContentImport(
            content=content,
            provider=provider,
            source_interface=source_interface,
            content_type=content_type,
            title=file.filename,
            metadata={
                "file_name": file.filename,
                "file_size": len(content_bytes),
                "import_method": "file_upload"
            }
        )

        # Use the existing import function
        result = await import_web_content(import_request)

        return {
            **result,
            "file_info": {
                "filename": file.filename,
                "size_bytes": len(content_bytes),
                "content_type": file.content_type
            }
        }

    except Exception as e:
        logger.error(f"File import failed: {e}")
        raise HTTPException(status_code=500, detail=f"File import failed: {str(e)}")

@router.post("/search")
async def search_integrated_content(request: ContentSearchRequest):
    """
    Search through all integrated content using semantic similarity

    Searches across content from both API integrations and web imports
    with unified ranking and filtering.
    """
    try:
        logger.info(f"🔍 Searching integrated content: '{request.query}'")

        # Perform semantic search
        results = await content_integration_service.search_integrated_content(
            query=request.query,
            content_type=request.content_type,
            provider=request.provider,
            source=request.source,
            max_results=request.max_results
        )

        return {
            "success": True,
            "query": request.query,
            "results_count": len(results),
            "results": [
                {
                    "id": result.id,
                    "title": result.title,
                    "content_preview": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                    "provider": result.provider,
                    "source": result.source,
                    "content_type": result.content_type,
                    "confidence_score": result.confidence_score,
                    "medical_concepts": result.medical_concepts[:10],  # First 10 concepts
                    "tags": result.tags,
                    "created_at": result.created_at,
                    "metadata": {
                        key: value for key, value in result.metadata.items()
                        if key in ["source_interface", "features_used", "extraction_method"]
                    }
                }
                for result in results
            ],
            "search_metadata": {
                "providers_found": list(set(r.provider for r in results)),
                "content_types_found": list(set(r.content_type for r in results)),
                "sources_found": list(set(r.source for r in results))
            }
        }

    except Exception as e:
        logger.error(f"Content search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/content/{content_id}")
async def get_content_details(content_id: str):
    """Get detailed information about a specific integrated content item"""
    try:
        # Retrieve content from service
        content = content_integration_service.content_store.get(content_id)

        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        return {
            "success": True,
            "content": content.dict(),
            "analysis": {
                "word_count": len(content.content.split()),
                "medical_concept_count": len(content.medical_concepts),
                "reference_count": len(content.references),
                "tag_count": len(content.tags),
                "confidence_level": "high" if content.confidence_score > 0.8 else "medium" if content.confidence_score > 0.6 else "low"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve content {content_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve content")

@router.post("/merge-similar")
async def merge_similar_content(similarity_threshold: float = 0.9):
    """
    Identify and merge similar content from different sources

    Useful for consolidating related information extracted from
    multiple AI providers or interfaces.
    """
    try:
        logger.info(f"🔄 Merging similar content (threshold: {similarity_threshold})")

        merged_items = await content_integration_service.merge_similar_content(
            similarity_threshold=similarity_threshold
        )

        return {
            "success": True,
            "merged_items_count": len(merged_items),
            "similarity_threshold": similarity_threshold,
            "merged_items": merged_items[:10],  # Return first 10 for preview
            "summary": {
                "total_items_processed": len(merged_items),
                "consolidation_ratio": f"{len(merged_items)} items from original content"
            }
        }

    except Exception as e:
        logger.error(f"Content merging failed: {e}")
        raise HTTPException(status_code=500, detail=f"Merging failed: {str(e)}")

@router.get("/export")
async def export_content(
    format_type: str = "json",
    provider: Optional[str] = None,
    content_type: Optional[ContentType] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Export integrated content in various formats

    Supports JSON, Markdown, and CSV formats for different use cases.
    """
    try:
        logger.info(f"📤 Exporting content in {format_type} format")

        # Build filter criteria
        filter_criteria = {}
        if provider:
            filter_criteria["provider"] = provider
        if content_type:
            filter_criteria["content_type"] = content_type
        if date_from:
            filter_criteria["date_from"] = date_from
        if date_to:
            filter_criteria["date_to"] = date_to

        # Export content
        exported_content = await content_integration_service.export_integrated_content(
            format_type=format_type,
            filter_criteria=filter_criteria
        )

        return {
            "success": True,
            "format": format_type,
            "filter_criteria": filter_criteria,
            "content": exported_content,
            "export_info": {
                "generated_at": "datetime.utcnow().isoformat()",
                "content_length": len(exported_content),
                "format_type": format_type
            }
        }

    except Exception as e:
        logger.error(f"Content export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/statistics")
async def get_integration_statistics():
    """Get statistics about integrated content"""
    try:
        all_content = list(content_integration_service.content_store.values())

        if not all_content:
            return {
                "success": True,
                "message": "No content has been integrated yet",
                "statistics": {
                    "total_items": 0,
                    "by_provider": {},
                    "by_source": {},
                    "by_content_type": {}
                }
            }

        # Calculate statistics
        stats = {
            "total_items": len(all_content),
            "by_provider": {},
            "by_source": {},
            "by_content_type": {},
            "by_extraction_method": {},
            "average_confidence": sum(c.confidence_score for c in all_content) / len(all_content),
            "total_medical_concepts": sum(len(c.medical_concepts) for c in all_content),
            "total_references": sum(len(c.references) for c in all_content)
        }

        # Count by categories
        for content in all_content:
            # By provider
            stats["by_provider"][content.provider] = stats["by_provider"].get(content.provider, 0) + 1

            # By source
            stats["by_source"][content.source] = stats["by_source"].get(content.source, 0) + 1

            # By content type
            stats["by_content_type"][content.content_type] = stats["by_content_type"].get(content.content_type, 0) + 1

            # By extraction method
            stats["by_extraction_method"][content.extraction_method] = stats["by_extraction_method"].get(content.extraction_method, 0) + 1

        return {
            "success": True,
            "statistics": stats,
            "insights": {
                "most_used_provider": max(stats["by_provider"].items(), key=lambda x: x[1])[0] if stats["by_provider"] else None,
                "content_quality": "high" if stats["average_confidence"] > 0.8 else "medium" if stats["average_confidence"] > 0.6 else "needs_improvement",
                "integration_coverage": {
                    "api_integration": stats["by_extraction_method"].get("api", 0),
                    "web_integration": stats["by_extraction_method"].get("web_import", 0)
                }
            }
        }

    except Exception as e:
        logger.error(f"Statistics calculation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate statistics")

@router.get("/import-templates")
async def get_import_templates():
    """Get templates and examples for importing content from different providers"""

    return {
        "success": True,
        "templates": {
            "gemini_deep_search": {
                "description": "Import content from Gemini AI Studio with Deep Search",
                "example": {
                    "content": "Based on my deep search of recent neurosurgery literature, I found 15 relevant papers on glioblastoma treatment...",
                    "provider": "gemini",
                    "source_interface": "ai_studio",
                    "content_type": "research_summary",
                    "features_used": ["deep_search", "deep_think"],
                    "metadata": {
                        "search_query": "glioblastoma treatment 2024",
                        "sources_found": 15,
                        "reasoning_depth": "high"
                    }
                }
            },
            "claude_extended_reasoning": {
                "description": "Import content from Claude.ai with extended reasoning",
                "example": {
                    "content": "Let me analyze this complex medical case step by step. First, I'll examine the symptoms...",
                    "provider": "claude",
                    "source_interface": "claude_ai",
                    "content_type": "medical_analysis",
                    "features_used": ["extended_reasoning", "file_analysis"],
                    "metadata": {
                        "reasoning_steps": 5,
                        "confidence_level": "high",
                        "analysis_type": "case_study"
                    }
                }
            },
            "chatgpt_code_interpreter": {
                "description": "Import content from ChatGPT with Code Interpreter",
                "example": {
                    "content": "I've analyzed the medical data using Python. Here are the statistical results...",
                    "provider": "openai",
                    "source_interface": "chatgpt",
                    "content_type": "diagnostic_insight",
                    "features_used": ["code_interpreter", "data_analysis"],
                    "metadata": {
                        "data_processed": True,
                        "statistical_analysis": True,
                        "charts_generated": 3
                    }
                }
            },
            "perplexity_real_time": {
                "description": "Import content from Perplexity with real-time search",
                "example": {
                    "content": "According to the latest research from 2024, new findings show...",
                    "provider": "perplexity",
                    "source_interface": "perplexity_web",
                    "content_type": "research_summary",
                    "features_used": ["real_time_search", "source_citations"],
                    "metadata": {
                        "search_date": "2024-current",
                        "sources_cited": 8,
                        "real_time_data": True
                    }
                }
            }
        },
        "usage_instructions": {
            "web_interface_workflow": [
                "1. Use AI provider's web interface (AI Studio, Claude.ai, ChatGPT, Perplexity)",
                "2. Generate content using advanced features (Deep Search, Extended Reasoning, etc.)",
                "3. Copy the generated content",
                "4. Use /import/web-content endpoint to integrate into platform",
                "5. Content is automatically processed and made searchable"
            ],
            "batch_import_workflow": [
                "1. Collect multiple content items from various sources",
                "2. Format according to templates above",
                "3. Use /import/batch endpoint for efficient processing",
                "4. Review import statistics and merge similar content if needed"
            ]
        }
    }