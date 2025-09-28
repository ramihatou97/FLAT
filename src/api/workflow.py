"""
Research Workflow API Endpoints
AI-powered research methodology, hypothesis generation, and workflow automation
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
from pydantic import BaseModel
from enum import Enum

from ..services.research_workflow_engine import research_workflow_engine, StudyType, ResearchPhase, FundingType

logger = logging.getLogger(__name__)
router = APIRouter()

class WorkflowRequest(BaseModel):
    research_question: str
    specialty: str = "neurosurgery"
    study_preferences: Optional[Dict[str, Any]] = None
    budget_constraints: Optional[Dict[str, float]] = None
    timeline_constraints: Optional[Dict[str, str]] = None

class HypothesisRequest(BaseModel):
    research_question: str
    literature_context: Optional[Dict[str, Any]] = None
    focus_areas: Optional[List[str]] = None

class StudyDesignRequest(BaseModel):
    research_question: str
    hypothesis: str
    preferred_study_type: Optional[StudyType] = None
    sample_size_preference: Optional[int] = None
    budget_limit: Optional[float] = None

class GrantProposalRequest(BaseModel):
    research_question: str
    study_design_summary: str
    requested_amount: Optional[float] = None
    funding_type: Optional[FundingType] = None
    institution_type: str = "academic"

class TimelineOptimizationRequest(BaseModel):
    current_timeline: Dict[str, str]
    constraints: Optional[Dict[str, Any]] = None
    priority_factors: Optional[List[str]] = None

@router.post("/generate-workflow")
async def generate_research_workflow(request: WorkflowRequest):
    """
    Generate comprehensive research workflow from research question

    Includes:
    - Literature landscape analysis
    - Hypothesis generation
    - Study design methodology
    - Grant proposal framework
    - Timeline and risk assessment
    """
    try:
        logger.info(f"🔬 Generating research workflow for: '{request.research_question}'")

        # Generate comprehensive workflow
        workflow = await research_workflow_engine.generate_research_workflow(
            research_question=request.research_question,
            specialty=request.specialty,
            study_preferences=request.study_preferences
        )

        # Format response
        return {
            "success": True,
            "workflow": {
                "research_question": workflow.research_question,
                "quality_score": round(workflow.quality_score, 3),
                "hypothesis": {
                    "primary": workflow.hypothesis.primary_hypothesis,
                    "secondary": workflow.hypothesis.secondary_hypotheses,
                    "null": workflow.hypothesis.null_hypothesis,
                    "alternative": workflow.hypothesis.alternative_hypothesis,
                    "predictions": workflow.hypothesis.testable_predictions,
                    "confounders": workflow.hypothesis.potential_confounders,
                    "strength": round(workflow.hypothesis.strength_of_evidence, 3),
                    "novelty": round(workflow.hypothesis.novelty_score, 3)
                },
                "study_design": {
                    "type": workflow.study_design.study_type.value,
                    "sample_size": workflow.study_design.sample_size,
                    "power_analysis": workflow.study_design.power_analysis,
                    "inclusion_criteria": workflow.study_design.inclusion_criteria,
                    "exclusion_criteria": workflow.study_design.exclusion_criteria,
                    "primary_endpoints": workflow.study_design.primary_endpoints,
                    "secondary_endpoints": workflow.study_design.secondary_endpoints,
                    "statistical_methods": workflow.study_design.statistical_methods,
                    "timeline": workflow.study_design.timeline,
                    "feasibility": round(workflow.study_design.feasibility_score, 3)
                },
                "grant_proposal": {
                    "title": workflow.grant_proposal.title,
                    "specific_aims": workflow.grant_proposal.specific_aims,
                    "background": workflow.grant_proposal.background_significance,
                    "innovation": workflow.grant_proposal.innovation,
                    "approach": workflow.grant_proposal.approach,
                    "budget": workflow.grant_proposal.budget_summary,
                    "timeline": workflow.grant_proposal.timeline,
                    "funding_sources": workflow.grant_proposal.potential_funding_sources,
                    "success_probability": round(workflow.grant_proposal.success_probability, 3)
                },
                "recommendations": workflow.methodology_recommendations,
                "risk_assessment": workflow.risk_assessment
            },
            "metadata": {
                "generation_timestamp": workflow.research_question,  # Will be fixed with proper timestamp
                "ai_providers_used": ["claude", "gemini", "literature_analysis"],
                "methodology": "AI-powered research workflow automation",
                "specialty_focus": request.specialty
            }
        }

    except Exception as e:
        logger.error(f"Research workflow generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow generation failed: {str(e)}")

@router.post("/generate-hypothesis")
async def generate_research_hypothesis(request: HypothesisRequest):
    """
    Generate AI-powered research hypotheses

    Features:
    - Literature-informed hypothesis generation
    - Testable predictions
    - Confounder identification
    - Novelty and strength assessment
    """
    try:
        logger.info(f"💡 Generating hypothesis for: '{request.research_question}'")

        # If no literature context provided, perform rapid analysis
        if not request.literature_context:
            from ..services.literature_analysis_engine import literature_analysis_engine

            synthesis = await literature_analysis_engine.analyze_literature_corpus(
                topic=request.research_question,
                max_papers=10,  # Rapid analysis
                years_back=3,
                include_meta_analysis=False
            )

            literature_context = {
                "existing_evidence": synthesis.evidence_summary,
                "research_gaps": synthesis.future_research,
                "evidence_quality": synthesis.quality_score
            }
        else:
            literature_context = request.literature_context

        # Generate hypothesis using workflow engine
        hypothesis = await research_workflow_engine._generate_research_hypothesis(
            request.research_question, literature_context
        )

        return {
            "success": True,
            "hypothesis": {
                "primary_hypothesis": hypothesis.primary_hypothesis,
                "secondary_hypotheses": hypothesis.secondary_hypotheses,
                "null_hypothesis": hypothesis.null_hypothesis,
                "alternative_hypothesis": hypothesis.alternative_hypothesis,
                "testable_predictions": hypothesis.testable_predictions,
                "potential_confounders": hypothesis.potential_confounders,
                "strength_of_evidence": round(hypothesis.strength_of_evidence, 3),
                "novelty_score": round(hypothesis.novelty_score, 3)
            },
            "literature_context": literature_context,
            "recommendations": {
                "testing_strategy": "Design experiments to test each prediction systematically",
                "confounder_control": "Implement randomization and stratification strategies",
                "validation_approach": "Consider pilot studies before full implementation"
            }
        }

    except Exception as e:
        logger.error(f"Hypothesis generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hypothesis generation failed: {str(e)}")

@router.post("/design-study")
async def design_study_methodology(request: StudyDesignRequest):
    """
    Design optimal study methodology

    Features:
    - Study type recommendation
    - Sample size calculation
    - Statistical methodology
    - Timeline planning
    - Feasibility assessment
    """
    try:
        logger.info(f"📊 Designing study for: '{request.research_question}'")

        # Create mock hypothesis for design process
        from ..services.research_workflow_engine import ResearchHypothesis

        hypothesis = ResearchHypothesis(
            primary_hypothesis=request.hypothesis,
            secondary_hypotheses=[],
            null_hypothesis="No significant difference",
            alternative_hypothesis="Significant difference exists",
            testable_predictions=[],
            potential_confounders=[],
            strength_of_evidence=0.7,
            novelty_score=0.7
        )

        # Design study methodology
        study_design = await research_workflow_engine._design_study_methodology(
            request.research_question,
            hypothesis,
            {
                "preferred_type": request.preferred_study_type.value if request.preferred_study_type else None,
                "sample_size": request.sample_size_preference,
                "budget_limit": request.budget_limit
            }
        )

        # Generate methodology recommendations
        recommendations = await research_workflow_engine._generate_methodology_recommendations(
            request.research_question, study_design
        )

        return {
            "success": True,
            "study_design": {
                "study_type": study_design.study_type.value,
                "sample_size": study_design.sample_size,
                "power_analysis": study_design.power_analysis,
                "inclusion_criteria": study_design.inclusion_criteria,
                "exclusion_criteria": study_design.exclusion_criteria,
                "primary_endpoints": study_design.primary_endpoints,
                "secondary_endpoints": study_design.secondary_endpoints,
                "statistical_methods": study_design.statistical_methods,
                "timeline": study_design.timeline,
                "feasibility_score": round(study_design.feasibility_score, 3)
            },
            "methodology_recommendations": recommendations,
            "implementation_notes": {
                "regulatory_considerations": "IRB approval required before study initiation",
                "data_management": "Implement electronic data capture system",
                "quality_assurance": "Regular monitoring and data audits recommended",
                "ethics": "Ensure informed consent and patient safety protocols"
            }
        }

    except Exception as e:
        logger.error(f"Study design failed: {e}")
        raise HTTPException(status_code=500, detail=f"Study design failed: {str(e)}")

@router.post("/grant-proposal")
async def generate_grant_proposal(request: GrantProposalRequest):
    """
    Generate grant proposal framework

    Features:
    - Funding source matching
    - Budget estimation
    - Timeline development
    - Success probability assessment
    """
    try:
        logger.info(f"💰 Generating grant proposal for: '{request.research_question}'")

        # Create mock objects for proposal generation
        from ..services.research_workflow_engine import ResearchHypothesis, StudyDesign, StudyType

        hypothesis = ResearchHypothesis(
            primary_hypothesis="Primary research hypothesis",
            secondary_hypotheses=[],
            null_hypothesis="No effect",
            alternative_hypothesis="Significant effect",
            testable_predictions=[],
            potential_confounders=[],
            strength_of_evidence=0.7,
            novelty_score=0.7
        )

        study_design = StudyDesign(
            study_type=StudyType.COHORT_STUDY,
            sample_size=100,
            power_analysis={},
            inclusion_criteria=[],
            exclusion_criteria=[],
            primary_endpoints=[],
            secondary_endpoints=[],
            statistical_methods=[],
            timeline={},
            feasibility_score=0.7
        )

        # Generate grant proposal
        grant_proposal = await research_workflow_engine._generate_grant_proposal(
            request.research_question, hypothesis, study_design
        )

        return {
            "success": True,
            "grant_proposal": {
                "title": grant_proposal.title,
                "specific_aims": grant_proposal.specific_aims,
                "background_significance": grant_proposal.background_significance,
                "innovation": grant_proposal.innovation,
                "approach": grant_proposal.approach,
                "budget_summary": grant_proposal.budget_summary,
                "timeline": grant_proposal.timeline,
                "potential_funding_sources": grant_proposal.potential_funding_sources,
                "success_probability": round(grant_proposal.success_probability, 3)
            },
            "funding_strategy": {
                "recommended_sources": grant_proposal.potential_funding_sources[:3],
                "application_timeline": "Plan 6-12 months for proposal development",
                "success_factors": [
                    "Strong preliminary data",
                    "Clear clinical significance",
                    "Feasible methodology",
                    "Experienced team",
                    "Institutional support"
                ]
            }
        }

    except Exception as e:
        logger.error(f"Grant proposal generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Grant proposal generation failed: {str(e)}")

@router.post("/optimize-timeline")
async def optimize_research_timeline(request: TimelineOptimizationRequest):
    """
    Optimize research timeline based on constraints

    Features:
    - Critical path analysis
    - Resource optimization
    - Risk factor identification
    - Parallel activity identification
    """
    try:
        logger.info("📅 Optimizing research timeline")

        # Create mock study design for optimization
        from ..services.research_workflow_engine import StudyDesign, StudyType

        study_design = StudyDesign(
            study_type=StudyType.COHORT_STUDY,
            sample_size=100,
            power_analysis={},
            inclusion_criteria=[],
            exclusion_criteria=[],
            primary_endpoints=[],
            secondary_endpoints=[],
            statistical_methods=[],
            timeline=request.current_timeline,
            feasibility_score=0.7
        )

        # Optimize timeline
        optimization_result = await research_workflow_engine.optimize_research_timeline(
            study_design, request.constraints
        )

        return {
            "success": True,
            "timeline_optimization": optimization_result,
            "recommendations": {
                "parallel_activities": "Identify activities that can run concurrently",
                "resource_allocation": "Optimize resource usage across timeline",
                "risk_mitigation": "Build buffer time for high-risk activities",
                "milestone_tracking": "Establish clear checkpoints and deliverables"
            }
        }

    except Exception as e:
        logger.error(f"Timeline optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Timeline optimization failed: {str(e)}")

@router.get("/study-types")
async def get_study_types():
    """Get available study types and their characteristics"""

    return {
        "success": True,
        "study_types": [
            {
                "type": "randomized_trial",
                "label": "Randomized Controlled Trial",
                "description": "Gold standard for intervention studies",
                "evidence_level": "High",
                "typical_duration": "2-5 years",
                "complexity": "High",
                "cost": "High",
                "best_for": ["Treatment efficacy", "Intervention comparison"]
            },
            {
                "type": "cohort_study",
                "label": "Cohort Study",
                "description": "Follow groups over time to assess outcomes",
                "evidence_level": "Medium-High",
                "typical_duration": "1-3 years",
                "complexity": "Medium",
                "cost": "Medium",
                "best_for": ["Risk factors", "Natural history", "Prognosis"]
            },
            {
                "type": "case_control",
                "label": "Case-Control Study",
                "description": "Compare cases with disease to controls without",
                "evidence_level": "Medium",
                "typical_duration": "6 months - 2 years",
                "complexity": "Medium",
                "cost": "Medium",
                "best_for": ["Rare diseases", "Risk factor identification"]
            },
            {
                "type": "cross_sectional",
                "label": "Cross-Sectional Study",
                "description": "Snapshot assessment at single time point",
                "evidence_level": "Medium",
                "typical_duration": "3-12 months",
                "complexity": "Low",
                "cost": "Low",
                "best_for": ["Prevalence", "Associations"]
            },
            {
                "type": "systematic_review",
                "label": "Systematic Review",
                "description": "Comprehensive review of existing literature",
                "evidence_level": "Very High",
                "typical_duration": "6-18 months",
                "complexity": "Medium",
                "cost": "Low",
                "best_for": ["Evidence synthesis", "Clinical guidelines"]
            }
        ]
    }

@router.get("/funding-sources")
async def get_funding_sources():
    """Get available funding sources and their characteristics"""

    return {
        "success": True,
        "funding_sources": [
            {
                "agency": "NIH/NINDS",
                "type": "Federal",
                "mechanisms": ["R01", "R21", "K08", "K23"],
                "typical_amounts": {
                    "R01": "$250,000/year",
                    "R21": "$100,000/year",
                    "K08": "$150,000/year"
                },
                "success_rates": {
                    "R01": "18%",
                    "R21": "15%",
                    "K08": "25%"
                },
                "focus_areas": ["Neurosurgery", "Brain disorders", "Spinal cord injury"],
                "application_cycles": "3 times per year",
                "notes": "Strong preliminary data required"
            },
            {
                "agency": "NSF",
                "type": "Federal",
                "mechanisms": ["Standard Grant", "CAREER"],
                "typical_amounts": {
                    "Standard": "$200,000",
                    "CAREER": "$500,000"
                },
                "success_rates": {
                    "Standard": "22%",
                    "CAREER": "15%"
                },
                "focus_areas": ["Engineering", "Computational neuroscience", "Biomaterials"],
                "application_cycles": "Annual",
                "notes": "Focus on innovation and broader impacts"
            },
            {
                "agency": "Private Foundations",
                "type": "Private",
                "mechanisms": ["Research Grant", "Fellowship", "Equipment"],
                "typical_amounts": {
                    "Small": "$50,000",
                    "Medium": "$150,000",
                    "Large": "$300,000"
                },
                "success_rates": {
                    "Average": "25%"
                },
                "focus_areas": ["Disease-specific research", "Young investigators"],
                "application_cycles": "Varies",
                "notes": "Often disease-specific focus"
            }
        ]
    }

@router.get("/workflow-templates")
async def get_workflow_templates():
    """Get pre-configured workflow templates for common research types"""

    return {
        "success": True,
        "templates": [
            {
                "name": "Clinical Trial Template",
                "description": "Template for interventional clinical studies",
                "study_type": "randomized_trial",
                "typical_timeline": {
                    "planning": "6 months",
                    "recruitment": "12 months",
                    "intervention": "18 months",
                    "follow_up": "12 months",
                    "analysis": "6 months"
                },
                "key_components": [
                    "FDA/IRB approvals",
                    "Randomization strategy",
                    "Primary endpoint definition",
                    "Safety monitoring plan"
                ]
            },
            {
                "name": "Observational Study Template",
                "description": "Template for cohort and case-control studies",
                "study_type": "cohort_study",
                "typical_timeline": {
                    "planning": "3 months",
                    "recruitment": "6 months",
                    "follow_up": "24 months",
                    "analysis": "4 months"
                },
                "key_components": [
                    "Exposure definition",
                    "Outcome measurement",
                    "Confounding control",
                    "Loss to follow-up plan"
                ]
            },
            {
                "name": "Systematic Review Template",
                "description": "Template for evidence synthesis studies",
                "study_type": "systematic_review",
                "typical_timeline": {
                    "protocol": "2 months",
                    "search": "2 months",
                    "screening": "3 months",
                    "extraction": "4 months",
                    "analysis": "3 months",
                    "writing": "3 months"
                },
                "key_components": [
                    "PRISMA compliance",
                    "Search strategy",
                    "Quality assessment",
                    "Meta-analysis plan"
                ]
            }
        ]
    }

@router.get("/capabilities")
async def get_workflow_capabilities():
    """Get comprehensive overview of workflow automation capabilities"""

    return {
        "success": True,
        "capabilities": {
            "research_workflow": {
                "description": "End-to-end research planning automation",
                "features": [
                    "Literature landscape analysis",
                    "AI-powered hypothesis generation",
                    "Study design optimization",
                    "Statistical methodology selection",
                    "Timeline and budget planning",
                    "Risk assessment and mitigation"
                ]
            },
            "grant_support": {
                "description": "Automated grant proposal assistance",
                "features": [
                    "Funding source matching",
                    "Budget estimation and breakdown",
                    "Success probability assessment",
                    "Proposal framework generation",
                    "Timeline optimization"
                ]
            },
            "methodology_design": {
                "description": "Evidence-based methodology recommendations",
                "features": [
                    "Study type selection",
                    "Sample size calculation",
                    "Endpoint definition",
                    "Statistical analysis planning",
                    "Quality assurance protocols"
                ]
            },
            "ai_integration": {
                "providers": ["Claude", "Gemini", "Literature Analysis Engine"],
                "specializations": {
                    "claude": "Academic writing and proposal generation",
                    "gemini": "Data analysis and methodology design",
                    "literature_engine": "Evidence synthesis and gap analysis"
                }
            }
        }
    }