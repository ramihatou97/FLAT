"""
Research Workflow Automation Engine
AI-powered research methodology, hypothesis generation, and experimental design
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .multi_ai_manager import multi_ai_manager
from .literature_analysis_engine import literature_analysis_engine
from .semantic_search_engine import semantic_search_engine
from .neurosurgical_concepts import neurosurgical_concepts

logger = logging.getLogger(__name__)

class StudyType(Enum):
    RANDOMIZED_TRIAL = "randomized_trial"
    COHORT_STUDY = "cohort_study"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    CASE_SERIES = "case_series"
    EXPERIMENTAL = "experimental"

class ResearchPhase(Enum):
    CONCEPTUALIZATION = "conceptualization"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    METHODOLOGY_DESIGN = "methodology_design"
    PROTOCOL_DEVELOPMENT = "protocol_development"
    STATISTICAL_PLANNING = "statistical_planning"
    PROPOSAL_WRITING = "proposal_writing"

class FundingType(Enum):
    NIH = "nih"
    NSF = "nsf"
    PRIVATE_FOUNDATION = "private_foundation"
    INDUSTRY = "industry"
    INSTITUTIONAL = "institutional"
    INTERNATIONAL = "international"

@dataclass
class ResearchHypothesis:
    primary_hypothesis: str
    secondary_hypotheses: List[str]
    null_hypothesis: str
    alternative_hypothesis: str
    testable_predictions: List[str]
    potential_confounders: List[str]
    strength_of_evidence: float
    novelty_score: float

@dataclass
class StudyDesign:
    study_type: StudyType
    sample_size: int
    power_analysis: Dict[str, Any]
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    primary_endpoints: List[str]
    secondary_endpoints: List[str]
    statistical_methods: List[str]
    timeline: Dict[str, str]
    feasibility_score: float

@dataclass
class GrantProposal:
    title: str
    specific_aims: List[str]
    background_significance: str
    innovation: str
    approach: str
    budget_summary: Dict[str, float]
    timeline: Dict[str, str]
    potential_funding_sources: List[Dict[str, Any]]
    success_probability: float

@dataclass
class ResearchWorkflow:
    research_question: str
    hypothesis: ResearchHypothesis
    study_design: StudyDesign
    grant_proposal: GrantProposal
    methodology_recommendations: List[str]
    risk_assessment: Dict[str, Any]
    quality_score: float

class ResearchWorkflowEngine:
    """
    AI-powered research workflow automation for neurosurgical research
    Provides end-to-end research planning and methodology assistance
    """

    def __init__(self):
        self.funding_databases = {
            FundingType.NIH: {
                "neurosurgery_focus": ["NINDS", "NCI", "NIMH"],
                "typical_amounts": {"R01": 250000, "R21": 100000, "K08": 150000},
                "success_rates": {"R01": 0.18, "R21": 0.15, "K08": 0.25}
            },
            FundingType.NSF: {
                "neurosurgery_focus": ["Engineering", "Computer Science", "Biology"],
                "typical_amounts": {"Standard": 200000, "CAREER": 500000},
                "success_rates": {"Standard": 0.22, "CAREER": 0.15}
            },
            FundingType.PRIVATE_FOUNDATION: {
                "neurosurgery_focus": ["Brain & Behavior", "Michael J. Fox", "Dana Foundation"],
                "typical_amounts": {"Small": 50000, "Medium": 150000, "Large": 300000},
                "success_rates": {"Small": 0.30, "Medium": 0.20, "Large": 0.12}
            }
        }

        # Cache for workflow analysis
        self.workflow_cache = {}

    async def generate_research_workflow(
        self,
        research_question: str,
        specialty: str = "neurosurgery",
        study_preferences: Optional[Dict[str, Any]] = None
    ) -> ResearchWorkflow:
        """
        Generate comprehensive research workflow from research question
        """

        try:
            logger.info(f"🔬 Generating research workflow for: '{research_question}'")

            # Step 1: Analyze research landscape
            literature_context = await self._analyze_research_landscape(research_question)

            # Step 2: Generate hypotheses
            hypothesis = await self._generate_research_hypothesis(research_question, literature_context)

            # Step 3: Design study methodology
            study_design = await self._design_study_methodology(
                research_question, hypothesis, study_preferences
            )

            # Step 4: Generate grant proposal framework
            grant_proposal = await self._generate_grant_proposal(
                research_question, hypothesis, study_design
            )

            # Step 5: Provide methodology recommendations
            recommendations = await self._generate_methodology_recommendations(
                research_question, study_design
            )

            # Step 6: Assess research risks
            risk_assessment = await self._assess_research_risks(study_design)

            # Step 7: Calculate overall quality score
            quality_score = await self._calculate_workflow_quality(
                hypothesis, study_design, grant_proposal
            )

            workflow = ResearchWorkflow(
                research_question=research_question,
                hypothesis=hypothesis,
                study_design=study_design,
                grant_proposal=grant_proposal,
                methodology_recommendations=recommendations,
                risk_assessment=risk_assessment,
                quality_score=quality_score
            )

            # Cache the workflow
            cache_key = f"{research_question}_{specialty}"
            self.workflow_cache[cache_key] = workflow

            logger.info(f"✅ Research workflow generated (quality: {quality_score:.2f})")
            return workflow

        except Exception as e:
            logger.error(f"❌ Research workflow generation failed: {e}")
            raise

    async def _analyze_research_landscape(self, research_question: str) -> Dict[str, Any]:
        """Analyze existing research landscape for the question"""

        try:
            # Use literature analysis engine for rapid landscape analysis
            synthesis = await literature_analysis_engine.analyze_literature_corpus(
                topic=research_question,
                max_papers=20,  # Quick analysis
                years_back=5,   # Recent research
                include_meta_analysis=False
            )

            # Extract key insights
            landscape = {
                "existing_evidence": synthesis.evidence_summary,
                "research_gaps": synthesis.future_research,
                "conflicts_identified": len(synthesis.conflicts_detected),
                "evidence_quality": synthesis.quality_score,
                "total_papers": synthesis.total_papers,
                "key_concepts": await self._extract_key_concepts(research_question)
            }

            return landscape

        except Exception as e:
            logger.warning(f"Failed to analyze research landscape: {e}")
            return {
                "existing_evidence": "Limited analysis available",
                "research_gaps": ["Further research needed"],
                "conflicts_identified": 0,
                "evidence_quality": 0.5,
                "total_papers": 0,
                "key_concepts": []
            }

    async def _extract_key_concepts(self, research_question: str) -> List[str]:
        """Extract key neurosurgical concepts from research question"""

        try:
            concepts = await semantic_search_engine._extract_query_concepts(research_question)
            key_concepts = [
                concept.concept for concept in concepts
                if concept.confidence > 0.7 and neurosurgical_concepts.is_neurosurgical_term(concept.concept)
            ]
            return key_concepts[:10]  # Top 10 most relevant concepts

        except Exception as e:
            logger.warning(f"Failed to extract key concepts: {e}")
            return []

    async def _generate_research_hypothesis(
        self,
        research_question: str,
        literature_context: Dict[str, Any]
    ) -> ResearchHypothesis:
        """Generate testable research hypotheses using AI"""

        try:
            # Create hypothesis generation prompt
            prompt = f"""
            Generate research hypotheses for this neurosurgical research question:

            Research Question: {research_question}

            Literature Context:
            - Existing evidence: {literature_context.get('existing_evidence', 'Limited')}
            - Research gaps: {literature_context.get('research_gaps', [])}
            - Evidence quality: {literature_context.get('evidence_quality', 0.5)}

            Generate comprehensive hypotheses in JSON format:
            {{
                "primary_hypothesis": "Main testable hypothesis with specific predictions",
                "secondary_hypotheses": ["Secondary hypothesis 1", "Secondary hypothesis 2"],
                "null_hypothesis": "Statistical null hypothesis",
                "alternative_hypothesis": "Alternative hypothesis if null is rejected",
                "testable_predictions": ["Specific measurable prediction 1", "Prediction 2"],
                "potential_confounders": ["Potential confounder 1", "Confounder 2"],
                "strength_of_evidence": 0.75,
                "novelty_score": 0.85
            }}

            Ensure hypotheses are:
            1. Testable and falsifiable
            2. Specific and measurable
            3. Grounded in existing literature
            4. Clinically relevant for neurosurgery
            """

            result = await multi_ai_manager.generate_content(
                prompt=prompt,
                provider="claude",  # Use Claude for structured academic thinking
                context_type="medical",
                max_tokens=800,
                temperature=0.3
            )

            if result.get("success"):
                try:
                    hypothesis_data = json.loads(result["content"])

                    return ResearchHypothesis(
                        primary_hypothesis=hypothesis_data.get("primary_hypothesis", ""),
                        secondary_hypotheses=hypothesis_data.get("secondary_hypotheses", []),
                        null_hypothesis=hypothesis_data.get("null_hypothesis", ""),
                        alternative_hypothesis=hypothesis_data.get("alternative_hypothesis", ""),
                        testable_predictions=hypothesis_data.get("testable_predictions", []),
                        potential_confounders=hypothesis_data.get("potential_confounders", []),
                        strength_of_evidence=hypothesis_data.get("strength_of_evidence", 0.5),
                        novelty_score=hypothesis_data.get("novelty_score", 0.5)
                    )

                except json.JSONDecodeError:
                    pass

            # Fallback hypothesis generation
            return ResearchHypothesis(
                primary_hypothesis=f"Investigation of {research_question} will demonstrate significant clinical outcomes",
                secondary_hypotheses=[
                    "Secondary measures will show improvement",
                    "Safety profile will be acceptable"
                ],
                null_hypothesis="No significant difference between groups",
                alternative_hypothesis="Significant difference exists between groups",
                testable_predictions=[
                    "Primary outcome will improve by >20%",
                    "Adverse events will be <5%"
                ],
                potential_confounders=["Age", "Comorbidities", "Prior treatments"],
                strength_of_evidence=0.6,
                novelty_score=0.7
            )

        except Exception as e:
            logger.error(f"Failed to generate research hypothesis: {e}")
            raise

    async def _design_study_methodology(
        self,
        research_question: str,
        hypothesis: ResearchHypothesis,
        preferences: Optional[Dict[str, Any]]
    ) -> StudyDesign:
        """Design optimal study methodology using AI"""

        try:
            # Determine optimal study type
            study_type = await self._recommend_study_type(research_question, hypothesis)

            # Create methodology design prompt
            prompt = f"""
            Design study methodology for this neurosurgical research:

            Research Question: {research_question}
            Primary Hypothesis: {hypothesis.primary_hypothesis}
            Study Type: {study_type.value}

            Design comprehensive methodology in JSON format:
            {{
                "sample_size": 120,
                "power_analysis": {{
                    "power": 0.8,
                    "alpha": 0.05,
                    "effect_size": 0.5,
                    "two_tailed": true
                }},
                "inclusion_criteria": ["Criterion 1", "Criterion 2"],
                "exclusion_criteria": ["Exclusion 1", "Exclusion 2"],
                "primary_endpoints": ["Primary endpoint 1"],
                "secondary_endpoints": ["Secondary endpoint 1", "Secondary endpoint 2"],
                "statistical_methods": ["Method 1", "Method 2"],
                "timeline": {{
                    "recruitment": "6 months",
                    "intervention": "12 months",
                    "follow_up": "6 months",
                    "analysis": "3 months"
                }},
                "feasibility_score": 0.75
            }}

            Consider:
            1. Adequate statistical power
            2. Realistic timeline and recruitment
            3. Appropriate endpoints for neurosurgery
            4. Ethical considerations
            """

            result = await multi_ai_manager.generate_content(
                prompt=prompt,
                provider="gemini",  # Use Gemini for analytical design
                context_type="medical",
                max_tokens=1000,
                temperature=0.2
            )

            if result.get("success"):
                try:
                    design_data = json.loads(result["content"])

                    return StudyDesign(
                        study_type=study_type,
                        sample_size=design_data.get("sample_size", 100),
                        power_analysis=design_data.get("power_analysis", {}),
                        inclusion_criteria=design_data.get("inclusion_criteria", []),
                        exclusion_criteria=design_data.get("exclusion_criteria", []),
                        primary_endpoints=design_data.get("primary_endpoints", []),
                        secondary_endpoints=design_data.get("secondary_endpoints", []),
                        statistical_methods=design_data.get("statistical_methods", []),
                        timeline=design_data.get("timeline", {}),
                        feasibility_score=design_data.get("feasibility_score", 0.7)
                    )

                except json.JSONDecodeError:
                    pass

            # Fallback study design
            return StudyDesign(
                study_type=study_type,
                sample_size=100,
                power_analysis={"power": 0.8, "alpha": 0.05, "effect_size": 0.5},
                inclusion_criteria=["Adult patients", "Diagnosed condition", "Informed consent"],
                exclusion_criteria=["Pregnancy", "Severe comorbidities", "Unable to consent"],
                primary_endpoints=["Primary clinical outcome"],
                secondary_endpoints=["Quality of life", "Safety measures"],
                statistical_methods=["t-test", "Chi-square", "Regression analysis"],
                timeline={
                    "recruitment": "6 months",
                    "intervention": "12 months",
                    "follow_up": "6 months",
                    "analysis": "3 months"
                },
                feasibility_score=0.7
            )

        except Exception as e:
            logger.error(f"Failed to design study methodology: {e}")
            raise

    async def _recommend_study_type(self, research_question: str, hypothesis: ResearchHypothesis) -> StudyType:
        """Recommend optimal study type based on research question"""

        try:
            # Analyze research question for study type indicators
            question_lower = research_question.lower()

            # Decision tree for study type recommendation
            if any(term in question_lower for term in ['systematic review', 'meta-analysis', 'review']):
                return StudyType.SYSTEMATIC_REVIEW

            elif any(term in question_lower for term in ['randomized', 'trial', 'rct', 'controlled']):
                return StudyType.RANDOMIZED_TRIAL

            elif any(term in question_lower for term in ['cohort', 'longitudinal', 'follow']):
                return StudyType.COHORT_STUDY

            elif any(term in question_lower for term in ['case-control', 'case control']):
                return StudyType.CASE_CONTROL

            elif any(term in question_lower for term in ['cross-sectional', 'prevalence', 'survey']):
                return StudyType.CROSS_SECTIONAL

            elif any(term in question_lower for term in ['experiment', 'laboratory', 'in vitro']):
                return StudyType.EXPERIMENTAL

            else:
                # Default to cohort study for neurosurgical research
                return StudyType.COHORT_STUDY

        except Exception as e:
            logger.warning(f"Failed to recommend study type: {e}")
            return StudyType.COHORT_STUDY

    async def _generate_grant_proposal(
        self,
        research_question: str,
        hypothesis: ResearchHypothesis,
        study_design: StudyDesign
    ) -> GrantProposal:
        """Generate grant proposal framework"""

        try:
            # Create grant proposal prompt
            prompt = f"""
            Generate grant proposal framework for this neurosurgical research:

            Research Question: {research_question}
            Primary Hypothesis: {hypothesis.primary_hypothesis}
            Study Type: {study_design.study_type.value}
            Sample Size: {study_design.sample_size}

            Generate proposal framework in JSON format:
            {{
                "title": "Concise, compelling grant title",
                "specific_aims": ["Aim 1", "Aim 2", "Aim 3"],
                "background_significance": "Background and significance section",
                "innovation": "Innovation and impact statement",
                "approach": "Research approach and methodology",
                "budget_summary": {{
                    "personnel": 150000,
                    "equipment": 50000,
                    "supplies": 25000,
                    "travel": 5000,
                    "indirect": 50000,
                    "total": 280000
                }},
                "timeline": {{
                    "year_1": "Activities for year 1",
                    "year_2": "Activities for year 2",
                    "year_3": "Activities for year 3"
                }},
                "success_probability": 0.65
            }}

            Focus on:
            1. Clinical significance for neurosurgery
            2. Innovation and impact
            3. Feasible budget and timeline
            4. Strong scientific rationale
            """

            result = await multi_ai_manager.generate_content(
                prompt=prompt,
                provider="claude",  # Use Claude for grant writing
                context_type="medical",
                max_tokens=1200,
                temperature=0.3
            )

            if result.get("success"):
                try:
                    proposal_data = json.loads(result["content"])

                    # Match with funding sources
                    funding_sources = await self._match_funding_sources(research_question, proposal_data)

                    return GrantProposal(
                        title=proposal_data.get("title", ""),
                        specific_aims=proposal_data.get("specific_aims", []),
                        background_significance=proposal_data.get("background_significance", ""),
                        innovation=proposal_data.get("innovation", ""),
                        approach=proposal_data.get("approach", ""),
                        budget_summary=proposal_data.get("budget_summary", {}),
                        timeline=proposal_data.get("timeline", {}),
                        potential_funding_sources=funding_sources,
                        success_probability=proposal_data.get("success_probability", 0.5)
                    )

                except json.JSONDecodeError:
                    pass

            # Fallback proposal
            funding_sources = await self._match_funding_sources(research_question, {})

            return GrantProposal(
                title=f"Investigation of {research_question}",
                specific_aims=[
                    "Establish feasibility and safety",
                    "Evaluate clinical efficacy",
                    "Assess long-term outcomes"
                ],
                background_significance="Significant clinical problem requiring investigation",
                innovation="Novel approach to addressing clinical challenge",
                approach="Rigorous methodology with appropriate controls",
                budget_summary={
                    "personnel": 150000,
                    "equipment": 50000,
                    "supplies": 25000,
                    "travel": 5000,
                    "indirect": 50000,
                    "total": 280000
                },
                timeline={
                    "year_1": "Study setup and recruitment",
                    "year_2": "Data collection and analysis",
                    "year_3": "Completion and dissemination"
                },
                potential_funding_sources=funding_sources,
                success_probability=0.6
            )

        except Exception as e:
            logger.error(f"Failed to generate grant proposal: {e}")
            raise

    async def _match_funding_sources(self, research_question: str, proposal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match research with appropriate funding sources"""

        try:
            funding_matches = []

            # Analyze research for funding fit
            question_lower = research_question.lower()
            budget = proposal_data.get("budget_summary", {}).get("total", 280000)

            # NIH matching
            if any(term in question_lower for term in ['brain', 'neural', 'neurological', 'neurosurg']):
                funding_matches.append({
                    "agency": "NIH/NINDS",
                    "mechanism": "R01" if budget > 200000 else "R21",
                    "typical_amount": 250000 if budget > 200000 else 100000,
                    "success_rate": 0.18 if budget > 200000 else 0.15,
                    "fit_score": 0.9,
                    "deadline": "Multiple per year",
                    "notes": "Strong fit for neurosurgical research"
                })

            # Private foundation matching
            if any(term in question_lower for term in ['brain', 'movement', 'parkinson', 'alzheimer']):
                funding_matches.append({
                    "agency": "Private Foundations",
                    "mechanism": "Foundation Grant",
                    "typical_amount": 150000,
                    "success_rate": 0.25,
                    "fit_score": 0.8,
                    "deadline": "Varies",
                    "notes": "Consider disease-specific foundations"
                })

            # NSF matching for engineering/computational approaches
            if any(term in question_lower for term in ['computational', 'engineering', 'device', 'technology']):
                funding_matches.append({
                    "agency": "NSF",
                    "mechanism": "Standard Grant",
                    "typical_amount": 200000,
                    "success_rate": 0.22,
                    "fit_score": 0.7,
                    "deadline": "Annual",
                    "notes": "Good for engineering approaches"
                })

            return funding_matches

        except Exception as e:
            logger.warning(f"Failed to match funding sources: {e}")
            return []

    async def _generate_methodology_recommendations(
        self,
        research_question: str,
        study_design: StudyDesign
    ) -> List[str]:
        """Generate specific methodology recommendations"""

        recommendations = [
            f"Consider {study_design.study_type.value} design for optimal evidence generation",
            f"Target sample size of {study_design.sample_size} based on power analysis",
            "Implement robust randomization and blinding procedures where possible",
            "Use validated outcome measures specific to neurosurgery",
            "Plan for interim analyses and data safety monitoring",
            "Consider multi-center collaboration to enhance generalizability",
            "Implement electronic data capture for data quality",
            "Plan for missing data and dropout scenarios",
            "Include patient-reported outcomes and quality of life measures",
            "Ensure adequate follow-up duration for meaningful outcomes"
        ]

        # Add study-type specific recommendations
        if study_design.study_type == StudyType.RANDOMIZED_TRIAL:
            recommendations.extend([
                "Use stratified randomization for key prognostic factors",
                "Consider adaptive trial design for efficiency",
                "Plan for intention-to-treat and per-protocol analyses"
            ])

        elif study_design.study_type == StudyType.COHORT_STUDY:
            recommendations.extend([
                "Ensure adequate follow-up time for outcome development",
                "Control for selection bias and loss to follow-up",
                "Consider propensity score matching for confounders"
            ])

        return recommendations

    async def _assess_research_risks(self, study_design: StudyDesign) -> Dict[str, Any]:
        """Assess potential risks and challenges in the research"""

        return {
            "recruitment_risk": {
                "level": "medium" if study_design.sample_size > 100 else "low",
                "mitigation": "Multi-center collaboration and broad inclusion criteria"
            },
            "timeline_risk": {
                "level": "medium",
                "mitigation": "Build buffer time into milestones"
            },
            "technical_risk": {
                "level": "low" if study_design.study_type in [StudyType.COHORT_STUDY, StudyType.CASE_CONTROL] else "medium",
                "mitigation": "Pilot studies and protocol refinement"
            },
            "regulatory_risk": {
                "level": "medium",
                "mitigation": "Early IRB consultation and regulatory guidance"
            },
            "funding_risk": {
                "level": "high",
                "mitigation": "Multiple funding source applications and phased approach"
            }
        }

    async def _calculate_workflow_quality(
        self,
        hypothesis: ResearchHypothesis,
        study_design: StudyDesign,
        grant_proposal: GrantProposal
    ) -> float:
        """Calculate overall quality score for the research workflow"""

        try:
            # Hypothesis quality (30%)
            hypothesis_score = (hypothesis.strength_of_evidence + hypothesis.novelty_score) / 2

            # Study design quality (40%)
            design_score = study_design.feasibility_score

            # Grant proposal quality (30%)
            proposal_score = grant_proposal.success_probability

            # Combined quality score
            quality_score = (
                hypothesis_score * 0.3 +
                design_score * 0.4 +
                proposal_score * 0.3
            )

            return min(max(quality_score, 0.0), 1.0)

        except Exception as e:
            logger.error(f"Failed to calculate workflow quality: {e}")
            return 0.6

    async def optimize_research_timeline(
        self,
        study_design: StudyDesign,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize research timeline based on constraints and best practices"""

        try:
            # Base timeline from study design
            base_timeline = study_design.timeline

            # Apply optimization based on study type and constraints
            optimization_prompt = f"""
            Optimize research timeline for {study_design.study_type.value} study:

            Current Timeline: {base_timeline}
            Sample Size: {study_design.sample_size}
            Constraints: {constraints or 'None specified'}

            Provide optimized timeline in JSON format:
            {{
                "optimized_timeline": {{
                    "preparation": "3 months",
                    "recruitment": "6 months",
                    "intervention": "12 months",
                    "follow_up": "6 months",
                    "analysis": "3 months",
                    "dissemination": "3 months"
                }},
                "critical_path": ["Task 1", "Task 2", "Task 3"],
                "risk_factors": ["Risk 1", "Risk 2"],
                "optimization_notes": "Key optimization strategies"
            }}

            Consider:
            1. Parallel activities where possible
            2. Critical path dependencies
            3. Resource constraints
            4. Seasonal effects on recruitment
            """

            result = await multi_ai_manager.generate_content(
                prompt=optimization_prompt,
                provider="gemini",
                context_type="medical",
                max_tokens=600,
                temperature=0.2
            )

            if result.get("success"):
                try:
                    return json.loads(result["content"])
                except json.JSONDecodeError:
                    pass

            # Fallback optimization
            return {
                "optimized_timeline": base_timeline,
                "critical_path": ["IRB approval", "Recruitment", "Data analysis"],
                "risk_factors": ["Slow recruitment", "Technical delays"],
                "optimization_notes": "Standard timeline optimization applied"
            }

        except Exception as e:
            logger.error(f"Failed to optimize timeline: {e}")
            return {"error": str(e)}

# Global instance
research_workflow_engine = ResearchWorkflowEngine()