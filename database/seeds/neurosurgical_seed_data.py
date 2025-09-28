"""
Neurosurgical Encyclopedia Seed Data
Initial data population for anatomical structures, surgical procedures, and sample chapters
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from database.neurosurgical_models import (
    AnatomicalStructure, SurgicalProcedure, EvidenceSource, 
    AliveChapter, ContentEmbedding
)

class NeurosurgicalSeeder:
    """Seed neurosurgical database with initial data"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def seed_all(self):
        """Seed all neurosurgical data"""
        print("🧠 Starting neurosurgical database seeding...")
        
        # Seed in dependency order
        anatomical_structures = await self.seed_anatomical_structures()
        surgical_procedures = await self.seed_surgical_procedures(anatomical_structures)
        evidence_sources = await self.seed_evidence_sources()
        alive_chapters = await self.seed_alive_chapters(anatomical_structures, evidence_sources)
        
        await self.session.commit()
        print("✅ Neurosurgical database seeding completed!")
        
        return {
            "anatomical_structures": len(anatomical_structures),
            "surgical_procedures": len(surgical_procedures),
            "evidence_sources": len(evidence_sources),
            "alive_chapters": len(alive_chapters)
        }
    
    async def seed_anatomical_structures(self) -> List[AnatomicalStructure]:
        """Seed hierarchical anatomical structures"""
        print("📍 Seeding anatomical structures...")
        
        structures = []
        
        # Level 0: Central Nervous System
        cns = AnatomicalStructure(
            name="Central Nervous System",
            latin_name="Systema nervosum centrale",
            level=0,
            path="CNS",
            clinical_significance="The central nervous system comprises the brain and spinal cord, controlling all bodily functions.",
            tissue_type="neural",
            functional_role="Integration and control of nervous system functions",
            coordinates_3d={"center": [0, 0, 0], "bounds": [[-100, -150, -50], [100, 150, 50]]},
            eloquent_area=True
        )
        structures.append(cns)
        self.session.add(cns)
        await self.session.flush()  # Get ID for relationships
        
        # Level 1: Brain
        brain = AnatomicalStructure(
            name="Brain",
            latin_name="Encephalon",
            parent_id=cns.id,
            level=1,
            path="CNS > Brain",
            clinical_significance="The brain is the primary control center for the nervous system.",
            surgical_approaches=["craniotomy", "stereotactic", "endoscopic"],
            common_pathologies=["tumor", "hemorrhage", "ischemia", "trauma"],
            tissue_type="neural",
            functional_role="Cognitive functions, motor control, sensory processing",
            coordinates_3d={"center": [0, 0, 20], "bounds": [[-80, -60, -20], [80, 60, 60]]},
            eloquent_area=True,
            vascular_supply={
                "anterior_circulation": ["ACA", "MCA"],
                "posterior_circulation": ["PCA", "basilar", "vertebral"]
            }
        )
        structures.append(brain)
        self.session.add(brain)
        await self.session.flush()
        
        # Level 2: Brain regions
        brain_regions = [
            {
                "name": "Cerebrum",
                "latin_name": "Cerebrum",
                "clinical_significance": "Largest part of the brain responsible for higher cognitive functions.",
                "coordinates_3d": {"center": [0, 0, 30], "bounds": [[-70, -50, 0], [70, 50, 60]]},
                "functional_role": "Consciousness, thought, emotion, reasoning, language, memory"
            },
            {
                "name": "Cerebellum",
                "latin_name": "Cerebellum",
                "clinical_significance": "Coordinates movement, balance, and posture.",
                "coordinates_3d": {"center": [0, -40, 10], "bounds": [[-40, -60, -10], [40, -20, 30]]},
                "functional_role": "Motor coordination, balance, motor learning"
            },
            {
                "name": "Brainstem",
                "latin_name": "Truncus encephali",
                "clinical_significance": "Controls vital functions including breathing and heart rate.",
                "coordinates_3d": {"center": [0, -20, 0], "bounds": [[-15, -35, -20], [15, -5, 20]]},
                "functional_role": "Vital functions, consciousness, cranial nerve nuclei",
                "eloquent_area": True
            }
        ]
        
        for region_data in brain_regions:
            region = AnatomicalStructure(
                parent_id=brain.id,
                level=2,
                path=f"CNS > Brain > {region_data['name']}",
                tissue_type="neural",
                surgical_approaches=["craniotomy", "stereotactic"],
                common_pathologies=["tumor", "vascular malformation", "trauma"],
                **region_data
            )
            structures.append(region)
            self.session.add(region)
        
        await self.session.flush()
        
        # Level 1: Spinal Cord
        spinal_cord = AnatomicalStructure(
            name="Spinal Cord",
            latin_name="Medulla spinalis",
            parent_id=cns.id,
            level=1,
            path="CNS > Spinal Cord",
            clinical_significance="Transmits neural signals between brain and peripheral nervous system.",
            surgical_approaches=["laminectomy", "laminoplasty", "anterior approach"],
            common_pathologies=["compression", "tumor", "trauma", "syrinx"],
            tissue_type="neural",
            functional_role="Signal transmission, reflex processing",
            coordinates_3d={"center": [0, 0, -50], "bounds": [[-10, -10, -150], [10, 10, 50]]},
            eloquent_area=True
        )
        structures.append(spinal_cord)
        self.session.add(spinal_cord)
        
        print(f"✅ Created {len(structures)} anatomical structures")
        return structures
    
    async def seed_surgical_procedures(self, anatomical_structures: List[AnatomicalStructure]) -> List[SurgicalProcedure]:
        """Seed neurosurgical procedures"""
        print("🔧 Seeding surgical procedures...")
        
        procedures = []
        
        # Find brain structure for relationships
        brain = next((s for s in anatomical_structures if s.name == "Brain"), None)
        spinal_cord = next((s for s in anatomical_structures if s.name == "Spinal Cord"), None)
        
        procedure_data = [
            {
                "name": "Craniotomy for Tumor Resection",
                "short_name": "Craniotomy",
                "cpt_code": "61510",
                "subspecialty": "tumor",
                "complexity_score": 8,
                "duration_minutes": 240,
                "anesthesia_type": "general",
                "indications": ["brain tumor", "mass lesion", "biopsy"],
                "contraindications": ["severe coagulopathy", "unstable medical condition"],
                "step_by_step_guide": [
                    {"step": 1, "description": "Patient positioning and preparation"},
                    {"step": 2, "description": "Scalp incision and bone flap creation"},
                    {"step": 3, "description": "Dural opening"},
                    {"step": 4, "description": "Tumor identification and resection"},
                    {"step": 5, "description": "Hemostasis and closure"}
                ],
                "equipment_required": ["craniotome", "microscope", "ultrasonic aspirator", "neuronavigation"],
                "positioning": "supine or lateral",
                "surgical_approach": "transcranial",
                "complications": {
                    "bleeding": {"frequency": "5%", "severity": "moderate"},
                    "infection": {"frequency": "2%", "severity": "moderate"},
                    "neurological deficit": {"frequency": "3%", "severity": "high"}
                },
                "success_rate": 0.92,
                "mortality_rate": 0.02,
                "evidence_level": "II",
                "learning_curve": "steep",
                "training_requirements": ["neurosurgery residency", "tumor fellowship"]
            },
            {
                "name": "Lumbar Laminectomy",
                "short_name": "Laminectomy",
                "cpt_code": "63047",
                "subspecialty": "spine",
                "complexity_score": 5,
                "duration_minutes": 120,
                "anesthesia_type": "general",
                "indications": ["spinal stenosis", "disc herniation", "spondylolisthesis"],
                "contraindications": ["active infection", "severe osteoporosis"],
                "step_by_step_guide": [
                    {"step": 1, "description": "Prone positioning"},
                    {"step": 2, "description": "Midline incision"},
                    {"step": 3, "description": "Muscle dissection"},
                    {"step": 4, "description": "Lamina removal"},
                    {"step": 5, "description": "Neural decompression"},
                    {"step": 6, "description": "Closure"}
                ],
                "equipment_required": ["drill", "kerrison rongeurs", "microscope"],
                "positioning": "prone",
                "surgical_approach": "posterior midline",
                "complications": {
                    "dural tear": {"frequency": "8%", "severity": "low"},
                    "infection": {"frequency": "3%", "severity": "moderate"},
                    "instability": {"frequency": "5%", "severity": "moderate"}
                },
                "success_rate": 0.88,
                "mortality_rate": 0.001,
                "evidence_level": "I",
                "learning_curve": "moderate",
                "training_requirements": ["neurosurgery residency"]
            },
            {
                "name": "Stereotactic Brain Biopsy",
                "short_name": "Stereotactic Biopsy",
                "cpt_code": "61750",
                "subspecialty": "tumor",
                "complexity_score": 6,
                "duration_minutes": 90,
                "anesthesia_type": "local with sedation",
                "indications": ["deep brain lesion", "multiple lesions", "eloquent area tumor"],
                "contraindications": ["coagulopathy", "vascular lesion"],
                "step_by_step_guide": [
                    {"step": 1, "description": "Frame placement"},
                    {"step": 2, "description": "Imaging and planning"},
                    {"step": 3, "description": "Trajectory calculation"},
                    {"step": 4, "description": "Burr hole creation"},
                    {"step": 5, "description": "Biopsy sampling"}
                ],
                "equipment_required": ["stereotactic frame", "navigation system", "biopsy needle"],
                "positioning": "supine",
                "surgical_approach": "stereotactic",
                "complications": {
                    "hemorrhage": {"frequency": "2%", "severity": "high"},
                    "infection": {"frequency": "1%", "severity": "moderate"}
                },
                "success_rate": 0.95,
                "mortality_rate": 0.005,
                "evidence_level": "II",
                "learning_curve": "moderate",
                "training_requirements": ["neurosurgery residency", "stereotactic training"]
            }
        ]
        
        for proc_data in procedure_data:
            procedure = SurgicalProcedure(**proc_data)
            procedures.append(procedure)
            self.session.add(procedure)
        
        print(f"✅ Created {len(procedures)} surgical procedures")
        return procedures
    
    async def seed_evidence_sources(self) -> List[EvidenceSource]:
        """Seed evidence sources"""
        print("📚 Seeding evidence sources...")
        
        sources = []
        
        source_data = [
            {
                "source_type": "pubmed",
                "external_id": "PMID:12345678",
                "title": "Outcomes of Craniotomy for Brain Tumor Resection: A Systematic Review",
                "authors": ["Smith JA", "Johnson MB", "Williams CD"],
                "journal": "Journal of Neurosurgery",
                "publication_date": datetime(2023, 6, 15),
                "volume": "138",
                "issue": "6",
                "pages": "1234-1245",
                "impact_factor": 4.5,
                "citation_count": 45,
                "credibility_score": 85.0,
                "evidence_level": "II",
                "study_design": "systematic review",
                "abstract": "This systematic review analyzes outcomes of craniotomy for brain tumor resection...",
                "keywords": ["craniotomy", "brain tumor", "outcomes", "neurosurgery"],
                "mesh_terms": ["Craniotomy", "Brain Neoplasms", "Neurosurgical Procedures"],
                "peer_reviewed": True,
                "open_access": True
            },
            {
                "source_type": "pubmed",
                "external_id": "PMID:87654321",
                "title": "Lumbar Laminectomy for Spinal Stenosis: Long-term Follow-up Study",
                "authors": ["Brown KL", "Davis RM", "Wilson PJ"],
                "journal": "Spine",
                "publication_date": datetime(2023, 8, 20),
                "volume": "48",
                "issue": "16",
                "pages": "1156-1163",
                "impact_factor": 3.2,
                "citation_count": 28,
                "credibility_score": 78.0,
                "evidence_level": "III",
                "study_design": "cohort study",
                "abstract": "Long-term outcomes following lumbar laminectomy for spinal stenosis...",
                "keywords": ["laminectomy", "spinal stenosis", "outcomes", "spine surgery"],
                "mesh_terms": ["Laminectomy", "Spinal Stenosis", "Treatment Outcome"],
                "peer_reviewed": True,
                "open_access": False
            },
            {
                "source_type": "textbook",
                "external_id": "ISBN:9780123456789",
                "title": "Principles of Neurosurgery",
                "authors": ["Greenberg MS"],
                "publisher": "Thieme Medical Publishers",
                "publication_date": datetime(2022, 1, 1),
                "credibility_score": 92.0,
                "evidence_level": "V",
                "abstract": "Comprehensive textbook covering fundamental principles of neurosurgical practice...",
                "keywords": ["neurosurgery", "principles", "textbook", "education"],
                "peer_reviewed": True
            }
        ]
        
        for source_data_item in source_data:
            source = EvidenceSource(**source_data_item)
            sources.append(source)
            self.session.add(source)
        
        print(f"✅ Created {len(sources)} evidence sources")
        return sources
    
    async def seed_alive_chapters(self, anatomical_structures: List[AnatomicalStructure], evidence_sources: List[EvidenceSource]) -> List[AliveChapter]:
        """Seed alive chapters"""
        print("📖 Seeding alive chapters...")
        
        chapters = []
        
        chapter_data = [
            {
                "title": "Brain Tumor Management in Neurosurgery",
                "slug": "brain-tumor-management",
                "subtitle": "Comprehensive approach to diagnosis, treatment, and outcomes",
                "subspecialty": "tumor",
                "content_sections": [
                    {
                        "id": "introduction",
                        "title": "Introduction",
                        "content": "Brain tumors represent a diverse group of neoplasms requiring specialized neurosurgical management...",
                        "order": 1
                    },
                    {
                        "id": "classification",
                        "title": "Classification and Grading",
                        "content": "The WHO classification system provides standardized grading for brain tumors...",
                        "order": 2
                    },
                    {
                        "id": "surgical_management",
                        "title": "Surgical Management",
                        "content": "Surgical resection remains the primary treatment for most brain tumors...",
                        "order": 3
                    }
                ],
                "summary": "Comprehensive guide to brain tumor management including classification, surgical approaches, and outcomes.",
                "learning_objectives": [
                    "Understand brain tumor classification systems",
                    "Master surgical approaches for tumor resection",
                    "Recognize complications and management strategies"
                ],
                "key_points": [
                    "Maximal safe resection improves outcomes",
                    "Intraoperative monitoring preserves function",
                    "Multidisciplinary approach is essential"
                ],
                "monitoring_keywords": ["brain tumor", "craniotomy", "glioma", "meningioma", "tumor resection"],
                "update_frequency": "weekly",
                "quality_score": 85.0,
                "completeness_score": 78.0,
                "accuracy_score": 92.0,
                "freshness_score": 88.0,
                "word_count": 2500,
                "reading_time_minutes": 12,
                "difficulty_level": "intermediate",
                "target_audience": ["residents", "attendings"]
            },
            {
                "title": "Spinal Stenosis: Diagnosis and Surgical Treatment",
                "slug": "spinal-stenosis-treatment",
                "subtitle": "Evidence-based approach to spinal decompression",
                "subspecialty": "spine",
                "content_sections": [
                    {
                        "id": "pathophysiology",
                        "title": "Pathophysiology",
                        "content": "Spinal stenosis results from narrowing of the spinal canal...",
                        "order": 1
                    },
                    {
                        "id": "diagnosis",
                        "title": "Diagnostic Evaluation",
                        "content": "Clinical presentation and imaging findings guide diagnosis...",
                        "order": 2
                    },
                    {
                        "id": "surgical_options",
                        "title": "Surgical Options",
                        "content": "Decompressive procedures include laminectomy and laminoplasty...",
                        "order": 3
                    }
                ],
                "summary": "Evidence-based approach to diagnosis and surgical treatment of spinal stenosis.",
                "learning_objectives": [
                    "Recognize clinical presentation of spinal stenosis",
                    "Understand imaging findings and interpretation",
                    "Master surgical decompression techniques"
                ],
                "monitoring_keywords": ["spinal stenosis", "laminectomy", "decompression", "spine surgery"],
                "update_frequency": "monthly",
                "quality_score": 82.0,
                "completeness_score": 85.0,
                "accuracy_score": 89.0,
                "freshness_score": 75.0,
                "word_count": 1800,
                "reading_time_minutes": 9,
                "difficulty_level": "intermediate",
                "target_audience": ["residents", "attendings", "fellows"]
            }
        ]
        
        for chapter_data_item in chapter_data:
            chapter = AliveChapter(**chapter_data_item)
            chapters.append(chapter)
            self.session.add(chapter)
        
        print(f"✅ Created {len(chapters)} alive chapters")
        return chapters

async def run_seeder(session: AsyncSession):
    """Run the neurosurgical database seeder"""
    seeder = NeurosurgicalSeeder(session)
    return await seeder.seed_all()

# Example usage
if __name__ == "__main__":
    # This would be called from the main application
    # async with get_contextual_db_session() as session:
    #     results = await run_seeder(session)
    #     print(f"Seeding completed: {results}")
    pass
