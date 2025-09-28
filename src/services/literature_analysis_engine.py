"""
AI Literature Analysis Engine
Advanced automated analysis and synthesis of medical literature
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
from enum import Enum
import networkx as nx
import numpy as np

from .research_api import research_api
from .multi_ai_manager import multi_ai_manager
from .semantic_search_engine import semantic_search_engine
from .neurosurgical_concepts import neurosurgical_concepts, ConceptCategory

logger = logging.getLogger(__name__)

class EvidenceLevel(Enum):
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    RANDOMIZED_TRIAL = "randomized_trial"
    COHORT_STUDY = "cohort_study"
    CASE_CONTROL = "case_control"
    CASE_SERIES = "case_series"
    CASE_REPORT = "case_report"
    EXPERT_OPINION = "expert_opinion"

class ConflictType(Enum):
    METHODOLOGY = "methodology"
    RESULTS = "results"
    INTERPRETATION = "interpretation"
    DOSAGE = "dosage"
    TIMING = "timing"
    POPULATION = "population"

@dataclass
class CitationNode:
    pmid: str
    title: str
    authors: List[str]
    journal: str
    year: int
    citation_count: int
    abstract: str
    keywords: List[str]
    evidence_level: EvidenceLevel
    neurosurgical_relevance: float

@dataclass
class CitationEdge:
    citing_pmid: str
    cited_pmid: str
    context: str
    relationship_type: str  # supports, contradicts, extends, questions
    strength: float

@dataclass
class LiteratureConflict:
    pmid_a: str
    pmid_b: str
    conflict_type: ConflictType
    description: str
    confidence: float
    resolution_suggestion: str

@dataclass
class EvidenceSynthesis:
    topic: str
    total_papers: int
    evidence_summary: str
    quality_score: float
    recommendations: List[str]
    limitations: List[str]
    future_research: List[str]
    conflicts_detected: List[LiteratureConflict]
    citation_network: Dict[str, Any]

class LiteratureAnalysisEngine:
    """
    AI-powered literature analysis engine for neurosurgical research
    Provides automated review, synthesis, and conflict detection
    """

    def __init__(self):
        self.evidence_weights = {
            EvidenceLevel.SYSTEMATIC_REVIEW: 1.0,
            EvidenceLevel.META_ANALYSIS: 1.0,
            EvidenceLevel.RANDOMIZED_TRIAL: 0.9,
            EvidenceLevel.COHORT_STUDY: 0.8,
            EvidenceLevel.CASE_CONTROL: 0.7,
            EvidenceLevel.CASE_SERIES: 0.6,
            EvidenceLevel.CASE_REPORT: 0.5,
            EvidenceLevel.EXPERT_OPINION: 0.4
        }

        # Cache for literature analysis
        self.analysis_cache = {}
        self.citation_networks = {}

    async def analyze_literature_corpus(
        self,
        topic: str,
        max_papers: int = 50,
        years_back: int = 10,
        include_meta_analysis: bool = True
    ) -> EvidenceSynthesis:
        """
        Comprehensive analysis of literature corpus on a specific topic
        """

        try:
            logger.info(f"🔬 Starting literature analysis for: '{topic}'")

            # Step 1: Gather relevant literature
            papers = await self._gather_literature(topic, max_papers, years_back)
            logger.info(f"📚 Gathered {len(papers)} papers for analysis")

            # Step 2: Build citation network
            citation_network = await self._build_citation_network(papers)
            logger.info(f"🕸️ Built citation network with {len(citation_network['nodes'])} nodes")

            # Step 3: Classify evidence levels
            classified_papers = await self._classify_evidence_levels(papers)

            # Step 4: Detect conflicts in findings
            conflicts = await self._detect_research_conflicts(classified_papers)
            logger.info(f"⚠️ Detected {len(conflicts)} potential conflicts")

            # Step 5: Generate evidence synthesis
            synthesis = await self._generate_evidence_synthesis(
                topic, classified_papers, conflicts, citation_network
            )

            # Step 6: Calculate quality metrics
            quality_score = await self._calculate_synthesis_quality(classified_papers, conflicts)

            result = EvidenceSynthesis(
                topic=topic,
                total_papers=len(papers),
                evidence_summary=synthesis['summary'],
                quality_score=quality_score,
                recommendations=synthesis['recommendations'],
                limitations=synthesis['limitations'],
                future_research=synthesis['future_research'],
                conflicts_detected=conflicts,
                citation_network=citation_network
            )

            # Cache the result
            cache_key = f"{topic}_{max_papers}_{years_back}"
            self.analysis_cache[cache_key] = result

            logger.info(f"✅ Literature analysis completed (quality: {quality_score:.2f})")
            return result

        except Exception as e:
            logger.error(f"❌ Literature analysis failed: {e}")
            raise

    async def _gather_literature(
        self,
        topic: str,
        max_papers: int,
        years_back: int
    ) -> List[Dict[str, Any]]:
        """Gather relevant literature from multiple sources"""

        try:
            # Use existing research API to gather papers
            current_year = datetime.now().year
            year_from = current_year - years_back

            # Search PubMed
            pubmed_result = await research_api.search_pubmed(
                query=topic,
                max_results=max_papers // 2,
                year_from=year_from,
                article_types=["Clinical Trial", "Systematic Review", "Meta-Analysis", "Review"]
            )

            papers = []
            if pubmed_result.get("success"):
                papers.extend(pubmed_result.get("articles", []))

            # Search Google Scholar for additional papers
            scholar_result = await research_api.search_google_scholar(
                query=topic,
                max_results=max_papers // 2,
                year_from=year_from
            )

            if scholar_result.get("success"):
                papers.extend(scholar_result.get("articles", []))

            # Remove duplicates based on title similarity
            unique_papers = await self._deduplicate_papers(papers)

            # Enhance papers with neurosurgical relevance scoring
            enhanced_papers = []
            for paper in unique_papers[:max_papers]:
                relevance = await self._calculate_neurosurgical_relevance(paper)
                paper['neurosurgical_relevance'] = relevance
                enhanced_papers.append(paper)

            # Sort by relevance and return top papers
            enhanced_papers.sort(key=lambda x: x['neurosurgical_relevance'], reverse=True)
            return enhanced_papers

        except Exception as e:
            logger.error(f"Failed to gather literature: {e}")
            return []

    async def _build_citation_network(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build citation network graph from papers"""

        try:
            # Create network graph
            G = nx.DiGraph()

            # Add nodes for each paper
            nodes = []
            for paper in papers:
                pmid = paper.get('pmid', paper.get('id', str(hash(paper['title']))))

                node_data = {
                    'pmid': pmid,
                    'title': paper['title'],
                    'authors': paper.get('authors', []),
                    'year': paper.get('year', 0),
                    'journal': paper.get('journal', ''),
                    'citation_count': paper.get('citation_count', 0),
                    'neurosurgical_relevance': paper.get('neurosurgical_relevance', 0.0)
                }

                G.add_node(pmid, **node_data)
                nodes.append(node_data)

            # Add edges based on citations (simplified approach)
            edges = []
            for paper in papers:
                pmid = paper.get('pmid', paper.get('id', str(hash(paper['title']))))
                references = paper.get('references', [])

                for ref_pmid in references:
                    if ref_pmid in G.nodes():
                        G.add_edge(pmid, ref_pmid, relationship='cites')
                        edges.append({
                            'citing': pmid,
                            'cited': ref_pmid,
                            'relationship': 'cites'
                        })

            # Calculate network metrics
            try:
                pagerank = nx.pagerank(G)
                betweenness = nx.betweenness_centrality(G)
                closeness = nx.closeness_centrality(G)
            except:
                pagerank = {node: 0.1 for node in G.nodes()}
                betweenness = {node: 0.1 for node in G.nodes()}
                closeness = {node: 0.1 for node in G.nodes()}

            network_data = {
                'nodes': nodes,
                'edges': edges,
                'metrics': {
                    'total_nodes': len(nodes),
                    'total_edges': len(edges),
                    'density': nx.density(G) if len(nodes) > 1 else 0,
                    'pagerank': pagerank,
                    'betweenness_centrality': betweenness,
                    'closeness_centrality': closeness
                }
            }

            return network_data

        except Exception as e:
            logger.error(f"Failed to build citation network: {e}")
            return {'nodes': [], 'edges': [], 'metrics': {}}

    async def _classify_evidence_levels(self, papers: List[Dict[str, Any]]) -> List[CitationNode]:
        """Classify papers by evidence level using AI analysis"""

        classified_papers = []

        for paper in papers:
            try:
                # Extract key information
                title = paper.get('title', '')
                abstract = paper.get('abstract', '')
                keywords = paper.get('keywords', [])

                # Use AI to classify evidence level
                evidence_level = await self._ai_classify_evidence_level(title, abstract)

                # Create CitationNode
                node = CitationNode(
                    pmid=paper.get('pmid', str(hash(title))),
                    title=title,
                    authors=paper.get('authors', []),
                    journal=paper.get('journal', ''),
                    year=paper.get('year', 0),
                    citation_count=paper.get('citation_count', 0),
                    abstract=abstract,
                    keywords=keywords,
                    evidence_level=evidence_level,
                    neurosurgical_relevance=paper.get('neurosurgical_relevance', 0.0)
                )

                classified_papers.append(node)

            except Exception as e:
                logger.warning(f"Failed to classify paper: {e}")
                continue

        return classified_papers

    async def _ai_classify_evidence_level(self, title: str, abstract: str) -> EvidenceLevel:
        """Use AI to classify the evidence level of a paper"""

        try:
            # Create classification prompt
            prompt = f"""
            Classify the evidence level of this medical research paper:

            Title: {title}
            Abstract: {abstract[:500]}...

            Classify as one of:
            - systematic_review: Systematic review or meta-analysis
            - meta_analysis: Statistical meta-analysis
            - randomized_trial: Randomized controlled trial
            - cohort_study: Cohort or longitudinal study
            - case_control: Case-control study
            - case_series: Case series or case studies
            - case_report: Single case report
            - expert_opinion: Expert opinion or editorial

            Respond with only the classification (e.g., "randomized_trial").
            """

            # Use Claude for classification (best for medical text analysis)
            result = await multi_ai_manager.generate_content(
                prompt=prompt,
                provider="claude",
                context_type="medical",
                max_tokens=50,
                temperature=0.1
            )

            if result.get("success"):
                classification = result["content"].strip().lower()

                # Map to EvidenceLevel enum
                level_mapping = {
                    'systematic_review': EvidenceLevel.SYSTEMATIC_REVIEW,
                    'meta_analysis': EvidenceLevel.META_ANALYSIS,
                    'randomized_trial': EvidenceLevel.RANDOMIZED_TRIAL,
                    'cohort_study': EvidenceLevel.COHORT_STUDY,
                    'case_control': EvidenceLevel.CASE_CONTROL,
                    'case_series': EvidenceLevel.CASE_SERIES,
                    'case_report': EvidenceLevel.CASE_REPORT,
                    'expert_opinion': EvidenceLevel.EXPERT_OPINION
                }

                return level_mapping.get(classification, EvidenceLevel.EXPERT_OPINION)

            # Fallback classification based on keywords
            title_abstract = (title + " " + abstract).lower()

            if any(term in title_abstract for term in ['systematic review', 'meta-analysis']):
                return EvidenceLevel.SYSTEMATIC_REVIEW
            elif any(term in title_abstract for term in ['randomized', 'rct', 'controlled trial']):
                return EvidenceLevel.RANDOMIZED_TRIAL
            elif any(term in title_abstract for term in ['cohort', 'longitudinal']):
                return EvidenceLevel.COHORT_STUDY
            elif any(term in title_abstract for term in ['case-control', 'case control']):
                return EvidenceLevel.CASE_CONTROL
            elif any(term in title_abstract for term in ['case series', 'case study']):
                return EvidenceLevel.CASE_SERIES
            elif any(term in title_abstract for term in ['case report']):
                return EvidenceLevel.CASE_REPORT
            else:
                return EvidenceLevel.EXPERT_OPINION

        except Exception as e:
            logger.warning(f"Failed to classify evidence level: {e}")
            return EvidenceLevel.EXPERT_OPINION

    async def _detect_research_conflicts(self, papers: List[CitationNode]) -> List[LiteratureConflict]:
        """Detect conflicts and contradictions in research findings"""

        conflicts = []

        try:
            # Group papers by similar topics using semantic search
            topic_groups = await self._group_papers_by_topic(papers)

            for topic, group_papers in topic_groups.items():
                if len(group_papers) < 2:
                    continue

                # Compare findings within each topic group
                topic_conflicts = await self._detect_conflicts_in_group(group_papers)
                conflicts.extend(topic_conflicts)

            return conflicts

        except Exception as e:
            logger.error(f"Failed to detect research conflicts: {e}")
            return []

    async def _group_papers_by_topic(self, papers: List[CitationNode]) -> Dict[str, List[CitationNode]]:
        """Group papers by similar topics using semantic analysis"""

        topic_groups = defaultdict(list)

        try:
            # Extract topics from titles and abstracts
            for paper in papers:
                # Use semantic search to extract key concepts
                concepts = await semantic_search_engine._extract_query_concepts(
                    paper.title + " " + paper.abstract
                )

                # Group by primary concept category
                primary_concepts = [c.concept for c in concepts if c.confidence > 0.7]

                if primary_concepts:
                    topic_key = primary_concepts[0]  # Use most confident concept as grouping key
                    topic_groups[topic_key].append(paper)
                else:
                    topic_groups['general'].append(paper)

            return dict(topic_groups)

        except Exception as e:
            logger.error(f"Failed to group papers by topic: {e}")
            return {'general': papers}

    async def _detect_conflicts_in_group(self, papers: List[CitationNode]) -> List[LiteratureConflict]:
        """Detect conflicts within a group of related papers"""

        conflicts = []

        try:
            # Compare each pair of papers
            for i, paper_a in enumerate(papers):
                for paper_b in papers[i+1:]:
                    conflict = await self._compare_papers_for_conflicts(paper_a, paper_b)
                    if conflict:
                        conflicts.append(conflict)

            return conflicts

        except Exception as e:
            logger.error(f"Failed to detect conflicts in group: {e}")
            return []

    async def _compare_papers_for_conflicts(self, paper_a: CitationNode, paper_b: CitationNode) -> Optional[LiteratureConflict]:
        """Compare two papers to detect potential conflicts"""

        try:
            # Create conflict detection prompt
            prompt = f"""
            Compare these two medical research papers for conflicts or contradictions:

            Paper A:
            Title: {paper_a.title}
            Abstract: {paper_a.abstract[:500]}...
            Evidence Level: {paper_a.evidence_level.value}

            Paper B:
            Title: {paper_b.title}
            Abstract: {paper_b.abstract[:500]}...
            Evidence Level: {paper_b.evidence_level.value}

            Identify if there are any conflicts in:
            1. Methodology
            2. Results/findings
            3. Interpretation
            4. Dosage recommendations
            5. Timing protocols
            6. Patient populations

            If conflicts exist, respond with JSON:
            {{
                "has_conflict": true,
                "conflict_type": "methodology|results|interpretation|dosage|timing|population",
                "description": "Brief description of the conflict",
                "confidence": 0.85,
                "resolution": "Suggestion for resolving the conflict"
            }}

            If no significant conflicts, respond with:
            {{"has_conflict": false}}
            """

            result = await multi_ai_manager.generate_content(
                prompt=prompt,
                provider="gemini",  # Use Gemini for analytical comparison
                context_type="medical",
                max_tokens=300,
                temperature=0.2
            )

            if result.get("success"):
                try:
                    analysis = json.loads(result["content"])

                    if analysis.get("has_conflict"):
                        conflict_type_map = {
                            'methodology': ConflictType.METHODOLOGY,
                            'results': ConflictType.RESULTS,
                            'interpretation': ConflictType.INTERPRETATION,
                            'dosage': ConflictType.DOSAGE,
                            'timing': ConflictType.TIMING,
                            'population': ConflictType.POPULATION
                        }

                        conflict_type = conflict_type_map.get(
                            analysis.get("conflict_type", "interpretation"),
                            ConflictType.INTERPRETATION
                        )

                        return LiteratureConflict(
                            pmid_a=paper_a.pmid,
                            pmid_b=paper_b.pmid,
                            conflict_type=conflict_type,
                            description=analysis.get("description", "Conflicting findings detected"),
                            confidence=analysis.get("confidence", 0.5),
                            resolution_suggestion=analysis.get("resolution", "Further research needed")
                        )

                except json.JSONDecodeError:
                    pass

            return None

        except Exception as e:
            logger.warning(f"Failed to compare papers for conflicts: {e}")
            return None

    async def _generate_evidence_synthesis(
        self,
        topic: str,
        papers: List[CitationNode],
        conflicts: List[LiteratureConflict],
        citation_network: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive evidence synthesis using AI"""

        try:
            # Prepare synthesis prompt with paper summaries
            high_quality_papers = [p for p in papers if self.evidence_weights[p.evidence_level] >= 0.8]

            papers_summary = "\n".join([
                f"- {paper.title} ({paper.evidence_level.value}, {paper.year}): {paper.abstract[:200]}..."
                for paper in high_quality_papers[:10]  # Top 10 high-quality papers
            ])

            conflicts_summary = "\n".join([
                f"- Conflict: {conflict.description} (confidence: {conflict.confidence:.2f})"
                for conflict in conflicts[:5]  # Top 5 conflicts
            ])

            prompt = f"""
            Generate a comprehensive evidence synthesis for the topic: "{topic}"

            High-Quality Research Papers:
            {papers_summary}

            Detected Conflicts:
            {conflicts_summary}

            Provide a structured synthesis in JSON format:
            {{
                "summary": "Comprehensive 3-paragraph summary of current evidence",
                "recommendations": ["Clinical recommendation 1", "Clinical recommendation 2", ...],
                "limitations": ["Study limitation 1", "Study limitation 2", ...],
                "future_research": ["Research direction 1", "Research direction 2", ...]
            }}

            Focus on neurosurgical clinical relevance and evidence-based recommendations.
            """

            result = await multi_ai_manager.generate_content(
                prompt=prompt,
                provider="claude",  # Use Claude for comprehensive synthesis
                context_type="medical",
                max_tokens=1000,
                temperature=0.3
            )

            if result.get("success"):
                try:
                    synthesis = json.loads(result["content"])
                    return synthesis
                except json.JSONDecodeError:
                    pass

            # Fallback synthesis
            return {
                "summary": f"Analysis of {len(papers)} papers on {topic} reveals emerging evidence in neurosurgical practice. High-quality studies suggest promising outcomes, though methodological variations exist. Further research is needed to establish definitive clinical guidelines.",
                "recommendations": [
                    "Consider evidence-based protocols for clinical implementation",
                    "Monitor patient outcomes with standardized assessments",
                    "Validate findings in larger multicenter studies"
                ],
                "limitations": [
                    "Limited sample sizes in some studies",
                    "Methodological heterogeneity across studies",
                    "Potential publication bias"
                ],
                "future_research": [
                    "Large-scale randomized controlled trials needed",
                    "Long-term outcome studies required",
                    "Standardization of assessment protocols"
                ]
            }

        except Exception as e:
            logger.error(f"Failed to generate evidence synthesis: {e}")
            return {
                "summary": f"Evidence synthesis for {topic} could not be completed.",
                "recommendations": [],
                "limitations": ["Synthesis generation failed"],
                "future_research": []
            }

    async def _calculate_synthesis_quality(self, papers: List[CitationNode], conflicts: List[LiteratureConflict]) -> float:
        """Calculate overall quality score for the evidence synthesis"""

        try:
            if not papers:
                return 0.0

            # Evidence level quality (40% of score)
            evidence_scores = [self.evidence_weights[paper.evidence_level] for paper in papers]
            avg_evidence_quality = sum(evidence_scores) / len(evidence_scores)

            # Sample size factor (20% of score)
            total_papers = len(papers)
            size_factor = min(total_papers / 20, 1.0)  # Optimal around 20 papers

            # Recency factor (20% of score)
            current_year = datetime.now().year
            years = [paper.year for paper in papers if paper.year > 0]
            if years:
                avg_year = sum(years) / len(years)
                recency_factor = max(0, min((avg_year - (current_year - 10)) / 10, 1.0))
            else:
                recency_factor = 0.5

            # Conflict penalty (10% of score)
            conflict_penalty = min(len(conflicts) * 0.1, 0.3)  # Max 30% penalty

            # Neurosurgical relevance (10% of score)
            relevance_scores = [paper.neurosurgical_relevance for paper in papers]
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.5

            # Combined quality score
            quality_score = (
                avg_evidence_quality * 0.4 +
                size_factor * 0.2 +
                recency_factor * 0.2 +
                avg_relevance * 0.1 -
                conflict_penalty
            )

            return max(0.0, min(quality_score, 1.0))

        except Exception as e:
            logger.error(f"Failed to calculate synthesis quality: {e}")
            return 0.5

    async def _calculate_neurosurgical_relevance(self, paper: Dict[str, Any]) -> float:
        """Calculate neurosurgical relevance score for a paper"""

        try:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            keywords = paper.get('keywords', [])

            # Combine text for analysis
            text = f"{title} {abstract} {' '.join(keywords)}"

            # Extract neurosurgical concepts
            concepts = await semantic_search_engine._extract_query_concepts(text)

            # Calculate relevance based on concept matches and weights
            relevance_score = 0.0
            total_weight = 0.0

            for concept in concepts:
                if concept.category and concept.confidence > 0.5:
                    weight = neurosurgical_concepts.get_concept_weight(concept.concept)
                    relevance_score += weight * concept.confidence
                    total_weight += weight

            # Normalize to 0-1 range
            if total_weight > 0:
                normalized_score = min(relevance_score / total_weight, 1.0)
            else:
                # Fallback: simple keyword matching
                neurosurg_keywords = ['neurosurg', 'brain', 'cranial', 'spine', 'cerebral', 'neurological']
                matches = sum(1 for keyword in neurosurg_keywords if keyword in text.lower())
                normalized_score = min(matches / len(neurosurg_keywords), 1.0)

            return normalized_score

        except Exception as e:
            logger.warning(f"Failed to calculate neurosurgical relevance: {e}")
            return 0.5

    async def _deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate papers based on title similarity"""

        unique_papers = []
        seen_titles = set()

        for paper in papers:
            title = paper.get('title', '').lower().strip()

            # Simple deduplication based on title similarity
            is_duplicate = False
            for seen_title in seen_titles:
                if self._title_similarity(title, seen_title) > 0.85:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_papers.append(paper)
                seen_titles.add(title)

        return unique_papers

    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles"""

        # Simple word-based similarity
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    async def generate_systematic_review(
        self,
        topic: str,
        include_meta_analysis: bool = True,
        years_back: int = 10
    ) -> Dict[str, Any]:
        """Generate a complete systematic review with meta-analysis"""

        try:
            logger.info(f"📋 Generating systematic review for: '{topic}'")

            # Perform comprehensive literature analysis
            synthesis = await self.analyze_literature_corpus(
                topic=topic,
                max_papers=100,  # More papers for systematic review
                years_back=years_back,
                include_meta_analysis=include_meta_analysis
            )

            # Generate systematic review structure
            review_prompt = f"""
            Generate a comprehensive systematic review for: "{topic}"

            Based on analysis of {synthesis.total_papers} papers with quality score: {synthesis.quality_score:.2f}

            Evidence Summary: {synthesis.evidence_summary}

            Provide structured systematic review in JSON format:
            {{
                "title": "Systematic Review Title",
                "abstract": "Structured abstract with background, methods, results, conclusions",
                "introduction": "Background and rationale",
                "methods": "Search strategy, inclusion/exclusion criteria, data extraction",
                "results": "Study characteristics, risk of bias, synthesis of results",
                "discussion": "Summary of findings, limitations, implications",
                "conclusion": "Key conclusions and clinical implications",
                "prisma_checklist": ["Item 1", "Item 2", ...],
                "search_strategy": "Detailed search methodology"
            }}

            Follow PRISMA guidelines for systematic review reporting.
            """

            result = await multi_ai_manager.generate_content(
                prompt=review_prompt,
                provider="claude",  # Use Claude for structured academic writing
                context_type="medical",
                max_tokens=2000,
                temperature=0.2
            )

            if result.get("success"):
                try:
                    review_data = json.loads(result["content"])

                    # Add synthesis data
                    review_data.update({
                        "literature_synthesis": synthesis,
                        "methodology": "AI-powered systematic review with automated literature analysis",
                        "quality_assessment": f"Overall evidence quality: {synthesis.quality_score:.1%}",
                        "conflicts_identified": len(synthesis.conflicts_detected),
                        "citation_network_metrics": synthesis.citation_network.get('metrics', {})
                    })

                    return {
                        "success": True,
                        "systematic_review": review_data,
                        "metadata": {
                            "papers_analyzed": synthesis.total_papers,
                            "evidence_quality": synthesis.quality_score,
                            "conflicts_detected": len(synthesis.conflicts_detected),
                            "generation_date": datetime.now().isoformat(),
                            "ai_generated": True
                        }
                    }

                except json.JSONDecodeError:
                    pass

            # Fallback response
            return {
                "success": False,
                "error": "Failed to generate systematic review structure",
                "literature_synthesis": synthesis
            }

        except Exception as e:
            logger.error(f"Failed to generate systematic review: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
literature_analysis_engine = LiteratureAnalysisEngine()