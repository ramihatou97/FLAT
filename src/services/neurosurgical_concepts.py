"""
Neurosurgical Concepts Database
Comprehensive medical terminology and concept mapping for neurosurgery
"""

from typing import Dict, List, Set, Tuple
from enum import Enum
import re

class ConceptCategory(Enum):
    ANATOMY = "anatomy"
    PATHOLOGY = "pathology"
    PROCEDURES = "procedures"
    IMAGING = "imaging"
    INSTRUMENTS = "instruments"
    MEDICATIONS = "medications"
    ASSESSMENTS = "assessments"
    SYMPTOMS = "symptoms"
    TECHNIQUES = "techniques"

class NeurosurgicalConcepts:
    """
    Comprehensive neurosurgical concept database with 500+ terms
    Designed specifically for advanced semantic search in neurosurgical literature
    """

    def __init__(self):
        self.concepts = self._initialize_concepts()
        self.synonyms = self._initialize_synonyms()
        self.concept_hierarchy = self._initialize_hierarchy()
        self.abbreviations = self._initialize_abbreviations()

    def _initialize_concepts(self) -> Dict[ConceptCategory, List[str]]:
        """Initialize comprehensive neurosurgical concepts"""

        return {
            ConceptCategory.ANATOMY: [
                # Brain Structures
                "cerebral cortex", "frontal lobe", "parietal lobe", "temporal lobe", "occipital lobe",
                "prefrontal cortex", "motor cortex", "sensory cortex", "visual cortex", "auditory cortex",
                "cerebellum", "brainstem", "medulla oblongata", "pons", "midbrain", "thalamus",
                "hypothalamus", "hippocampus", "amygdala", "corpus callosum", "basal ganglia",
                "caudate nucleus", "putamen", "globus pallidus", "substantia nigra",

                # Vascular Anatomy
                "anterior cerebral artery", "middle cerebral artery", "posterior cerebral artery",
                "basilar artery", "vertebral artery", "carotid artery", "anterior communicating artery",
                "posterior communicating artery", "circle of Willis", "cerebrospinal fluid",
                "ventricular system", "lateral ventricles", "third ventricle", "fourth ventricle",
                "aqueduct of Sylvius", "choroid plexus",

                # Spinal Anatomy
                "spinal cord", "cervical spine", "thoracic spine", "lumbar spine", "sacral spine",
                "vertebral body", "intervertebral disc", "spinal canal", "neural foramen",
                "dura mater", "arachnoid mater", "pia mater", "subarachnoid space",
                "epidural space", "subdural space", "conus medullaris", "cauda equina",

                # Cranial Nerves
                "olfactory nerve", "optic nerve", "oculomotor nerve", "trochlear nerve",
                "trigeminal nerve", "abducens nerve", "facial nerve", "vestibulocochlear nerve",
                "glossopharyngeal nerve", "vagus nerve", "accessory nerve", "hypoglossal nerve",

                # Skull and Meninges
                "frontal bone", "parietal bone", "temporal bone", "occipital bone", "sphenoid bone",
                "ethmoid bone", "cranial vault", "skull base", "anterior fossa", "middle fossa",
                "posterior fossa", "foramen magnum", "sella turcica", "clinoid processes"
            ],

            ConceptCategory.PATHOLOGY: [
                # Brain Tumors
                "glioblastoma", "astrocytoma", "oligodendroglioma", "ependymoma", "medulloepithelioma",
                "meningioma", "pituitary adenoma", "craniopharyngioma", "acoustic neuroma",
                "schwannoma", "neurofibroma", "hemangioblastoma", "chordoma", "germinoma",
                "primary CNS lymphoma", "metastatic brain tumor", "brain metastases",

                # Vascular Pathology
                "cerebral aneurysm", "arteriovenous malformation", "cavernous malformation",
                "dural arteriovenous fistula", "moyamoya disease", "cerebral vasospasm",
                "subarachnoid hemorrhage", "intracerebral hemorrhage", "subdural hematoma",
                "epidural hematoma", "chronic subdural hematoma", "cerebral infarction",
                "ischemic stroke", "hemorrhagic stroke", "transient ischemic attack",

                # Spinal Pathology
                "herniated disc", "spinal stenosis", "spondylolisthesis", "spondylosis",
                "spinal tumor", "spinal metastases", "syringomyelia", "spinal cord injury",
                "cervical myelopathy", "lumbar radiculopathy", "cauda equina syndrome",
                "tethered cord syndrome", "Chiari malformation", "spina bifida",

                # Functional Disorders
                "epilepsy", "temporal lobe epilepsy", "focal seizures", "generalized seizures",
                "status epilepticus", "trigeminal neuralgia", "hemifacial spasm",
                "essential tremor", "Parkinson's disease", "dystonia", "chronic pain",
                "neuropathic pain", "central pain syndrome",

                # Trauma
                "traumatic brain injury", "concussion", "diffuse axonal injury", "contusion",
                "penetrating head injury", "skull fracture", "cervical spine injury",
                "spinal cord contusion", "cord transection", "central cord syndrome",
                "anterior cord syndrome", "Brown-Sequard syndrome",

                # Hydrocephalus
                "normal pressure hydrocephalus", "communicating hydrocephalus",
                "non-communicating hydrocephalus", "congenital hydrocephalus",
                "acquired hydrocephalus", "pseudotumor cerebri", "intracranial hypertension"
            ],

            ConceptCategory.PROCEDURES: [
                # General Neurosurgical Procedures
                "craniotomy", "craniectomy", "burr hole", "stereotactic biopsy",
                "image-guided surgery", "neuronavigation", "awake craniotomy",
                "intraoperative monitoring", "cortical mapping", "brain mapping",

                # Tumor Surgery
                "gross total resection", "subtotal resection", "tumor debulking",
                "laser interstitial thermal therapy", "stereotactic radiosurgery",
                "gamma knife", "cyberknife", "linear accelerator",

                # Vascular Procedures
                "aneurysm clipping", "aneurysm coiling", "arteriovenous malformation resection",
                "carotid endarterectomy", "extracranial-intracranial bypass",
                "superficial temporal artery to middle cerebral artery bypass",
                "vertebral artery transposition", "cerebral revascularization",

                # Spinal Procedures
                "laminectomy", "laminoplasty", "discectomy", "microdiscectomy",
                "anterior cervical discectomy and fusion", "posterior spinal fusion",
                "pedicle screw fixation", "cervical corpectomy", "vertebroplasty",
                "kyphoplasty", "spinal decompression", "foraminotomy",

                # Functional Procedures
                "deep brain stimulation", "vagus nerve stimulation", "epilepsy surgery",
                "temporal lobectomy", "hemispherectomy", "corpus callosotomy",
                "selective amygdalohippocampectomy", "multiple subpial transections",
                "gamma knife radiosurgery", "microvascular decompression",

                # Minimally Invasive Procedures
                "endoscopic surgery", "keyhole surgery", "tubular retractor surgery",
                "endoscopic third ventriculostomy", "endoscopic tumor resection",
                "percutaneous procedures", "stereotactic procedures"
            ],

            ConceptCategory.IMAGING: [
                # CT Imaging
                "computed tomography", "CT angiography", "CT perfusion", "CT myelography",
                "non-contrast CT", "contrast-enhanced CT", "CT venography",

                # MRI Imaging
                "magnetic resonance imaging", "T1-weighted imaging", "T2-weighted imaging",
                "FLAIR imaging", "diffusion-weighted imaging", "perfusion-weighted imaging",
                "susceptibility-weighted imaging", "gradient echo imaging",
                "functional MRI", "diffusion tensor imaging", "tractography",
                "MR angiography", "MR venography", "MR spectroscopy",
                "dynamic contrast-enhanced MRI", "blood oxygen level-dependent imaging",

                # Nuclear Medicine
                "positron emission tomography", "single-photon emission computed tomography",
                "PET-CT", "brain SPECT", "cerebrospinal fluid flow study",

                # Angiography
                "digital subtraction angiography", "cerebral angiography", "spinal angiography",
                "catheter angiography", "rotational angiography", "3D angiography",

                # Specialized Imaging
                "intraoperative ultrasound", "intraoperative MRI", "fluorescence-guided surgery",
                "5-aminolevulinic acid", "indocyanine green angiography", "electrocorticography"
            ],

            ConceptCategory.INSTRUMENTS: [
                # Surgical Instruments
                "microscope", "operating microscope", "endoscope", "neuroendoscope",
                "ultrasonic aspirator", "CUSA", "bipolar cautery", "monopolar cautery",
                "micro-scissors", "micro-forceps", "micro-dissectors", "retractors",
                "self-retaining retractors", "brain spatulas", "suction devices",

                # Monitoring Equipment
                "intracranial pressure monitor", "external ventricular drain",
                "intraoperative neurophysiological monitoring", "somatosensory evoked potentials",
                "motor evoked potentials", "brainstem auditory evoked potentials",
                "electromyography", "electroencephalography", "cortical stimulator",

                # Navigation and Robotics
                "stereotactic frame", "frameless stereotaxy", "neuronavigation system",
                "robotic surgery", "surgical robot", "image guidance system",
                "intraoperative imaging", "O-arm", "intraoperative CT",

                # Implants and Devices
                "cranial plates", "titanium mesh", "bone cement", "dural patches",
                "shunt systems", "ventriculoperitoneal shunt", "programmable shunt",
                "deep brain stimulation electrodes", "spinal cord stimulator",
                "vagus nerve stimulator", "responsive neurostimulation"
            ],

            ConceptCategory.MEDICATIONS: [
                # Anesthetics
                "propofol", "sevoflurane", "isoflurane", "desflurane", "fentanyl",
                "remifentanil", "rocuronium", "vecuronium", "succinylcholine",

                # Anticonvulsants
                "phenytoin", "levetiracetam", "carbamazepine", "valproic acid",
                "lamotrigine", "topiramate", "oxcarbazepine", "lacosamide",

                # Corticosteroids
                "dexamethasone", "methylprednisolone", "prednisolone", "hydrocortisone",

                # Hemostatic Agents
                "gelfoam", "surgicel", "thrombin", "fibrin sealant", "bone wax",

                # Contrast Agents
                "gadolinium", "iodinated contrast", "omnipaque", "magnevist",

                # Chemotherapy
                "temozolomide", "carmustine", "lomustine", "bevacizumab", "nivolumab"
            ],

            ConceptCategory.ASSESSMENTS: [
                # Neurological Scales
                "Glasgow Coma Scale", "Hunt and Hess scale", "World Federation scale",
                "Fisher scale", "modified Rankin Scale", "Barthel Index",
                "Karnofsky Performance Scale", "ASIA Impairment Scale",

                # Cognitive Assessments
                "Mini-Mental State Examination", "Montreal Cognitive Assessment",
                "Wechsler Adult Intelligence Scale", "Trail Making Test",
                "Wisconsin Card Sorting Test", "Stroop Test",

                # Functional Assessments
                "Functional Independence Measure", "Disability Rating Scale",
                "Community Integration Questionnaire", "Quality of Life scales",

                # Pain Assessments
                "Visual Analog Scale", "Numeric Rating Scale", "McGill Pain Questionnaire",
                "Oswestry Disability Index", "Neck Disability Index"
            ],

            ConceptCategory.SYMPTOMS: [
                # Neurological Symptoms
                "headache", "seizure", "focal deficit", "weakness", "paralysis",
                "numbness", "tingling", "ataxia", "dysarthria", "dysphagia",
                "diplopia", "visual field defect", "aphasia", "dysphasia",
                "memory loss", "confusion", "altered mental status",

                # Motor Symptoms
                "hemiparesis", "hemiplegia", "quadriparesis", "quadriplegia",
                "monoparesis", "paraparesis", "paraplegia", "spasticity",
                "rigidity", "tremor", "bradykinesia", "akinesia",

                # Sensory Symptoms
                "hyperesthesia", "hypoesthesia", "anesthesia", "paresthesia",
                "allodynia", "hyperalgesia", "radiculopathy", "neuropathy",

                # Cognitive Symptoms
                "dementia", "delirium", "amnesia", "agnosia", "apraxia",
                "executive dysfunction", "attention deficit", "concentration problems"
            ],

            ConceptCategory.TECHNIQUES: [
                # Surgical Techniques
                "microsurgical technique", "endoscopic technique", "minimally invasive surgery",
                "keyhole approach", "transcranial approach", "transsphenoidal approach",
                "retrosigmoid approach", "pterional approach", "orbitozygomatic approach",
                "subtemporal approach", "interhemispheric approach",

                # Anesthesia Techniques
                "awake anesthesia", "monitored anesthesia care", "total intravenous anesthesia",
                "balanced anesthesia", "regional anesthesia", "local anesthesia",

                # Monitoring Techniques
                "continuous monitoring", "intermittent monitoring", "real-time monitoring",
                "multimodal monitoring", "invasive monitoring", "non-invasive monitoring"
            ]
        }

    def _initialize_synonyms(self) -> Dict[str, List[str]]:
        """Initialize synonym mappings for medical terms"""

        return {
            # Anatomy Synonyms
            "cerebral cortex": ["cortex", "cortical tissue", "brain cortex"],
            "cerebrospinal fluid": ["CSF", "spinal fluid", "cerebral fluid"],
            "intracranial pressure": ["ICP", "brain pressure", "cranial pressure"],
            "blood-brain barrier": ["BBB", "cerebral barrier"],

            # Pathology Synonyms
            "glioblastoma": ["GBM", "glioblastoma multiforme", "grade IV astrocytoma"],
            "arteriovenous malformation": ["AVM", "cerebral AVM", "brain AVM"],
            "subarachnoid hemorrhage": ["SAH", "aneurysmal hemorrhage"],
            "traumatic brain injury": ["TBI", "head injury", "brain trauma"],
            "herniated disc": ["disc herniation", "slipped disc", "prolapsed disc"],

            # Procedures Synonyms
            "deep brain stimulation": ["DBS", "brain stimulation", "neural stimulation"],
            "stereotactic radiosurgery": ["SRS", "gamma knife", "cyberknife"],
            "anterior cervical discectomy and fusion": ["ACDF", "cervical fusion"],
            "ventriculoperitoneal shunt": ["VP shunt", "ventricular shunt"],

            # Imaging Synonyms
            "magnetic resonance imaging": ["MRI", "MR imaging", "nuclear magnetic resonance"],
            "computed tomography": ["CT", "CAT scan", "computerized tomography"],
            "positron emission tomography": ["PET", "PET scan"],
            "diffusion tensor imaging": ["DTI", "tensor imaging"],

            # Assessment Synonyms
            "Glasgow Coma Scale": ["GCS", "coma scale"],
            "modified Rankin Scale": ["mRS", "Rankin score"],
            "Mini-Mental State Examination": ["MMSE", "mini-mental"],

            # General Medical Synonyms
            "central nervous system": ["CNS", "nervous system"],
            "peripheral nervous system": ["PNS"],
            "blood oxygen level dependent": ["BOLD", "BOLD signal"],
            "functional magnetic resonance imaging": ["fMRI", "functional MRI"]
        }

    def _initialize_hierarchy(self) -> Dict[str, List[str]]:
        """Initialize concept hierarchy for semantic relationships"""

        return {
            # Brain regions hierarchy
            "brain": ["cerebrum", "cerebellum", "brainstem"],
            "cerebrum": ["frontal lobe", "parietal lobe", "temporal lobe", "occipital lobe"],
            "brainstem": ["midbrain", "pons", "medulla oblongata"],

            # Tumor hierarchy
            "brain tumor": ["primary brain tumor", "metastatic brain tumor"],
            "primary brain tumor": ["glioma", "meningioma", "pituitary adenoma"],
            "glioma": ["astrocytoma", "oligodendroglioma", "ependymoma"],
            "astrocytoma": ["pilocytic astrocytoma", "diffuse astrocytoma", "glioblastoma"],

            # Vascular hierarchy
            "cerebrovascular disease": ["stroke", "aneurysm", "arteriovenous malformation"],
            "stroke": ["ischemic stroke", "hemorrhagic stroke"],
            "hemorrhagic stroke": ["intracerebral hemorrhage", "subarachnoid hemorrhage"],

            # Spinal hierarchy
            "spinal pathology": ["degenerative disease", "spinal tumor", "spinal trauma"],
            "degenerative disease": ["herniated disc", "spinal stenosis", "spondylolisthesis"],

            # Surgical hierarchy
            "neurosurgery": ["cranial surgery", "spinal surgery", "functional surgery"],
            "cranial surgery": ["tumor resection", "vascular surgery", "trauma surgery"],
            "functional surgery": ["epilepsy surgery", "movement disorder surgery", "pain surgery"]
        }

    def _initialize_abbreviations(self) -> Dict[str, str]:
        """Initialize medical abbreviations"""

        return {
            # Common abbreviations
            "ACA": "anterior cerebral artery",
            "MCA": "middle cerebral artery",
            "PCA": "posterior cerebral artery",
            "ACoA": "anterior communicating artery",
            "PCoA": "posterior communicating artery",
            "CSF": "cerebrospinal fluid",
            "ICP": "intracranial pressure",
            "EVD": "external ventricular drain",
            "VP": "ventriculoperitoneal",
            "DBS": "deep brain stimulation",
            "VNS": "vagus nerve stimulation",
            "SRS": "stereotactic radiosurgery",
            "GKS": "gamma knife surgery",
            "ACDF": "anterior cervical discectomy and fusion",
            "PSF": "posterior spinal fusion",
            "IONM": "intraoperative neurophysiological monitoring",
            "MEP": "motor evoked potentials",
            "SSEP": "somatosensory evoked potentials",
            "BAEP": "brainstem auditory evoked potentials",
            "ECoG": "electrocorticography",
            "EMG": "electromyography",
            "EEG": "electroencephalography",
            "fMRI": "functional magnetic resonance imaging",
            "DTI": "diffusion tensor imaging",
            "DWI": "diffusion-weighted imaging",
            "PWI": "perfusion-weighted imaging",
            "SWI": "susceptibility-weighted imaging",
            "DSA": "digital subtraction angiography",
            "CTA": "computed tomography angiography",
            "MRA": "magnetic resonance angiography",
            "PET": "positron emission tomography",
            "SPECT": "single-photon emission computed tomography",
            "GCS": "Glasgow Coma Scale",
            "mRS": "modified Rankin Scale",
            "KPS": "Karnofsky Performance Scale",
            "MMSE": "Mini-Mental State Examination",
            "MoCA": "Montreal Cognitive Assessment",
            "ASIA": "American Spinal Injury Association",
            "ODI": "Oswestry Disability Index",
            "NDI": "Neck Disability Index",
            "VAS": "Visual Analog Scale",
            "NRS": "Numeric Rating Scale",
            "WHO": "World Health Organization",
            "CNS": "central nervous system",
            "PNS": "peripheral nervous system",
            "BBB": "blood-brain barrier",
            "BOLD": "blood oxygen level dependent"
        }

    def get_all_concepts(self) -> List[str]:
        """Get all neurosurgical concepts as a flat list"""
        all_concepts = []
        for category_concepts in self.concepts.values():
            all_concepts.extend(category_concepts)
        return all_concepts

    def get_concepts_by_category(self, category: ConceptCategory) -> List[str]:
        """Get concepts for a specific category"""
        return self.concepts.get(category, [])

    def get_synonyms(self, term: str) -> List[str]:
        """Get synonyms for a given term"""
        return self.synonyms.get(term.lower(), [])

    def expand_abbreviation(self, abbrev: str) -> str:
        """Expand medical abbreviation to full term"""
        return self.abbreviations.get(abbrev.upper(), abbrev)

    def get_concept_category(self, term: str) -> ConceptCategory:
        """Determine the category of a medical concept"""
        term_lower = term.lower()

        for category, concept_list in self.concepts.items():
            if term_lower in [concept.lower() for concept in concept_list]:
                return category

        return None

    def get_related_concepts(self, term: str) -> List[str]:
        """Get related concepts based on hierarchy"""
        related = []
        term_lower = term.lower()

        # Check hierarchy for parent-child relationships
        for parent, children in self.concept_hierarchy.items():
            if term_lower == parent.lower():
                related.extend(children)
            elif term_lower in [child.lower() for child in children]:
                related.append(parent)
                # Add sibling concepts
                related.extend([child for child in children if child.lower() != term_lower])

        # Add synonyms
        related.extend(self.get_synonyms(term))

        return list(set(related))

    def is_neurosurgical_term(self, term: str) -> bool:
        """Check if a term is a recognized neurosurgical concept"""
        term_lower = term.lower()
        all_concepts = self.get_all_concepts()

        # Direct match
        if term_lower in [concept.lower() for concept in all_concepts]:
            return True

        # Synonym match
        for synonyms in self.synonyms.values():
            if term_lower in [syn.lower() for syn in synonyms]:
                return True

        # Abbreviation match
        if term.upper() in self.abbreviations:
            return True

        return False

    def get_concept_weight(self, term: str) -> float:
        """Get importance weight for a concept (0.0 to 1.0)"""

        # Core neurosurgical concepts get higher weights
        high_priority_patterns = [
            r'\b(glioblastoma|meningioma|aneurysm|stroke)\b',
            r'\b(craniotomy|laminectomy|deep brain stimulation)\b',
            r'\b(frontal lobe|temporal lobe|cerebellum|brainstem)\b'
        ]

        medium_priority_patterns = [
            r'\b(tumor|surgery|imaging|assessment)\b',
            r'\b(magnetic resonance|computed tomography)\b'
        ]

        term_lower = term.lower()

        for pattern in high_priority_patterns:
            if re.search(pattern, term_lower):
                return 1.0

        for pattern in medium_priority_patterns:
            if re.search(pattern, term_lower):
                return 0.7

        # Default weight for recognized terms
        if self.is_neurosurgical_term(term):
            return 0.5

        return 0.1

# Global instance
neurosurgical_concepts = NeurosurgicalConcepts()