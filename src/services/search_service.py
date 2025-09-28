"""Simplified search service"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SearchService:
    """Simple search service for medical content"""

    async def search_content(
        self,
        query: str,
        specialty: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search medical content"""

        try:
            # TODO: Implement real search when database integration is complete
            # For now, return mock search results
            mock_results = [
                {
                    "id": "1",
                    "title": "Brain Tumor Management",
                    "snippet": "Comprehensive approach to brain tumor diagnosis and surgical treatment including craniotomy procedures and post-operative care...",
                    "type": "chapter",
                    "specialty": "neurosurgery",
                    "relevance_score": 0.95,
                    "last_updated": "2024-01-15"
                },
                {
                    "id": "2",
                    "title": "Spinal Fusion Techniques",
                    "snippet": "Modern approaches to spinal fusion surgery including minimally invasive techniques and hardware selection...",
                    "type": "chapter",
                    "specialty": "neurosurgery",
                    "relevance_score": 0.87,
                    "last_updated": "2024-01-10"
                },
                {
                    "id": "3",
                    "title": "Recent Advances in Neuro-oncology",
                    "snippet": "Latest research in brain tumor treatment and molecular targeted therapies...",
                    "type": "article",
                    "specialty": "neurosurgery",
                    "relevance_score": 0.82,
                    "last_updated": "2024-01-08"
                }
            ]

            # Filter results based on criteria
            filtered_results = []
            for result in mock_results:
                if specialty and result["specialty"] != specialty:
                    continue
                if content_type and result["type"] != content_type:
                    continue
                if query.lower() not in result["title"].lower() and query.lower() not in result["snippet"].lower():
                    continue

                filtered_results.append(result)

            # Sort by relevance score
            filtered_results.sort(key=lambda x: x["relevance_score"], reverse=True)

            # Limit results
            limited_results = filtered_results[:limit]

            logger.info(f"Search completed: {len(limited_results)} results for '{query}'")
            return {
                "success": True,
                "query": query,
                "results": limited_results,
                "total": len(limited_results),
                "filters": {
                    "specialty": specialty,
                    "content_type": content_type
                }
            }

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    async def get_search_suggestions(self, partial_query: str) -> Dict[str, Any]:
        """Get search suggestions for autocomplete"""

        try:
            # Common medical search terms
            medical_terms = [
                "brain tumor", "craniotomy", "spinal fusion", "aneurysm",
                "glioma", "meningioma", "hydrocephalus", "cervical spine",
                "lumbar spine", "neurosurgery", "minimally invasive",
                "post-operative care", "surgical techniques", "radiology"
            ]

            # Filter terms that match partial query
            partial_lower = partial_query.lower()
            suggestions = [
                term for term in medical_terms
                if partial_lower in term.lower()
            ]

            return {
                "success": True,
                "query": partial_query,
                "suggestions": suggestions[:5]  # Limit to 5 suggestions
            }

        except Exception as e:
            logger.error(f"Search suggestions failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "suggestions": []
            }

# Global search service instance
search_service = SearchService()