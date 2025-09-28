"""
Document Library API Endpoints
Upload and manage medical documents, books, chapters, papers
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
import logging
from pydantic import BaseModel

from ..services.document_service import document_service

logger = logging.getLogger(__name__)
router = APIRouter()

class DocumentMetadata(BaseModel):
    title: str
    document_type: str  # book, chapter, paper, reference, etc.
    authors: Optional[List[str]] = None
    specialty: Optional[str] = None
    subspecialty: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    isbn: Optional[str] = None
    keywords: Optional[List[str]] = None

class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    specialty: Optional[str] = None
    parent_id: Optional[str] = None

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    authors: Optional[str] = Form(None),  # JSON string of authors list
    specialty: Optional[str] = Form(None),
    subspecialty: Optional[str] = Form(None),
    journal: Optional[str] = Form(None),
    publication_date: Optional[str] = Form(None),
    doi: Optional[str] = Form(None),
    pmid: Optional[str] = Form(None),
    isbn: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None)  # JSON string of keywords list
):
    """Upload a document to the library (PDF, DOCX, TXT, MD)"""

    try:
        # Read file content
        file_content = await file.read()

        # Parse JSON fields
        import json
        parsed_authors = json.loads(authors) if authors else []
        parsed_keywords = json.loads(keywords) if keywords else []

        # Prepare metadata
        metadata = {}
        if journal:
            metadata["journal"] = journal
        if publication_date:
            metadata["publication_date"] = publication_date
        if doi:
            metadata["doi"] = doi
        if pmid:
            metadata["pmid"] = pmid
        if isbn:
            metadata["isbn"] = isbn
        if parsed_keywords:
            metadata["keywords"] = parsed_keywords

        # Upload document
        result = await document_service.upload_document(
            file_content=file_content,
            filename=file.filename,
            title=title,
            document_type=document_type,
            authors=parsed_authors,
            specialty=specialty,
            metadata=metadata
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "message": "Document uploaded successfully",
            "document": result["document"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")

@router.get("/{document_id}")
async def get_document(document_id: str):
    """Get document details by ID"""

    try:
        result = await document_service.get_document(document_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])

        return result["document"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document")

@router.get("/{document_id}/content")
async def get_document_content(document_id: str):
    """Get extracted text content of document"""

    try:
        result = await document_service.get_document_content(document_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document content")

@router.get("/")
async def list_documents(
    document_type: Optional[str] = None,
    specialty: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """List documents with filtering and search"""

    try:
        result = await document_service.list_documents(
            document_type=document_type,
            specialty=specialty,
            status=status,
            search=search,
            limit=limit,
            offset=offset
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "documents": result["documents"],
            "total": result["total"],
            "limit": limit,
            "offset": offset,
            "filters": {
                "document_type": document_type,
                "specialty": specialty,
                "status": status,
                "search": search
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete document from library"""

    try:
        result = await document_service.delete_document(document_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])

        return {"message": result["message"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@router.post("/collections")
async def create_collection(collection_data: CollectionCreate):
    """Create a new document collection/folder"""

    try:
        result = await document_service.create_collection(
            name=collection_data.name,
            description=collection_data.description,
            specialty=collection_data.specialty,
            parent_id=collection_data.parent_id
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "message": "Collection created successfully",
            "collection": result["collection"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to create collection")

@router.get("/stats/overview")
async def get_library_stats():
    """Get library statistics and overview"""

    try:
        result = await document_service.get_library_stats()

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result["stats"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get library stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get library stats")

@router.get("/types/available")
async def get_document_types():
    """Get available document types"""

    return {
        "document_types": [
            {"value": "book", "label": "Medical Book", "description": "Complete medical textbook"},
            {"value": "chapter", "label": "Book Chapter", "description": "Individual chapter from medical book"},
            {"value": "paper", "label": "Research Paper", "description": "Peer-reviewed research article"},
            {"value": "reference", "label": "Reference Material", "description": "Quick reference guide or manual"},
            {"value": "guideline", "label": "Clinical Guideline", "description": "Medical practice guideline"},
            {"value": "case_study", "label": "Case Study", "description": "Clinical case report"},
            {"value": "review", "label": "Review Article", "description": "Systematic or narrative review"},
            {"value": "thesis", "label": "Thesis/Dissertation", "description": "Academic thesis or dissertation"}
        ],
        "specialties": [
            "neurosurgery", "cardiology", "oncology", "neurology",
            "radiology", "pathology", "internal_medicine", "surgery",
            "pediatrics", "psychiatry", "emergency_medicine", "anesthesiology"
        ]
    }