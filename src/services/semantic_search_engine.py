"""
Neurosurgical Semantic Search Engine
Advanced medical concept extraction, vector embeddings, and intelligent search
"""

import asyncio
import logging
import re
import math
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime
from collections import defaultdict, Counter
import numpy as np
from dataclasses import dataclass
import json

# Try to import sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

from .neurosurgical_concepts import neurosurgical_concepts, ConceptCategory
from ..core.database import get_async_session
from ..models.document import Document, DocumentExtract

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    document_id: str
    title: str
    content_snippet: str
    relevance_score: float
    concept_matches: List[str]
    concept_categories: List[str]
    semantic_similarity: float
    keyword_score: float
    medical_relevance: float
    document_type: str
    authors: List[str]
    specialty: str

@dataclass
class ConceptExtraction:
    concept: str
    category: ConceptCategory
    weight: float
    synonyms: List[str]
    related_concepts: List[str]
    positions: List[int]
    confidence: float

class NeurosurgicalSemanticSearchEngine:
    """
    Advanced semantic search engine for neurosurgical medical literature
    Combines medical concept extraction, vector embeddings, and intelligent ranking
    """

    def __init__(self):
        self.model = None
        self.concept_embeddings = {}
        self.document_embeddings = {}
        self.search_cache = {}

        # Initialize embedding model if available
        if EMBEDDINGS_AVAILABLE:
            try:
                # Use medical domain model for better medical text understanding
                self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
                logger.info("✅ Sentence transformer model loaded successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load sentence transformer: {e}")
                self.model = None
        else:
            logger.warning("⚠️ Sentence transformers not available. Using keyword-based search only.")

    async def initialize_embeddings(self):
        """Initialize concept embeddings for semantic similarity"""

        if not self.model:
            logger.info("🔄 Embeddings not available, using keyword-based search")
            return

        try:
            logger.info("🧠 Initializing neurosurgical concept embeddings...")

            # Get all neurosurgical concepts
            all_concepts = neurosurgical_concepts.get_all_concepts()

            # Create embeddings for concepts in batches
            batch_size = 50
            for i in range(0, len(all_concepts), batch_size):
                batch = all_concepts[i:i + batch_size]
                embeddings = self.model.encode(batch)

                for concept, embedding in zip(batch, embeddings):
                    self.concept_embeddings[concept.lower()] = embedding

            logger.info(f"✅ Created embeddings for {len(self.concept_embeddings)} neurosurgical concepts")

        except Exception as e:
            logger.error(f"❌ Failed to initialize concept embeddings: {e}")
            self.model = None

    async def search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        max_results: int = 20,
        search_type: str = "semantic",
        specialty_filter: Optional[str] = None,
        document_type_filter: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Perform intelligent semantic search with neurosurgical concept understanding
        """

        try:
            logger.info(f"🔍 Neurosurgical semantic search: '{query}' (type: {search_type})")

            # Extract medical concepts from query
            query_concepts = await self._extract_query_concepts(query)

            # Expand query with medical synonyms and related concepts
            expanded_query = await self._expand_query(query, query_concepts)

            # Get candidate documents
            candidate_docs = await self._get_candidate_documents(
                document_ids, specialty_filter, document_type_filter
            )

            if not candidate_docs:
                return []

            # Score documents based on search type
            if search_type == "semantic" and self.model:
                results = await self._semantic_search(expanded_query, query_concepts, candidate_docs)
            elif search_type == "medical_concept":
                results = await self._medical_concept_search(query_concepts, candidate_docs)
            else:
                results = await self._keyword_search(expanded_query, candidate_docs)

            # Apply additional neurosurgical relevance filtering
            results = await self._apply_medical_relevance_scoring(results, query_concepts)

            # Sort by relevance and return top results
            results.sort(key=lambda x: x.relevance_score, reverse=True)

            return results[:max_results]

        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []

    async def _extract_query_concepts(self, query: str) -> List[ConceptExtraction]:
        """Extract neurosurgical concepts from search query"""

        concepts = []
        query_lower = query.lower()

        # Extract direct concept matches
        all_concepts = neurosurgical_concepts.get_all_concepts()

        for concept in all_concepts:
            concept_lower = concept.lower()

            # Look for exact matches and partial matches
            positions = []
            start = 0
            while True:
                pos = query_lower.find(concept_lower, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1

            if positions:
                category = neurosurgical_concepts.get_concept_category(concept)
                weight = neurosurgical_concepts.get_concept_weight(concept)
                synonyms = neurosurgical_concepts.get_synonyms(concept)
                related = neurosurgical_concepts.get_related_concepts(concept)

                concepts.append(ConceptExtraction(
                    concept=concept,
                    category=category,
                    weight=weight,
                    synonyms=synonyms,
                    related_concepts=related,
                    positions=positions,
                    confidence=1.0  # Direct match
                ))

        # Extract abbreviations
        words = re.findall(r'\b[A-Z]{2,}\b', query)
        for word in words:
            expanded = neurosurgical_concepts.expand_abbreviation(word)
            if expanded != word and neurosurgical_concepts.is_neurosurgical_term(expanded):
                category = neurosurgical_concepts.get_concept_category(expanded)
                concepts.append(ConceptExtraction(
                    concept=expanded,
                    category=category,
                    weight=neurosurgical_concepts.get_concept_weight(expanded),
                    synonyms=neurosurgical_concepts.get_synonyms(expanded),
                    related_concepts=neurosurgical_concepts.get_related_concepts(expanded),
                    positions=[query.find(word)],
                    confidence=0.9  # Abbreviation match
                ))

        # Fuzzy matching for partial terms
        query_words = re.findall(r'\b\w+\b', query_lower)
        for concept in all_concepts:
            concept_words = concept.lower().split()

            # Check for partial word matches
            overlap = set(query_words) & set(concept_words)
            if overlap and len(overlap) >= len(concept_words) * 0.5:  # 50% overlap threshold
                if not any(c.concept == concept for c in concepts):  # Avoid duplicates
                    category = neurosurgical_concepts.get_concept_category(concept)
                    confidence = len(overlap) / len(concept_words)

                    concepts.append(ConceptExtraction(
                        concept=concept,
                        category=category,
                        weight=neurosurgical_concepts.get_concept_weight(concept) * confidence,
                        synonyms=neurosurgical_concepts.get_synonyms(concept),
                        related_concepts=neurosurgical_concepts.get_related_concepts(concept),
                        positions=[],
                        confidence=confidence
                    ))

        return concepts

    async def _expand_query(self, query: str, concepts: List[ConceptExtraction]) -> str:
        """Expand query with medical synonyms and related concepts"""

        expanded_terms = [query]

        for concept_extraction in concepts:
            # Add synonyms
            expanded_terms.extend(concept_extraction.synonyms)

            # Add high-confidence related concepts
            if concept_extraction.confidence > 0.8:
                expanded_terms.extend(concept_extraction.related_concepts[:3])  # Top 3 related

        # Remove duplicates and join
        unique_terms = list(set(expanded_terms))
        return " ".join(unique_terms)

    async def _get_candidate_documents(
        self,
        document_ids: Optional[List[str]],
        specialty_filter: Optional[str],
        document_type_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get candidate documents for search"""

        try:
            async with get_async_session() as session:
                # Build query
                query = session.query(Document, DocumentExtract).join(
                    DocumentExtract, Document.id == DocumentExtract.document_id
                ).filter(Document.status == "ready")

                # Apply filters
                if document_ids:
                    query = query.filter(Document.id.in_(document_ids))

                if specialty_filter:
                    query = query.filter(Document.specialty == specialty_filter)

                if document_type_filter:
                    query = query.filter(Document.document_type == document_type_filter)

                # Execute query
                results = await session.execute(query)
                documents = results.all()

                # Convert to dictionary format
                candidate_docs = []
                for doc, extract in documents:
                    candidate_docs.append({
                        "id": str(doc.id),
                        "title": doc.title,
                        "content": extract.content,
                        "document_type": doc.document_type,
                        "authors": doc.authors or [],
                        "specialty": doc.specialty or "",
                        "keywords": doc.keywords or [],
                        "word_count": extract.word_count
                    })

                return candidate_docs

        except Exception as e:
            logger.error(f"Failed to get candidate documents: {e}")
            return []

    async def _semantic_search(
        self,
        expanded_query: str,
        query_concepts: List[ConceptExtraction],
        candidate_docs: List[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Perform semantic search using vector embeddings"""

        if not self.model:
            # Fallback to keyword search
            return await self._keyword_search(expanded_query, candidate_docs)

        try:
            # Create query embedding
            query_embedding = self.model.encode([expanded_query])[0]

            results = []

            for doc in candidate_docs:
                # Create or get document embedding
                doc_key = doc["id"]
                if doc_key not in self.document_embeddings:
                    # Create embedding for document content
                    content_sample = doc["content"][:1000]  # First 1000 chars for efficiency
                    self.document_embeddings[doc_key] = self.model.encode([content_sample])[0]

                doc_embedding = self.document_embeddings[doc_key]

                # Calculate semantic similarity
                semantic_similarity = self._cosine_similarity(query_embedding, doc_embedding)

                # Calculate concept-based scores
                concept_score, matched_concepts = await self._calculate_concept_score(
                    doc["content"], query_concepts
                )

                # Calculate keyword score
                keyword_score = self._calculate_keyword_score(expanded_query, doc["content"])

                # Calculate medical relevance
                medical_relevance = await self._calculate_medical_relevance(
                    doc["content"], doc["specialty"]
                )

                # Combined relevance score
                relevance_score = (
                    semantic_similarity * 0.4 +
                    concept_score * 0.4 +
                    keyword_score * 0.1 +
                    medical_relevance * 0.1
                )

                # Extract content snippet
                snippet = self._extract_snippet(doc["content"], matched_concepts, 200)

                # Get concept categories
                categories = list(set([
                    concept.category.value for concept in query_concepts
                    if concept.category
                ]))

                results.append(SearchResult(
                    document_id=doc["id"],
                    title=doc["title"],
                    content_snippet=snippet,
                    relevance_score=relevance_score,
                    concept_matches=matched_concepts,
                    concept_categories=categories,
                    semantic_similarity=semantic_similarity,
                    keyword_score=keyword_score,
                    medical_relevance=medical_relevance,
                    document_type=doc["document_type"],
                    authors=doc["authors"],
                    specialty=doc["specialty"]
                ))

            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return await self._keyword_search(expanded_query, candidate_docs)

    async def _medical_concept_search(
        self,
        query_concepts: List[ConceptExtraction],
        candidate_docs: List[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Search based purely on medical concept matching"""

        results = []

        for doc in candidate_docs:
            concept_score, matched_concepts = await self._calculate_concept_score(
                doc["content"], query_concepts
            )

            if concept_score > 0.1:  # Minimum concept relevance threshold
                # Extract content snippet around concepts
                snippet = self._extract_snippet(doc["content"], matched_concepts, 200)

                # Get concept categories
                categories = list(set([
                    concept.category.value for concept in query_concepts
                    if concept.category
                ]))

                results.append(SearchResult(
                    document_id=doc["id"],
                    title=doc["title"],
                    content_snippet=snippet,
                    relevance_score=concept_score,
                    concept_matches=matched_concepts,
                    concept_categories=categories,
                    semantic_similarity=0.0,
                    keyword_score=0.0,
                    medical_relevance=concept_score,
                    document_type=doc["document_type"],
                    authors=doc["authors"],
                    specialty=doc["specialty"]
                ))

        return results

    async def _keyword_search(
        self,
        expanded_query: str,
        candidate_docs: List[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Fallback keyword-based search"""

        results = []
        query_terms = expanded_query.lower().split()

        for doc in candidate_docs:
            content_lower = doc["content"].lower()

            # Calculate keyword score
            keyword_score = self._calculate_keyword_score(expanded_query, doc["content"])

            if keyword_score > 0.1:  # Minimum keyword relevance threshold
                # Find keyword matches
                matched_terms = [term for term in query_terms if term in content_lower]

                # Extract snippet around keywords
                snippet = self._extract_snippet(doc["content"], matched_terms, 200)

                results.append(SearchResult(
                    document_id=doc["id"],
                    title=doc["title"],
                    content_snippet=snippet,
                    relevance_score=keyword_score,
                    concept_matches=matched_terms,
                    concept_categories=[],
                    semantic_similarity=0.0,
                    keyword_score=keyword_score,
                    medical_relevance=0.0,
                    document_type=doc["document_type"],
                    authors=doc["authors"],
                    specialty=doc["specialty"]
                ))

        return results

    async def _calculate_concept_score(
        self,
        content: str,
        query_concepts: List[ConceptExtraction]
    ) -> Tuple[float, List[str]]:
        """Calculate concept-based relevance score"""

        content_lower = content.lower()
        matched_concepts = []
        total_score = 0.0

        for concept_extraction in query_concepts:
            concept_lower = concept_extraction.concept.lower()

            # Check for direct concept match
            if concept_lower in content_lower:
                matched_concepts.append(concept_extraction.concept)
                score = concept_extraction.weight * concept_extraction.confidence
                total_score += score

            # Check for synonym matches
            for synonym in concept_extraction.synonyms:
                if synonym.lower() in content_lower:
                    matched_concepts.append(synonym)
                    score = concept_extraction.weight * 0.8  # Slight penalty for synonyms
                    total_score += score

            # Check for related concept matches (lower weight)
            for related in concept_extraction.related_concepts:
                if related.lower() in content_lower:
                    matched_concepts.append(related)
                    score = concept_extraction.weight * 0.5  # Lower weight for related concepts
                    total_score += score

        # Normalize score
        if query_concepts:
            max_possible_score = sum(c.weight for c in query_concepts)
            normalized_score = min(total_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
        else:
            normalized_score = 0.0

        return normalized_score, list(set(matched_concepts))

    def _calculate_keyword_score(self, query: str, content: str) -> float:
        """Calculate keyword-based relevance score"""

        query_terms = set(query.lower().split())
        content_terms = content.lower().split()
        content_term_count = Counter(content_terms)

        score = 0.0
        total_terms = len(query_terms)

        for term in query_terms:
            if term in content_term_count:
                # TF-IDF like scoring
                tf = content_term_count[term] / len(content_terms)
                score += tf

        return min(score / total_terms if total_terms > 0 else 0.0, 1.0)

    async def _calculate_medical_relevance(self, content: str, specialty: str) -> float:
        """Calculate medical relevance based on neurosurgical content"""

        # Base score from specialty match
        relevance = 0.0
        if specialty and "neurosurg" in specialty.lower():
            relevance += 0.3

        # Count neurosurgical terms in content
        content_lower = content.lower()
        neurosurg_terms = 0
        total_concepts = neurosurgical_concepts.get_all_concepts()

        for concept in total_concepts[:100]:  # Sample for efficiency
            if concept.lower() in content_lower:
                neurosurg_terms += 1

        # Normalize neurosurgical term density
        content_words = len(content.split())
        if content_words > 0:
            term_density = min(neurosurg_terms / (content_words / 100), 1.0)  # Per 100 words
            relevance += term_density * 0.7

        return min(relevance, 1.0)

    async def _apply_medical_relevance_scoring(
        self,
        results: List[SearchResult],
        query_concepts: List[ConceptExtraction]
    ) -> List[SearchResult]:
        """Apply additional medical relevance scoring"""

        for result in results:
            # Boost scores for high-priority neurosurgical concepts
            concept_boost = 0.0
            for concept in result.concept_matches:
                if neurosurgical_concepts.is_neurosurgical_term(concept):
                    weight = neurosurgical_concepts.get_concept_weight(concept)
                    concept_boost += weight * 0.1

            # Boost scores for neurosurgery specialty
            specialty_boost = 0.0
            if "neurosurg" in result.specialty.lower():
                specialty_boost = 0.1

            # Apply boosts
            result.relevance_score = min(result.relevance_score + concept_boost + specialty_boost, 1.0)

        return results

    def _extract_snippet(self, content: str, matched_terms: List[str], max_length: int) -> str:
        """Extract relevant snippet from content around matched terms"""

        if not matched_terms:
            return content[:max_length] + "..." if len(content) > max_length else content

        content_lower = content.lower()
        best_position = 0
        max_term_density = 0

        # Find position with highest density of matched terms
        window_size = max_length // 2
        for i in range(0, len(content) - window_size, 50):
            window = content_lower[i:i + window_size]
            term_count = sum(1 for term in matched_terms if term.lower() in window)

            if term_count > max_term_density:
                max_term_density = term_count
                best_position = i

        # Extract snippet
        start = max(0, best_position - 50)
        end = min(len(content), start + max_length)
        snippet = content[start:end]

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))
        except:
            return 0.0

    async def get_search_suggestions(self, query: str) -> List[str]:
        """Get intelligent search suggestions based on neurosurgical concepts"""

        suggestions = []
        query_lower = query.lower()

        # Find partial matches in concepts
        all_concepts = neurosurgical_concepts.get_all_concepts()

        for concept in all_concepts:
            if query_lower in concept.lower() and len(query) >= 3:
                suggestions.append(concept)

        # Add synonyms and related concepts
        for concept in suggestions[:5]:  # Top 5 to avoid too many suggestions
            suggestions.extend(neurosurgical_concepts.get_synonyms(concept)[:2])
            suggestions.extend(neurosurgical_concepts.get_related_concepts(concept)[:2])

        # Remove duplicates and sort by relevance
        unique_suggestions = list(set(suggestions))
        unique_suggestions.sort(key=lambda x: neurosurgical_concepts.get_concept_weight(x), reverse=True)

        return unique_suggestions[:10]  # Return top 10 suggestions

# Global instance
semantic_search_engine = NeurosurgicalSemanticSearchEngine()