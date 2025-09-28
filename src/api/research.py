"""
Research API Endpoints
PubMed, Google Scholar, and multi-source research integration
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
from pydantic import BaseModel

from ..services.research_api import research_api
from ..services.hybrid_ai_manager import hybrid_ai_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class ResearchQuery(BaseModel):
    query: str
    sources: Optional[List[str]] = None
    max_results_per_source: int = 10
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    specialty: Optional[str] = None

class IntelligentChapterRequest(BaseModel):
    topic: str
    chapter_type: str = "disease_overview"  # disease_overview, surgical_technique, anatomy_physiology, case_study
    specialty: str = "neurosurgery"
    depth: str = "comprehensive"  # comprehensive, concise, detailed

@router.post("/search")
async def search_medical_literature(request: ResearchQuery):
    """Search multiple medical literature sources simultaneously"""

    try:
        result = await research_api.search_multiple_sources(
            query=request.query,
            sources=request.sources,
            max_results_per_source=request.max_results_per_source
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Research search failed"))

        return {
            "query": request.query,
            "results": result["results"],
            "total_count": result["total_count"],
            "sources_searched": result["sources_searched"],
            "source_breakdown": result["source_results"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Literature search failed: {e}")
        raise HTTPException(status_code=500, detail="Literature search failed")

@router.get("/pubmed/search")
async def search_pubmed(
    query: str = Query(..., description="Search query for PubMed"),
    max_results: int = Query(10, description="Maximum number of results"),
    year_from: Optional[int] = Query(None, description="Start year for publication date filter"),
    year_to: Optional[int] = Query(None, description="End year for publication date filter"),
    article_types: Optional[List[str]] = Query(None, description="Article types to filter")
):
    """Search PubMed database for medical literature"""

    try:
        result = await research_api.search_pubmed(
            query=query,
            max_results=max_results,
            year_from=year_from,
            year_to=year_to,
            article_types=article_types
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "PubMed search failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PubMed search failed: {e}")
        raise HTTPException(status_code=500, detail="PubMed search failed")

@router.get("/scholar/search")
async def search_google_scholar(
    query: str = Query(..., description="Search query for Google Scholar"),
    max_results: int = Query(10, description="Maximum number of results"),
    year_from: Optional[int] = Query(None, description="Start year for publication date filter"),
    year_to: Optional[int] = Query(None, description="End year for publication date filter")
):
    """Search Google Scholar for academic literature"""

    try:
        result = await research_api.search_google_scholar(
            query=query,
            max_results=max_results,
            year_from=year_from,
            year_to=year_to
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Google Scholar search failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google Scholar search failed: {e}")
        raise HTTPException(status_code=500, detail="Google Scholar search failed")

@router.get("/article/{pmid}")
async def get_article_details(pmid: str):
    """Get detailed information about a specific PubMed article"""

    try:
        result = await research_api.get_article_details(pmid)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Article not found"))

        return result["article"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get article details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get article details")

@router.post("/intelligent-chapter")
async def generate_intelligent_chapter(request: IntelligentChapterRequest):
    """Generate comprehensive medical chapter using AI orchestration"""

    try:
        logger.info(f"🎯 Starting intelligent chapter generation for: {request.topic}")

        result = await hybrid_ai_manager.generate_intelligent_chapter(
            topic=request.topic,
            chapter_type=request.chapter_type,
            specialty=request.specialty,
            depth=request.depth
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Chapter generation failed"))

        return {
            "message": "Intelligent chapter generated successfully",
            "chapter": result["chapter"],
            "metadata": result["metadata"],
            "generation_details": {
                "ai_orchestration": "Multi-provider specialized AI system",
                "research_integration": f"{result['metadata']['research_sources']} sources analyzed",
                "evidence_quality": f"{result['metadata']['evidence_quality']:.1%} average score",
                "providers_used": result["metadata"]["ai_providers_used"],
                "estimated_cost": f"${result['metadata']['cost_estimate']:.2f}"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intelligent chapter generation failed: {e}")
        raise HTTPException(status_code=500, detail="Chapter generation failed")

@router.get("/sources/available")
async def get_available_research_sources():
    """Get available research sources and their capabilities"""

    try:
        return research_api.get_available_sources()

    except Exception as e:
        logger.error(f"Failed to get available sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available sources")

@router.get("/analytics/usage")
async def get_ai_usage_analytics():
    """Get AI usage analytics for cost optimization"""

    try:
        return hybrid_ai_manager.get_usage_analytics()

    except Exception as e:
        logger.error(f"Failed to get usage analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage analytics")

@router.get("/chapter-types")
async def get_chapter_types():
    """Get available chapter types and their characteristics"""

    return {
        "chapter_types": [
            {
                "value": "disease_overview",
                "label": "Disease Overview",
                "description": "Comprehensive overview of a medical condition",
                "sections": [
                    "Executive Summary", "Epidemiology", "Pathophysiology",
                    "Clinical Presentation", "Diagnostic Workup", "Treatment Options",
                    "Surgical Considerations", "Complications", "Prognosis"
                ],
                "estimated_length": "5,000 words",
                "ai_specialization": "Gemini for research, Claude for structure, Perplexity for current guidelines"
            },
            {
                "value": "surgical_technique",
                "label": "Surgical Technique",
                "description": "Detailed surgical procedure description",
                "sections": [
                    "Executive Summary", "Introduction", "Indications",
                    "Preoperative Planning", "Surgical Technique", "Postoperative Care",
                    "Complications", "Outcomes", "Pearls and Pitfalls"
                ],
                "estimated_length": "4,000 words",
                "ai_specialization": "Gemini for evidence, Claude for technical writing, Perplexity for visuals"
            },
            {
                "value": "anatomy_physiology",
                "label": "Anatomy & Physiology",
                "description": "Anatomical and physiological description",
                "sections": [
                    "Executive Summary", "Anatomical Overview", "Microanatomy",
                    "Physiological Function", "Development", "Clinical Correlations",
                    "Surgical Anatomy", "Imaging", "Clinical Applications"
                ],
                "estimated_length": "3,500 words",
                "ai_specialization": "Gemini for complex analysis, Perplexity for visual integration"
            },
            {
                "value": "case_study",
                "label": "Case Study",
                "description": "Clinical case presentation and analysis",
                "sections": [
                    "Executive Summary", "Case Presentation", "Clinical History",
                    "Examination", "Diagnostic Workup", "Differential Diagnosis",
                    "Management", "Surgical Intervention", "Follow-up", "Discussion"
                ],
                "estimated_length": "3,000 words",
                "ai_specialization": "Claude for clinical narrative, Gemini for evidence analysis"
            }
        ],
        "depth_options": [
            {
                "value": "comprehensive",
                "label": "Comprehensive",
                "description": "Detailed, in-depth coverage suitable for reference",
                "word_count_range": "4,000-6,000 words"
            },
            {
                "value": "concise",
                "label": "Concise",
                "description": "Essential information in condensed format",
                "word_count_range": "1,500-2,500 words"
            },
            {
                "value": "detailed",
                "label": "Detailed",
                "description": "Thorough coverage with technical details",
                "word_count_range": "3,000-4,500 words"
            }
        ],
        "specialties": [
            "neurosurgery", "cardiology", "oncology", "neurology",
            "radiology", "pathology", "internal_medicine", "surgery",
            "pediatrics", "psychiatry", "emergency_medicine", "anesthesiology"
        ]
    }