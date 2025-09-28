"""Document Library Service for Medical Knowledge Platform"""

import os
import shutil
import logging
from typing import Dict, Any, List, Optional, BinaryIO
from uuid import uuid4
from datetime import datetime
from pathlib import Path
import mimetypes

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from ..core.database import db_manager
from ..core.config import settings
from ..models.document import Document, DocumentType, ProcessingStatus, LibraryCollection

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for managing document library"""

    def __init__(self):
        self.upload_path = Path("uploads/documents")
        self.upload_path.mkdir(parents=True, exist_ok=True)

        # File type validation
        self.allowed_extensions = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'md': 'text/markdown'
        }

    async def upload_document(
        self,
        file_content: bytes,
        filename: str,
        title: str,
        document_type: str,
        authors: List[str] = None,
        specialty: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Upload and process a document"""

        try:
            # Validate file
            validation_result = self._validate_file(filename, len(file_content))
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }

            # Generate unique filename
            file_extension = Path(filename).suffix.lower().lstrip('.')
            unique_filename = f"{uuid4()}.{file_extension}"
            file_path = self.upload_path / unique_filename

            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)

            # Create document record
            document = Document(
                title=title,
                authors=authors or [],
                document_type=document_type,
                specialty=specialty,
                original_filename=filename,
                file_path=str(file_path),
                file_size_bytes=len(file_content),
                file_type=file_extension,
                mime_type=self.allowed_extensions.get(file_extension),
                processing_status=ProcessingStatus.PENDING.value,
                uploaded_by="system"  # TODO: Add user management
            )

            # Add metadata if provided
            if metadata:
                if "publication_date" in metadata:
                    try:
                        document.publication_date = datetime.fromisoformat(metadata["publication_date"])
                    except:
                        pass
                document.journal = metadata.get("journal")
                document.doi = metadata.get("doi")
                document.pmid = metadata.get("pmid")
                document.isbn = metadata.get("isbn")
                document.keywords = metadata.get("keywords", [])

            # Save to database
            async with db_manager.get_session() as session:
                session.add(document)
                await session.flush()
                await session.refresh(document)

                logger.info(f"Document uploaded: {title} (ID: {document.id})")

                # Start background processing
                await self._schedule_processing(document.id)

                return {
                    "success": True,
                    "document": document.to_dict(),
                    "message": "Document uploaded successfully and processing started"
                }

        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get document by ID"""

        try:
            async with db_manager.get_session() as session:
                result = await session.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()

                if not document:
                    return {
                        "success": False,
                        "error": "Document not found"
                    }

                return {
                    "success": True,
                    "document": document.to_dict()
                }

        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def list_documents(
        self,
        document_type: Optional[str] = None,
        specialty: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List documents with filtering"""

        try:
            async with db_manager.get_session() as session:
                # Build query
                query = select(Document)

                # Apply filters
                if document_type:
                    query = query.where(Document.document_type == document_type)
                if specialty:
                    query = query.where(Document.specialty == specialty)
                if status:
                    query = query.where(Document.processing_status == status)
                if search:
                    search_term = f"%{search}%"
                    query = query.where(
                        Document.title.ilike(search_term) |
                        Document.authors.astext.ilike(search_term)
                    )

                # Get total count
                count_query = select(func.count(Document.id)).where(*query.whereclause.clauses if query.whereclause else [])
                count_result = await session.execute(count_query)
                total = count_result.scalar()

                # Apply ordering and pagination
                query = query.order_by(Document.created_at.desc())
                query = query.offset(offset).limit(limit)

                # Execute query
                result = await session.execute(query)
                documents = result.scalars().all()

                return {
                    "success": True,
                    "documents": [doc.to_dict() for doc in documents],
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }

        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete document and its file"""

        try:
            async with db_manager.get_session() as session:
                # Get document
                result = await session.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()

                if not document:
                    return {
                        "success": False,
                        "error": "Document not found"
                    }

                # Delete file
                try:
                    file_path = Path(document.file_path)
                    if file_path.exists():
                        file_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete file {document.file_path}: {e}")

                # Delete from database
                await session.delete(document)
                await session.commit()

                logger.info(f"Document deleted: {document.title} (ID: {document_id})")

                return {
                    "success": True,
                    "message": "Document deleted successfully"
                }

        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_document_content(self, document_id: str) -> Dict[str, Any]:
        """Get extracted text content of document"""

        try:
            async with db_manager.get_session() as session:
                result = await session.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()

                if not document:
                    return {
                        "success": False,
                        "error": "Document not found"
                    }

                if not document.extracted_text:
                    return {
                        "success": False,
                        "error": "Document content not yet extracted"
                    }

                return {
                    "success": True,
                    "document_id": document_id,
                    "title": document.title,
                    "content": document.extracted_text,
                    "word_count": document.word_count,
                    "page_count": document.page_count
                }

        except Exception as e:
            logger.error(f"Failed to get document content {document_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_collection(
        self,
        name: str,
        description: str = None,
        specialty: str = None,
        parent_id: str = None
    ) -> Dict[str, Any]:
        """Create a new document collection"""

        try:
            collection = LibraryCollection(
                name=name,
                description=description,
                specialty=specialty,
                parent_id=parent_id if parent_id else None,
                created_by="system"  # TODO: Add user management
            )

            async with db_manager.get_session() as session:
                session.add(collection)
                await session.flush()
                await session.refresh(collection)

                return {
                    "success": True,
                    "collection": {
                        "id": str(collection.id),
                        "name": collection.name,
                        "description": collection.description,
                        "specialty": collection.specialty,
                        "document_count": collection.document_count,
                        "created_at": collection.created_at.isoformat()
                    }
                }

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_library_stats(self) -> Dict[str, Any]:
        """Get library statistics"""

        try:
            async with db_manager.get_session() as session:
                # Total documents
                total_docs = await session.execute(select(func.count(Document.id)))
                total_documents = total_docs.scalar()

                # Documents by type
                type_stats = await session.execute(
                    select(Document.document_type, func.count(Document.id))
                    .group_by(Document.document_type)
                )
                documents_by_type = {row[0]: row[1] for row in type_stats.fetchall()}

                # Documents by specialty
                specialty_stats = await session.execute(
                    select(Document.specialty, func.count(Document.id))
                    .where(Document.specialty.isnot(None))
                    .group_by(Document.specialty)
                )
                documents_by_specialty = {row[0]: row[1] for row in specialty_stats.fetchall()}

                # Processing status
                status_stats = await session.execute(
                    select(Document.processing_status, func.count(Document.id))
                    .group_by(Document.processing_status)
                )
                documents_by_status = {row[0]: row[1] for row in status_stats.fetchall()}

                # Total storage
                storage_stats = await session.execute(select(func.sum(Document.file_size_bytes)))
                total_storage_bytes = storage_stats.scalar() or 0

                return {
                    "success": True,
                    "stats": {
                        "total_documents": total_documents,
                        "documents_by_type": documents_by_type,
                        "documents_by_specialty": documents_by_specialty,
                        "documents_by_status": documents_by_status,
                        "total_storage_bytes": total_storage_bytes,
                        "total_storage_mb": round(total_storage_bytes / (1024 * 1024), 2)
                    }
                }

        except Exception as e:
            logger.error(f"Failed to get library stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _validate_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate uploaded file"""

        # Check file extension
        file_extension = Path(filename).suffix.lower().lstrip('.')
        if file_extension not in self.allowed_extensions:
            return {
                "valid": False,
                "error": f"File type .{file_extension} not supported. Allowed: {', '.join(self.allowed_extensions.keys())}"
            }

        # Check file size
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return {
                "valid": False,
                "error": f"File size {file_size / (1024 * 1024):.1f}MB exceeds maximum {settings.max_file_size_mb}MB"
            }

        return {"valid": True}

    async def _schedule_processing(self, document_id: str):
        """Schedule document processing (placeholder for background task)"""
        # TODO: Implement background processing with Celery or similar
        logger.info(f"Processing scheduled for document {document_id}")

# Global document service instance
document_service = DocumentService()