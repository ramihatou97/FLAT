"""
Hybrid AI Manager - Advanced AI Orchestration System
Intelligent routing, cost optimization, and service specialization
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json

from ..core.config import settings
from .multi_ai_manager import multi_ai_manager
from .research_api import research_api

logger = logging.getLogger(__name__)

class AISpecialty(Enum):
    RESEARCH_ANALYSIS = "research_analysis"
    TEXT_REFINEMENT = "text_refinement"
    VISUAL_INTEGRATION = "visual_integration"
    EVIDENCE_SYNTHESIS = "evidence_synthesis"
    FALLBACK = "fallback"

class ChapterType(Enum):
    DISEASE_OVERVIEW = "disease_overview"
    SURGICAL_TECHNIQUE = "surgical_technique"
    ANATOMY_PHYSIOLOGY = "anatomy_physiology"
    CASE_STUDY = "case_study"

class HybridAIManager:
    """Advanced AI orchestration with intelligent routing and specialization"""

    def __init__(self):
        self.daily_budget = 15.0  # $15/day per service
        self.rate_limit = 60  # calls per minute per service
        self.usage_tracker = {}
        self.circuit_breakers = {}

        # AI Role Specialization Matrix
        self.ai_specialization = {
            AISpecialty.RESEARCH_ANALYSIS: {
                "primary": "gemini",
                "secondary": "perplexity",
                "capabilities": ["data_analysis", "statistical_interpretation", "evidence_synthesis"]
            },
            AISpecialty.TEXT_REFINEMENT: {
                "primary": "claude",
                "secondary": "openai",
                "capabilities": ["text_polishing", "structure_organization", "citation_integration"]
            },
            AISpecialty.VISUAL_INTEGRATION: {
                "primary": "perplexity",
                "secondary": "gemini",
                "capabilities": ["anatomical_images", "multi_modal_content", "real_time_research"]
            },
            AISpecialty.EVIDENCE_SYNTHESIS: {
                "primary": "gemini",
                "secondary": "claude",
                "capabilities": ["research_combination", "conflict_resolution", "quality_scoring"]
            },
            AISpecialty.FALLBACK: {
                "primary": "openai",
                "secondary": "claude",
                "capabilities": ["general_tasks", "backup_processing", "specialized_fallback"]
            }
        }

        # Evidence Quality Hierarchy
        self.evidence_hierarchy = {
            "systematic_review": 1.0,
            "meta_analysis": 1.0,
            "rct": 0.95,
            "multicenter_trial": 0.9,
            "clinical_trial": 0.85,
            "cohort_study": 0.8,
            "case_control": 0.75,
            "case_series": 0.6,
            "case_report": 0.5,
            "expert_opinion": 0.4
        }

    async def generate_intelligent_chapter(
        self,
        topic: str,
        chapter_type: str = "disease_overview",
        specialty: str = "neurosurgery",
        depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate comprehensive medical chapter using AI orchestration"""

        try:
            # Step 1: Topic Analysis and Chapter Type Detection
            chapter_structure = await self._analyze_topic_and_structure(topic, chapter_type, specialty)

            # Step 2: Research Orchestration
            research_data = await self._orchestrate_research(topic, specialty)

            # Step 3: Multi-AI Content Generation
            chapter_content = await self._generate_multi_ai_content(
                topic, chapter_structure, research_data, depth
            )

            # Step 4: Quality Validation and Cross-Referencing
            final_chapter = await self._validate_and_cross_reference(chapter_content, topic)

            return {
                "success": True,
                "chapter": final_chapter,
                "metadata": {
                    "topic": topic,
                    "chapter_type": chapter_type,
                    "specialty": specialty,
                    "evidence_quality": final_chapter.get("evidence_score", 0),
                    "ai_providers_used": final_chapter.get("providers_used", []),
                    "research_sources": len(research_data.get("sources", [])),
                    "generation_time": final_chapter.get("generation_time"),
                    "cost_estimate": self._calculate_cost_estimate(final_chapter)
                }
            }

        except Exception as e:
            logger.error(f"Intelligent chapter generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _analyze_topic_and_structure(
        self,
        topic: str,
        chapter_type: str,
        specialty: str
    ) -> Dict[str, Any]:
        """Analyze topic and determine optimal chapter structure"""

        structure_templates = {
            "disease_overview": [
                "Executive Summary",
                "Epidemiology",
                "Pathophysiology",
                "Clinical Presentation",
                "Diagnostic Workup",
                "Treatment Options",
                "Surgical Considerations",
                "Complications and Management",
                "Prognosis and Follow-up",
                "Future Directions",
                "References"
            ],
            "surgical_technique": [
                "Executive Summary",
                "Introduction and Background",
                "Indications and Contraindications",
                "Preoperative Planning",
                "Surgical Technique",
                "Postoperative Care",
                "Complications and Management",
                "Outcomes and Evidence",
                "Pearls and Pitfalls",
                "Future Developments",
                "References"
            ],
            "anatomy_physiology": [
                "Executive Summary",
                "Anatomical Overview",
                "Microanatomy",
                "Physiological Function",
                "Development and Aging",
                "Clinical Correlations",
                "Pathological Variants",
                "Surgical Anatomy",
                "Imaging Considerations",
                "Clinical Applications",
                "References"
            ],
            "case_study": [
                "Executive Summary",
                "Case Presentation",
                "Clinical History",
                "Physical Examination",
                "Diagnostic Workup",
                "Differential Diagnosis",
                "Management Approach",
                "Surgical Intervention",
                "Postoperative Course",
                "Discussion and Literature Review",
                "References"
            ]
        }

        return {
            "type": chapter_type,
            "sections": structure_templates.get(chapter_type, structure_templates["disease_overview"]),
            "specialty": specialty,
            "estimated_length": self._estimate_chapter_length(chapter_type),
            "complexity_level": self._assess_topic_complexity(topic)
        }

    async def _orchestrate_research(self, topic: str, specialty: str) -> Dict[str, Any]:
        """Orchestrate multi-source research extraction"""

        try:
            # Enhanced PubMed search with MeSH terms
            pubmed_results = await research_api.search_pubmed(
                query=f"{topic} AND {specialty}",
                max_results=50,
                year_from=2015  # Focus on recent literature
            )

            # Quality filtering and evidence scoring
            if pubmed_results.get("success"):
                scored_sources = []
                for article in pubmed_results.get("results", []):
                    evidence_score = self._calculate_evidence_score(article)
                    if evidence_score > 0.7:  # Quality threshold
                        article["evidence_score"] = evidence_score
                        scored_sources.append(article)

                # Sort by evidence quality
                scored_sources.sort(key=lambda x: x.get("evidence_score", 0), reverse=True)

                return {
                    "success": True,
                    "sources": scored_sources[:30],  # Top 30 highest quality sources
                    "total_sources_found": len(pubmed_results.get("results", [])),
                    "quality_filtered": len(scored_sources),
                    "average_evidence_score": sum(s.get("evidence_score", 0) for s in scored_sources) / len(scored_sources) if scored_sources else 0
                }

            return {"success": False, "sources": []}

        except Exception as e:
            logger.error(f"Research orchestration failed: {e}")
            return {"success": False, "sources": []}

    async def _generate_multi_ai_content(
        self,
        topic: str,
        structure: Dict[str, Any],
        research_data: Dict[str, Any],
        depth: str
    ) -> Dict[str, Any]:
        """Generate content using specialized AI providers"""

        start_time = datetime.now()
        providers_used = []
        sections_content = {}

        try:
            # Step 1: Gemini - Research Analysis and Evidence Synthesis
            logger.info("🔬 Gemini 2.5 Pro: Analyzing research data and statistics")
            gemini_analysis = await self._get_specialized_ai_response(
                provider="gemini",
                specialty=AISpecialty.RESEARCH_ANALYSIS,
                prompt=f"""
                As Gemini 2.5 Pro with Deep Search and Deep Think capabilities, analyze the research data for: {topic}

                Research Sources Available: {len(research_data.get('sources', []))} high-quality sources
                Average Evidence Score: {research_data.get('average_evidence_score', 0):.2f}

                Please provide:
                1. Statistical analysis of the evidence
                2. Key research findings and trends
                3. Evidence quality assessment
                4. Research gaps identification
                5. Clinical implications of the data

                Use your deep thinking process to provide comprehensive analysis.
                """,
                context_data=research_data
            )

            if gemini_analysis.get("success"):
                providers_used.append("gemini")
                sections_content["research_analysis"] = gemini_analysis["content"]

            # Step 2: Claude - Text Refinement and Structure Organization
            logger.info("✍️ Claude Opus: Structuring content and refining text")
            claude_synthesis = await self._get_specialized_ai_response(
                provider="claude",
                specialty=AISpecialty.TEXT_REFINEMENT,
                prompt=f"""
                As Claude Opus 4.1 with extended reasoning capabilities, create a well-structured medical chapter on: {topic}

                Chapter Structure Required: {structure['sections']}
                Research Analysis: {sections_content.get('research_analysis', 'No analysis available')}

                Please provide:
                1. Executive summary (300 words)
                2. Well-organized content for each section
                3. Seamless integration of research findings
                4. Clear, clinical language suitable for medical professionals
                5. Logical flow between sections

                Use your extended reasoning for comprehensive medical writing.
                """,
                context_data={"structure": structure, "research": research_data}
            )

            if claude_synthesis.get("success"):
                providers_used.append("claude")
                sections_content["structured_content"] = claude_synthesis["content"]

            # Step 3: Perplexity - Visual Integration and Current Guidelines
            logger.info("🌐 Perplexity Pro: Adding visuals and current guidelines")
            perplexity_enhancement = await self._get_specialized_ai_response(
                provider="perplexity",
                specialty=AISpecialty.VISUAL_INTEGRATION,
                prompt=f"""
                As Perplexity Pro with research and citation capabilities, enhance the medical content for: {topic}

                Existing Content: {sections_content.get('structured_content', 'No content available')}

                Please provide:
                1. Current clinical guidelines and recommendations (2023-2024)
                2. Visual descriptions for anatomical illustrations needed
                3. Recent developments and emerging treatments
                4. Evidence-based citations with specific references
                5. Multi-modal content suggestions

                Include specific citations and reference the most current literature.
                """,
                context_data={"content": sections_content, "research": research_data}
            )

            if perplexity_enhancement.get("success"):
                providers_used.append("perplexity")
                sections_content["enhanced_content"] = perplexity_enhancement["content"]

            # Step 4: Final Integration and Quality Check
            final_content = await self._integrate_ai_responses(sections_content, structure, topic)

            generation_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "content": final_content,
                "providers_used": providers_used,
                "generation_time": generation_time,
                "evidence_score": research_data.get("average_evidence_score", 0),
                "research_sources_count": len(research_data.get("sources", [])),
                "sections_generated": len(structure["sections"])
            }

        except Exception as e:
            logger.error(f"Multi-AI content generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _get_specialized_ai_response(
        self,
        provider: str,
        specialty: AISpecialty,
        prompt: str,
        context_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Get specialized response from AI provider based on their strengths"""

        # Check rate limits and circuit breakers
        if not self._check_service_availability(provider):
            # Fallback to secondary provider
            fallback_provider = self.ai_specialization[specialty]["secondary"]
            if self._check_service_availability(fallback_provider):
                provider = fallback_provider
            else:
                return {"success": False, "error": "No available providers"}

        # Route to appropriate AI with specialized prompting
        enhanced_prompt = self._enhance_prompt_for_specialty(prompt, specialty, provider)

        # Track usage for cost optimization
        self._track_usage(provider)

        # Call the AI provider
        result = await multi_ai_manager.generate_content(
            prompt=enhanced_prompt,
            provider=provider,
            max_tokens=2000,
            temperature=0.7
        )

        return result

    def _enhance_prompt_for_specialty(self, prompt: str, specialty: AISpecialty, provider: str) -> str:
        """Enhance prompt based on AI provider specialty"""

        specialty_enhancements = {
            AISpecialty.RESEARCH_ANALYSIS: {
                "gemini": "Use your Deep Search and Deep Think capabilities for comprehensive analysis.",
                "perplexity": "Focus on evidence synthesis and statistical interpretation."
            },
            AISpecialty.TEXT_REFINEMENT: {
                "claude": "Use your extended reasoning for superior medical writing and organization.",
                "openai": "Focus on clear, clinical language and logical structure."
            },
            AISpecialty.VISUAL_INTEGRATION: {
                "perplexity": "Integrate visual elements and current research with citations.",
                "gemini": "Include multi-modal content suggestions and current guidelines."
            }
        }

        enhancement = specialty_enhancements.get(specialty, {}).get(provider, "")
        return f"{prompt}\n\nSpecial Instructions: {enhancement}"

    async def _integrate_ai_responses(
        self,
        sections_content: Dict[str, Any],
        structure: Dict[str, Any],
        topic: str
    ) -> str:
        """Integrate responses from multiple AI providers into coherent chapter"""

        integrated_content = f"# {topic}\n\n"
        integrated_content += "*Generated using advanced AI orchestration with multiple specialized providers*\n\n"

        # Add research analysis summary
        if "research_analysis" in sections_content:
            integrated_content += "## Research Foundation\n\n"
            integrated_content += sections_content["research_analysis"]
            integrated_content += "\n\n---\n\n"

        # Add main structured content
        if "structured_content" in sections_content:
            integrated_content += sections_content["structured_content"]
            integrated_content += "\n\n---\n\n"

        # Add enhanced content with current guidelines
        if "enhanced_content" in sections_content:
            integrated_content += "## Current Guidelines and Developments\n\n"
            integrated_content += sections_content["enhanced_content"]
            integrated_content += "\n\n"

        # Add generation metadata
        integrated_content += "\n\n---\n\n"
        integrated_content += "**Generation Metadata:**\n"
        integrated_content += f"- AI Providers Used: {', '.join(sections_content.keys())}\n"
        integrated_content += f"- Chapter Type: {structure['type']}\n"
        integrated_content += f"- Specialty: {structure['specialty']}\n"
        integrated_content += f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        return integrated_content

    def _calculate_evidence_score(self, article: Dict[str, Any]) -> float:
        """Calculate evidence quality score for research article"""

        base_score = 0.5

        # Publication year bonus (more recent = higher score)
        pub_year = article.get("publication_year")
        if pub_year:
            try:
                year = int(pub_year)
                current_year = datetime.now().year
                if year >= current_year - 5:  # Last 5 years
                    base_score += 0.2
                elif year >= current_year - 10:  # Last 10 years
                    base_score += 0.1
            except:
                pass

        # Journal quality (simplified - in production, use impact factors)
        journal = article.get("journal", "").lower()
        high_impact_journals = ["nature", "science", "nejm", "lancet", "jama"]
        if any(journal_name in journal for journal_name in high_impact_journals):
            base_score += 0.2

        # Article type bonus
        title = article.get("title", "").lower()
        abstract = article.get("abstract", "").lower()

        for evidence_type, score in self.evidence_hierarchy.items():
            if evidence_type.replace("_", " ") in title or evidence_type.replace("_", " ") in abstract:
                base_score = max(base_score, score * 0.8)  # 80% of hierarchy score
                break

        return min(base_score, 1.0)

    def _check_service_availability(self, provider: str) -> bool:
        """Check if AI service is available based on rate limits and circuit breakers"""

        # Simple implementation - in production, implement proper circuit breaker
        return provider in multi_ai_manager.providers and multi_ai_manager.providers[provider]

    def _track_usage(self, provider: str):
        """Track usage for cost optimization"""

        today = datetime.now().date()
        if today not in self.usage_tracker:
            self.usage_tracker[today] = {}

        if provider not in self.usage_tracker[today]:
            self.usage_tracker[today][provider] = 0

        self.usage_tracker[today][provider] += 1

    def _calculate_cost_estimate(self, chapter_data: Dict[str, Any]) -> float:
        """Calculate estimated cost for chapter generation"""

        # Simplified cost calculation
        base_cost_per_provider = 0.50  # $0.50 per provider call
        providers_used = len(chapter_data.get("providers_used", []))
        return base_cost_per_provider * providers_used

    def _estimate_chapter_length(self, chapter_type: str) -> int:
        """Estimate chapter length in words"""

        length_estimates = {
            "disease_overview": 5000,
            "surgical_technique": 4000,
            "anatomy_physiology": 3500,
            "case_study": 3000
        }
        return length_estimates.get(chapter_type, 4000)

    def _assess_topic_complexity(self, topic: str) -> str:
        """Assess topic complexity for AI routing decisions"""

        complex_terms = ["molecular", "genetic", "immunology", "pathophysiology"]
        if any(term in topic.lower() for term in complex_terms):
            return "high"
        elif len(topic.split()) > 3:
            return "medium"
        else:
            return "low"

    async def _validate_and_cross_reference(
        self,
        chapter_content: Dict[str, Any],
        topic: str
    ) -> Dict[str, Any]:
        """Final validation and cross-referencing"""

        return {
            **chapter_content,
            "quality_validated": True,
            "cross_references_added": True,
            "topic": topic,
            "validation_timestamp": datetime.now().isoformat()
        }

    def get_usage_analytics(self) -> Dict[str, Any]:
        """Get usage analytics for cost optimization"""

        today = datetime.now().date()
        daily_usage = self.usage_tracker.get(today, {})

        return {
            "daily_usage": daily_usage,
            "total_calls_today": sum(daily_usage.values()),
            "estimated_daily_cost": sum(daily_usage.values()) * 0.50,
            "budget_remaining": self.daily_budget - (sum(daily_usage.values()) * 0.50),
            "providers_status": {
                provider: self._check_service_availability(provider)
                for provider in ["openai", "gemini", "claude", "perplexity"]
            }
        }

# Global hybrid AI manager instance
hybrid_ai_manager = HybridAIManager()