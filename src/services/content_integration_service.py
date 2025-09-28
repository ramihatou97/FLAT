"""
Content Integration Service
==========================

Unified content integration system that handles content from both:
1. API integrations (programmatic AI provider calls)
2. Web interface extractions (manual AI provider interactions)

Ensures all extracted information is seamlessly integrated into the platform
with consistent formatting, indexing, and searchability.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path
import hashlib
import re
from pydantic import BaseModel

from ..core.database import get_async_session
from .semantic_search_engine import semantic_search_engine
from .neurosurgical_concepts import neurosurgical_concepts

logger = logging.getLogger(__name__)

class ContentSource(str, Enum):
    """Content source types"""
    GEMINI_API = "gemini_api"
    GEMINI_WEB = "gemini_web_studio"
    CLAUDE_API = "claude_api"
    CLAUDE_WEB = "claude_web_interface"
    OPENAI_API = "openai_api"
    OPENAI_WEB = "chatgpt_web"
    PERPLEXITY_API = "perplexity_api"
    PERPLEXITY_WEB = "perplexity_web"
    PLATFORM_GENERATED = "platform_internal"
    USER_UPLOADED = "user_upload"

class ContentType(str, Enum):
    """Content types for organization"""
    MEDICAL_ANALYSIS = "medical_analysis"
    RESEARCH_SUMMARY = "research_summary"
    LITERATURE_REVIEW = "literature_review"
    CASE_STUDY = "case_study"
    CLINICAL_GUIDELINES = "clinical_guidelines"
    DIAGNOSTIC_INSIGHT = "diagnostic_insight"
    TREATMENT_PROTOCOL = "treatment_protocol"
    EDUCATIONAL_CONTENT = "educational_content"
    RAW_EXTRACTION = "raw_extraction"

class IntegratedContent(BaseModel):
    """Unified content model for all sources"""
    id: str
    title: str
    content: str
    content_type: ContentType
    source: ContentSource
    provider: str  # gemini, claude, openai, perplexity
    extraction_method: str  # api, web_import, manual_entry
    metadata: Dict[str, Any]
    medical_concepts: List[str]
    confidence_score: float
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    references: List[str]
    embedding_vector: Optional[List[float]]

class ContentIntegrationService:
    """Service for integrating content from all AI provider sources"""

    def __init__(self):
        self.content_store = {}  # In-memory cache
        self.integration_rules = self._load_integration_rules()

    def _load_integration_rules(self) -> Dict:
        """Load content integration and processing rules"""
        return {
            "gemini": {
                "deep_search_indicators": ["searched for:", "found sources:", "references:"],
                "deep_think_indicators": ["reasoning:", "analysis:", "conclusion:"],
                "content_patterns": {
                    "citations": r'\[(\d+)\]',
                    "medical_terms": r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
                    "dosages": r'\d+\s*(?:mg|ml|g|l|units?)',
                    "procedures": r'(?i)\b(?:surgery|procedure|operation|intervention)\b'
                }
            },
            "claude": {
                "reasoning_indicators": ["Let me analyze", "My reasoning", "Based on"],
                "file_analysis_indicators": ["document analysis:", "file content:", "extracted from:"],
                "content_patterns": {
                    "structured_analysis": r'(?:Analysis|Summary|Conclusion):\s*(.*?)(?=\n\n|\Z)',
                    "medical_recommendations": r'(?i)(?:recommend|suggest|advise).*?[.!?]',
                    "evidence_levels": r'(?i)\b(?:level [IVX]+|grade [ABC]|class [123])\b'
                }
            },
            "openai": {
                "code_execution_indicators": ["```python", "execution result:", "calculated:"],
                "dalle_indicators": ["generated image:", "image description:"],
                "content_patterns": {
                    "step_by_step": r'(?:Step \d+|First|Second|Third|Finally):\s*(.*?)(?=\n|$)',
                    "medical_calculations": r'\d+(?:\.\d+)?\s*(?:mg/kg|units/ml|%)',
                    "clinical_scores": r'\b(?:NIHSS|GCS|mRS|Karnofsky)\s*(?:score)?:?\s*\d+'
                }
            },
            "perplexity": {
                "search_indicators": ["Sources:", "References:", "According to:"],
                "real_time_indicators": ["latest data:", "recent studies:", "current research:"],
                "content_patterns": {
                    "source_citations": r'\[\d+\]\s*(https?://[^\s]+)',
                    "recent_findings": r'(?i)(?:recent|latest|new|current)\s+(?:study|research|findings?)',
                    "publication_dates": r'\b(?:2024|2023|2022)\b'
                }
            }
        }

    async def integrate_api_content(
        self,
        content: str,
        provider: str,
        metadata: Dict[str, Any],
        content_type: ContentType = ContentType.RAW_EXTRACTION
    ) -> IntegratedContent:
        """Integrate content from API calls"""

        # Generate unique content ID
        content_id = self._generate_content_id(content, provider, "api")

        # Extract medical concepts
        medical_concepts = await self._extract_medical_concepts(content)

        # Determine content source
        source = self._map_provider_to_api_source(provider)

        # Create embedding vector
        embedding = await self._create_embedding(content)

        # Extract metadata based on provider
        enhanced_metadata = await self._enhance_metadata(content, provider, metadata)

        # Determine content confidence
        confidence = await self._calculate_confidence(content, provider, "api")

        integrated_content = IntegratedContent(
            id=content_id,
            title=enhanced_metadata.get("title", self._generate_title(content)),
            content=content,
            content_type=content_type,
            source=source,
            provider=provider,
            extraction_method="api",
            metadata=enhanced_metadata,
            medical_concepts=medical_concepts,
            confidence_score=confidence,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=self._extract_tags(content, provider),
            references=self._extract_references(content, provider),
            embedding_vector=embedding
        )

        # Store in database and cache
        await self._store_content(integrated_content)

        return integrated_content

    async def integrate_web_content(
        self,
        content: str,
        provider: str,
        source_interface: str,
        metadata: Dict[str, Any],
        content_type: ContentType = ContentType.RAW_EXTRACTION
    ) -> IntegratedContent:
        """Integrate content from web interfaces (manual extraction)"""

        # Generate unique content ID
        content_id = self._generate_content_id(content, provider, "web")

        # Extract medical concepts
        medical_concepts = await self._extract_medical_concepts(content)

        # Determine content source
        source = self._map_provider_to_web_source(provider)

        # Create embedding vector
        embedding = await self._create_embedding(content)

        # Extract metadata with web-specific enhancements
        enhanced_metadata = await self._enhance_web_metadata(
            content, provider, source_interface, metadata
        )

        # Determine content confidence (web content often has additional context)
        confidence = await self._calculate_confidence(content, provider, "web")

        integrated_content = IntegratedContent(
            id=content_id,
            title=enhanced_metadata.get("title", self._generate_title(content)),
            content=content,
            content_type=content_type,
            source=source,
            provider=provider,
            extraction_method="web_import",
            metadata=enhanced_metadata,
            medical_concepts=medical_concepts,
            confidence_score=confidence,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=self._extract_tags(content, provider),
            references=self._extract_references(content, provider),
            embedding_vector=embedding
        )

        # Store in database and cache
        await self._store_content(integrated_content)

        return integrated_content

    async def batch_integrate_content(
        self,
        content_items: List[Dict[str, Any]]
    ) -> List[IntegratedContent]:
        """Batch integration for multiple content items"""

        integrated_items = []

        for item in content_items:
            try:
                if item.get("extraction_method") == "api":
                    integrated = await self.integrate_api_content(
                        content=item["content"],
                        provider=item["provider"],
                        metadata=item.get("metadata", {}),
                        content_type=ContentType(item.get("content_type", "raw_extraction"))
                    )
                else:
                    integrated = await self.integrate_web_content(
                        content=item["content"],
                        provider=item["provider"],
                        source_interface=item.get("source_interface", "unknown"),
                        metadata=item.get("metadata", {}),
                        content_type=ContentType(item.get("content_type", "raw_extraction"))
                    )

                integrated_items.append(integrated)

            except Exception as e:
                logger.error(f"Failed to integrate content item: {e}")
                continue

        return integrated_items

    async def search_integrated_content(
        self,
        query: str,
        content_type: Optional[ContentType] = None,
        provider: Optional[str] = None,
        source: Optional[ContentSource] = None,
        max_results: int = 20
    ) -> List[IntegratedContent]:
        """Search through integrated content using semantic similarity"""

        # Create embedding for the query
        query_embedding = await self._create_embedding(query)

        # Search using semantic similarity
        similar_content = await self._semantic_search(
            query_embedding, content_type, provider, source, max_results
        )

        return similar_content

    async def merge_similar_content(
        self,
        similarity_threshold: float = 0.9
    ) -> List[Dict[str, Any]]:
        """Identify and merge similar content from different sources"""

        merged_items = []
        processed_ids = set()

        all_content = await self._get_all_content()

        for content in all_content:
            if content.id in processed_ids:
                continue

            # Find similar content
            similar_items = await self._find_similar_content(
                content, similarity_threshold
            )

            if similar_items:
                # Merge content
                merged = await self._merge_content_items([content] + similar_items)
                merged_items.append(merged)

                # Mark as processed
                processed_ids.add(content.id)
                for item in similar_items:
                    processed_ids.add(item.id)
            else:
                # Keep as standalone
                merged_items.append(content.dict())

        return merged_items

    async def export_integrated_content(
        self,
        format_type: str = "json",
        filter_criteria: Optional[Dict] = None
    ) -> str:
        """Export integrated content in various formats"""

        content_items = await self._filter_content(filter_criteria or {})

        if format_type == "json":
            return json.dumps([item.dict() for item in content_items], indent=2, default=str)
        elif format_type == "markdown":
            return await self._export_to_markdown(content_items)
        elif format_type == "csv":
            return await self._export_to_csv(content_items)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    # Helper Methods

    def _generate_content_id(self, content: str, provider: str, method: str) -> str:
        """Generate unique content ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{provider}_{method}_{timestamp}_{content_hash}"

    async def _extract_medical_concepts(self, content: str) -> List[str]:
        """Extract medical concepts from content"""
        concepts = []

        # Use neurosurgical concepts database
        all_concepts = neurosurgical_concepts.get_all_concepts()

        for concept in all_concepts:
            if concept.lower() in content.lower():
                concepts.append(concept)

        # Additional NLP-based concept extraction could be added here

        return list(set(concepts))

    async def _create_embedding(self, content: str) -> List[float]:
        """Create embedding vector for content"""
        try:
            embedding = await semantic_search_engine.create_embedding(content)
            return embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return []

    def _map_provider_to_api_source(self, provider: str) -> ContentSource:
        """Map provider to API source enum"""
        mapping = {
            "gemini": ContentSource.GEMINI_API,
            "claude": ContentSource.CLAUDE_API,
            "openai": ContentSource.OPENAI_API,
            "perplexity": ContentSource.PERPLEXITY_API
        }
        return mapping.get(provider, ContentSource.PLATFORM_GENERATED)

    def _map_provider_to_web_source(self, provider: str) -> ContentSource:
        """Map provider to web source enum"""
        mapping = {
            "gemini": ContentSource.GEMINI_WEB,
            "claude": ContentSource.CLAUDE_WEB,
            "openai": ContentSource.OPENAI_WEB,
            "perplexity": ContentSource.PERPLEXITY_WEB
        }
        return mapping.get(provider, ContentSource.USER_UPLOADED)

    async def _enhance_metadata(
        self, content: str, provider: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance metadata based on provider-specific patterns"""

        enhanced = metadata.copy()
        rules = self.integration_rules.get(provider, {})

        # Extract provider-specific features
        if provider == "gemini":
            enhanced.update(await self._extract_gemini_features(content))
        elif provider == "claude":
            enhanced.update(await self._extract_claude_features(content))
        elif provider == "openai":
            enhanced.update(await self._extract_openai_features(content))
        elif provider == "perplexity":
            enhanced.update(await self._extract_perplexity_features(content))

        # Add general metadata
        enhanced.update({
            "content_length": len(content),
            "word_count": len(content.split()),
            "medical_density": await self._calculate_medical_density(content),
            "readability_score": await self._calculate_readability(content),
            "extraction_timestamp": datetime.utcnow().isoformat()
        })

        return enhanced

    async def _enhance_web_metadata(
        self, content: str, provider: str, source_interface: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance metadata for web-sourced content"""

        enhanced = await self._enhance_metadata(content, provider, metadata)

        # Add web-specific metadata
        enhanced.update({
            "source_interface": source_interface,
            "extraction_context": "web_interface",
            "manual_extraction": True,
            "interface_features_used": await self._detect_interface_features(content, provider)
        })

        return enhanced

    async def _extract_gemini_features(self, content: str) -> Dict[str, Any]:
        """Extract Gemini-specific features"""
        features = {}

        # Detect Deep Search usage
        if any(indicator in content.lower() for indicator in ["searched for:", "found sources:"]):
            features["deep_search_used"] = True
            features["search_results_count"] = len(re.findall(r'\[\d+\]', content))

        # Detect Deep Think usage
        if any(indicator in content.lower() for indicator in ["reasoning:", "analysis:"]):
            features["deep_think_used"] = True
            features["reasoning_depth"] = len(re.findall(r'(?:because|therefore|thus|hence)', content.lower()))

        # Detect multimodal content
        if any(term in content.lower() for term in ["image", "chart", "diagram", "figure"]):
            features["multimodal_content"] = True

        return features

    async def _extract_claude_features(self, content: str) -> Dict[str, Any]:
        """Extract Claude-specific features"""
        features = {}

        # Detect extended reasoning
        reasoning_patterns = len(re.findall(r'(?:let me|first|second|third|finally)', content.lower()))
        features["reasoning_complexity"] = reasoning_patterns

        # Detect file analysis
        if any(term in content.lower() for term in ["document", "file", "uploaded"]):
            features["file_analysis"] = True

        # Detect structured thinking
        if re.search(r'\d+\.\s|\n-\s|•\s', content):
            features["structured_output"] = True

        return features

    async def _extract_openai_features(self, content: str) -> Dict[str, Any]:
        """Extract OpenAI-specific features"""
        features = {}

        # Detect code execution
        if "```" in content or "execution result" in content.lower():
            features["code_execution_used"] = True

        # Detect DALL-E usage
        if any(term in content.lower() for term in ["generated image", "dall-e", "image created"]):
            features["image_generation"] = True

        # Detect web browsing
        if any(term in content.lower() for term in ["browsed", "searched the web", "found online"]):
            features["web_browsing_used"] = True

        return features

    async def _extract_perplexity_features(self, content: str) -> Dict[str, Any]:
        """Extract Perplexity-specific features"""
        features = {}

        # Count source citations
        citations = len(re.findall(r'\[\d+\]', content))
        features["source_citations_count"] = citations

        # Detect real-time data
        if any(term in content.lower() for term in ["latest", "recent", "current", "2024"]):
            features["real_time_data"] = True

        # Extract source URLs
        urls = re.findall(r'https?://[^\s]+', content)
        features["source_urls"] = urls[:10]  # Limit to first 10

        return features

    def _generate_title(self, content: str, max_length: int = 100) -> str:
        """Generate title from content"""
        # Simple title generation - take first meaningful sentence
        sentences = content.split('.')
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if len(clean_sentence) > 10 and len(clean_sentence) <= max_length:
                return clean_sentence

        # Fallback to first max_length characters
        return content[:max_length].strip() + "..."

    def _extract_tags(self, content: str, provider: str) -> List[str]:
        """Extract relevant tags from content"""
        tags = [provider]

        # Medical specialties
        specialties = ["neurosurgery", "oncology", "cardiology", "radiology", "pathology"]
        for specialty in specialties:
            if specialty in content.lower():
                tags.append(specialty)

        # Content characteristics
        if len(content) > 2000:
            tags.append("detailed_analysis")
        if "treatment" in content.lower():
            tags.append("treatment")
        if "diagnosis" in content.lower():
            tags.append("diagnosis")
        if "research" in content.lower():
            tags.append("research")

        return list(set(tags))

    def _extract_references(self, content: str, provider: str) -> List[str]:
        """Extract references from content"""
        references = []

        # URL references
        urls = re.findall(r'https?://[^\s]+', content)
        references.extend(urls)

        # Citation patterns
        citations = re.findall(r'\[(\d+)\]', content)
        references.extend([f"Citation {c}" for c in citations])

        # DOI patterns
        dois = re.findall(r'10\.\d+/[^\s]+', content)
        references.extend([f"DOI: {doi}" for doi in dois])

        return references

    async def _calculate_confidence(self, content: str, provider: str, method: str) -> float:
        """Calculate confidence score for content"""
        base_confidence = 0.7

        # Provider-specific confidence adjustments
        provider_bonus = {
            "gemini": 0.1,
            "claude": 0.15,
            "openai": 0.1,
            "perplexity": 0.05
        }.get(provider, 0)

        # Method-specific adjustments
        method_bonus = 0.05 if method == "web" else 0  # Web content has human oversight

        # Content quality indicators
        quality_score = 0
        if len(content) > 500:  # Substantial content
            quality_score += 0.1
        if re.search(r'\[\d+\]', content):  # Has citations
            quality_score += 0.1
        if len(re.findall(r'[.!?]', content)) > 5:  # Well-structured
            quality_score += 0.05

        return min(1.0, base_confidence + provider_bonus + method_bonus + quality_score)

    async def _store_content(self, content: IntegratedContent):
        """Store content in database and cache"""
        # Store in cache
        self.content_store[content.id] = content

        # Store in database (implementation would depend on your database schema)
        try:
            async with get_async_session() as session:
                # Implementation for database storage
                # This would involve inserting into your content table
                pass
        except Exception as e:
            logger.error(f"Failed to store content in database: {e}")

    async def _calculate_medical_density(self, content: str) -> float:
        """Calculate the density of medical terms in content"""
        words = content.split()
        medical_terms = await self._extract_medical_concepts(content)

        if not words:
            return 0.0

        return len(medical_terms) / len(words)

    async def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (simplified)"""
        sentences = len(re.findall(r'[.!?]', content))
        words = len(content.split())

        if sentences == 0:
            return 0.0

        # Simplified readability (average words per sentence)
        avg_words_per_sentence = words / sentences

        # Score from 0-1 (lower is more readable)
        return min(1.0, avg_words_per_sentence / 25)

    async def _detect_interface_features(self, content: str, provider: str) -> List[str]:
        """Detect which interface features were used"""
        features = []

        if provider == "gemini":
            if "deep search" in content.lower():
                features.append("deep_search")
            if "deep think" in content.lower():
                features.append("deep_think")

        elif provider == "claude":
            if "reasoning" in content.lower():
                features.append("extended_reasoning")
            if "file" in content.lower():
                features.append("file_analysis")

        # Add more provider-specific feature detection

        return features

# Global instance
content_integration_service = ContentIntegrationService()