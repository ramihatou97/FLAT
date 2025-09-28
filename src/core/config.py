"""Comprehensive configuration for Medical Knowledge Platform"""

from typing import List, Optional, Dict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Single source of truth for configuration"""

    # Application
    app_name: str = "Medical Knowledge Platform"
    version: str = "3.0.0"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "dev_secret_key_change_in_production"

    # Database
    database_url: str = "postgresql://medical_user:medical_password@database:5432/medical_platform"
    database_pool_size: int = 10
    db_echo: bool = False

    # ===== AI SERVICE APIS =====
    # 1. OpenAI
    openai_api_key: Optional[str] = None

    # 2. Google AI (Gemini)
    google_api_key: Optional[str] = None
    google_search_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None

    # 3. Anthropic Claude
    claude_api_key: Optional[str] = None

    # 4. Perplexity
    perplexity_api_key: Optional[str] = None

    # ===== RESEARCH APIS =====
    # 5. PubMed
    pubmed_api_key: Optional[str] = None
    pubmed_email: Optional[str] = None

    # 6. Google Scholar
    scholar_api_key: Optional[str] = None

    # Additional APIs
    serpapi_key: Optional[str] = None
    scraperapi_key: Optional[str] = None

    # AI Provider Settings
    default_ai_provider: str = "gemini"
    enable_multi_provider_synthesis: bool = True
    max_concurrent_ai_requests: int = 3

    # Medical Domain
    medical_specialties: List[str] = [
        "neurosurgery", "cardiology", "oncology",
        "neurology", "radiology", "pathology"
    ]

    evidence_levels: Dict[str, float] = {
        "systematic_review": 1.0,
        "randomized_trial": 0.8,
        "cohort_study": 0.6,
        "case_report": 0.4,
        "expert_opinion": 0.2
    }

    # Intelligence & Enhancement
    enable_contextual_ai: bool = True
    query_enhancement_level: int = 3

    # Document Processing
    max_file_size_mb: int = 100
    allowed_file_types: str = "pdf,docx,txt,md"
    enable_ocr: bool = True
    enable_figure_extraction: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

settings = Settings()
