"""
Search API Endpoints
Advanced semantic search for neurosurgical medical content
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
from pydantic import BaseModel
from enum import Enum

from ..services.search_service import search_service
from ..services.semantic_search_engine import semantic_search_engine
from ..services.neurosurgical_concepts import neurosurgical_concepts, ConceptCategory

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchType(str, Enum):
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    MEDICAL_CONCEPT = "medical_concept"

class SearchRequest(BaseModel):
    query: str
    search_type: SearchType = SearchType.SEMANTIC
    specialty: Optional[str] = None
    document_type: Optional[str] = None
    document_ids: Optional[List[str]] = None
    max_results: int = 20

class ConceptExtractionRequest(BaseModel):
    text: str
    extract_synonyms: bool = True
    extract_related: bool = True

@router.post("/")
async def search_content(search_request: SearchRequest):
    """Advanced search with semantic understanding"""
    try:
        logger.info(f"🔍 Advanced search: '{search_request.query}' (type: {search_request.search_type})")

        # Use semantic search engine for advanced search types
        if search_request.search_type in [SearchType.SEMANTIC, SearchType.MEDICAL_CONCEPT]:
            results = await semantic_search_engine.search(
                query=search_request.query,
                document_ids=search_request.document_ids,
                max_results=search_request.max_results,
                search_type=search_request.search_type.value,
                specialty_filter=search_request.specialty,
                document_type_filter=search_request.document_type
            )

            # Convert search results to API format
            api_results = []
            for result in results:
                api_results.append({
                    "id": result.document_id,
                    "title": result.title,
                    "snippet": result.content_snippet,
                    "relevance_score": round(result.relevance_score, 3),
                    "concept_matches": result.concept_matches,
                    "concept_categories": result.concept_categories,
                    "semantic_similarity": round(result.semantic_similarity, 3),
                    "medical_relevance": round(result.medical_relevance, 3),
                    "document_type": result.document_type,
                    "authors": result.authors,
                    "specialty": result.specialty
                })

            return {
                "success": True,
                "results": api_results,
                "total_results": len(api_results),
                "search_type": search_request.search_type.value,
                "query": search_request.query,
                "semantic_search": True
            }

        else:
            # Fallback to traditional search for keyword searches
            result = await search_service.search_content(
                query=search_request.query,
                specialty=search_request.specialty,
                content_type=search_request.document_type,
                limit=search_request.max_results
            )

            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Search failed"))

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/suggestions")
async def get_search_suggestions(q: str = Query(..., min_length=1)):
    """Get intelligent neurosurgical search suggestions"""
    try:
        # Use semantic search engine for intelligent suggestions
        suggestions = await semantic_search_engine.get_search_suggestions(q)

        return {
            "success": True,
            "suggestions": suggestions,
            "query": q,
            "total": len(suggestions)
        }

    except Exception as e:
        logger.error(f"Search suggestions failed: {e}")
        # Fallback to traditional suggestions
        try:
            result = await search_service.get_search_suggestions(q)
            if result["success"]:
                return result
        except:
            pass

        raise HTTPException(status_code=500, detail="Failed to get search suggestions")

@router.post("/extract-concepts")
async def extract_medical_concepts(request: ConceptExtractionRequest):
    """Extract neurosurgical concepts from text"""
    try:
        logger.info(f"🧠 Extracting medical concepts from text ({len(request.text)} chars)")

        # Extract concepts using semantic search engine
        concepts = await semantic_search_engine._extract_query_concepts(request.text)

        # Format response
        extracted_concepts = []
        for concept in concepts:
            concept_data = {
                "concept": concept.concept,
                "category": concept.category.value if concept.category else None,
                "weight": concept.weight,
                "confidence": concept.confidence,
                "positions": concept.positions
            }

            if request.extract_synonyms:
                concept_data["synonyms"] = concept.synonyms

            if request.extract_related:
                concept_data["related_concepts"] = concept.related_concepts

            extracted_concepts.append(concept_data)

        # Sort by confidence and weight
        extracted_concepts.sort(key=lambda x: (x["confidence"], x["weight"]), reverse=True)

        return {
            "success": True,
            "concepts": extracted_concepts,
            "total_concepts": len(extracted_concepts),
            "text_length": len(request.text),
            "categories_found": list(set([c["category"] for c in extracted_concepts if c["category"]]))
        }

    except Exception as e:
        logger.error(f"Concept extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract medical concepts")

@router.get("/concepts/categories")
async def get_concept_categories():
    """Get all available neurosurgical concept categories"""
    try:
        categories = []
        for category in ConceptCategory:
            concepts = neurosurgical_concepts.get_concepts_by_category(category)
            categories.append({
                "category": category.value,
                "name": category.value.replace("_", " ").title(),
                "concept_count": len(concepts),
                "sample_concepts": concepts[:5]  # First 5 as samples
            })

        return {
            "success": True,
            "categories": categories,
            "total_categories": len(categories)
        }

    except Exception as e:
        logger.error(f"Failed to get concept categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get concept categories")

@router.get("/concepts/category/{category}")
async def get_concepts_by_category(category: str):
    """Get all concepts for a specific category"""
    try:
        # Validate category
        try:
            category_enum = ConceptCategory(category.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

        concepts = neurosurgical_concepts.get_concepts_by_category(category_enum)

        return {
            "success": True,
            "category": category,
            "concepts": concepts,
            "total_concepts": len(concepts)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get concepts for category {category}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get concepts")

@router.get("/concepts/expand/{term}")
async def expand_medical_term(term: str):
    """Get detailed information about a medical term"""
    try:
        logger.info(f"🔍 Expanding medical term: '{term}'")

        # Check if it's a known neurosurgical term
        is_neurosurg_term = neurosurgical_concepts.is_neurosurgical_term(term)

        if not is_neurosurg_term:
            return {
                "success": False,
                "message": f"'{term}' is not a recognized neurosurgical term",
                "term": term
            }

        # Get detailed information
        category = neurosurgical_concepts.get_concept_category(term)
        synonyms = neurosurgical_concepts.get_synonyms(term)
        related_concepts = neurosurgical_concepts.get_related_concepts(term)
        weight = neurosurgical_concepts.get_concept_weight(term)

        # Check if it's an abbreviation
        expanded = neurosurgical_concepts.expand_abbreviation(term)

        return {
            "success": True,
            "term": term,
            "expanded_term": expanded if expanded != term else None,
            "category": category.value if category else None,
            "weight": weight,
            "synonyms": synonyms,
            "related_concepts": related_concepts,
            "is_abbreviation": expanded != term
        }

    except Exception as e:
        logger.error(f"Failed to expand term '{term}': {e}")
        raise HTTPException(status_code=500, detail="Failed to expand medical term")

@router.get("/search/stats")
async def get_search_statistics():
    """Get statistics about the semantic search capabilities"""
    try:
        all_concepts = neurosurgical_concepts.get_all_concepts()

        # Count concepts by category
        category_stats = {}
        for category in ConceptCategory:
            concepts = neurosurgical_concepts.get_concepts_by_category(category)
            category_stats[category.value] = len(concepts)

        # Count synonyms and abbreviations
        synonym_count = sum(len(synonyms) for synonyms in neurosurgical_concepts.synonyms.values())
        abbreviation_count = len(neurosurgical_concepts.abbreviations)

        return {
            "success": True,
            "statistics": {
                "total_concepts": len(all_concepts),
                "categories": category_stats,
                "total_synonyms": synonym_count,
                "total_abbreviations": abbreviation_count,
                "embedding_model_available": semantic_search_engine.model is not None,
                "search_capabilities": [
                    "Semantic similarity search",
                    "Medical concept extraction",
                    "Query expansion with synonyms",
                    "Neurosurgical term recognition",
                    "Hierarchical concept relationships",
                    "Intelligent search suggestions"
                ]
            }
        }

    except Exception as e:
        logger.error(f"Failed to get search statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search statistics")