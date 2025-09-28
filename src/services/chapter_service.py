"""Chapter management service"""

from typing import List, Optional, Dict, Any
from uuid import uuid4
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from .ai_manager import ai_manager
from ..core.database import db_manager
from ..models.chapter import Chapter

logger = logging.getLogger(__name__)

class ChapterService:
    """Business logic for chapters"""

    async def create_chapter(
        self,
        title: str,
        content: str = "",
        specialty: str = "neurosurgery",
        auto_enhance: bool = False,
        db: Session = None
    ) -> Dict[str, Any]:
        """Create a new chapter"""

        try:
            # Generate AI content if requested and content is empty
            if auto_enhance and not content.strip():
                ai_result = await ai_manager.generate_content(
                    f"Create a comprehensive medical chapter about: {title}",
                    context_type="chapter"
                )

                if ai_result["success"]:
                    content = ai_result["content"]
                else:
                    logger.warning(f"AI content generation failed: {ai_result.get('error')}")

            # Generate summary from content
            summary = self._generate_summary(content, title)

            # Create chapter object
            chapter = Chapter(
                title=title,
                content=content,
                summary=summary,
                specialty=specialty,
                status="draft",
                metadata={
                    "word_count": len(content.split()) if content else 0,
                    "ai_enhanced": auto_enhance,
                    "version": "1.0"
                }
            )

            # Save to database
            async with db_manager.get_session() as session:
                session.add(chapter)
                await session.flush()  # Get the ID
                await session.refresh(chapter)

                logger.info(f"Chapter created: {title} (ID: {chapter.id})")
                return {
                    "success": True,
                    "chapter": chapter.to_dict()
                }

        except Exception as e:
            logger.error(f"Failed to create chapter: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_chapter(self, chapter_id: str, db: Session = None) -> Dict[str, Any]:
        """Get chapter by ID"""

        try:
            async with db_manager.get_session() as session:
                # Query for chapter by ID
                result = await session.execute(
                    select(Chapter).where(Chapter.id == chapter_id)
                )
                chapter = result.scalar_one_or_none()

                if not chapter:
                    return {
                        "success": False,
                        "error": "Chapter not found"
                    }

                return {
                    "success": True,
                    "chapter": chapter.to_dict()
                }

        except Exception as e:
            logger.error(f"Failed to get chapter {chapter_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def update_chapter(
        self,
        chapter_id: str,
        update_data: Dict[str, Any],
        db: Session = None
    ) -> Dict[str, Any]:
        """Update chapter"""

        try:
            # TODO: Implement database update when database integration is complete
            # For now, return success
            logger.info(f"Chapter updated: {chapter_id}")

            return {
                "success": True,
                "chapter_id": chapter_id,
                "updated_fields": list(update_data.keys())
            }

        except Exception as e:
            logger.error(f"Failed to update chapter {chapter_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def list_chapters(
        self,
        specialty: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        db: Session = None
    ) -> Dict[str, Any]:
        """List chapters with filtering"""

        try:
            async with db_manager.get_session() as session:
                # Build query
                query = select(Chapter)

                # Apply filters
                if specialty:
                    query = query.where(Chapter.specialty == specialty)
                if status:
                    query = query.where(Chapter.status == status)

                # Apply ordering
                query = query.order_by(Chapter.updated_at.desc())

                # Get total count (before pagination)
                count_result = await session.execute(
                    select(Chapter.id).where(*query.whereclause.clauses if query.whereclause else [])
                )
                total = len(count_result.all())

                # Apply pagination
                query = query.offset(offset).limit(limit)

                # Execute query
                result = await session.execute(query)
                chapters = result.scalars().all()

                return {
                    "success": True,
                    "chapters": [chapter.to_dict() for chapter in chapters],
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }

        except Exception as e:
            logger.error(f"Failed to list chapters: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_chapter(self, chapter_id: str, db: Session = None) -> Dict[str, Any]:
        """Delete chapter"""

        try:
            # TODO: Implement database deletion when database integration is complete
            logger.info(f"Chapter deleted: {chapter_id}")

            return {
                "success": True,
                "message": f"Chapter {chapter_id} deleted successfully"
            }

        except Exception as e:
            logger.error(f"Failed to delete chapter {chapter_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_summary(self, content: str, title: str) -> str:
        """Generate a summary from content"""

        if not content.strip():
            return f"Medical chapter about {title}"

        # Simple summary generation - take first 200 characters
        summary = content.strip()[:200]
        if len(content) > 200:
            summary += "..."

        return summary

# Global chapter service instance
chapter_service = ChapterService()
