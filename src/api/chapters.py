"""
Medical Chapters API Endpoints
Simple chapter management for personal use
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
import logging
from pydantic import BaseModel

from ..services.chapter_service import chapter_service

logger = logging.getLogger(__name__)
router = APIRouter()

class ChapterCreate(BaseModel):
    title: str
    content: str = ""
    specialty: str = "neurosurgery"
    auto_enhance: bool = False

class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    specialty: Optional[str] = None

@router.get("/{chapter_id}")
async def get_chapter(chapter_id: str):
    """Get chapter by ID"""
    try:
        result = await chapter_service.get_chapter(chapter_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Chapter not found"))
        return result["chapter"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chapter {chapter_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{chapter_id}")
async def update_chapter(chapter_id: str, chapter_data: ChapterUpdate):
    """Update chapter content"""
    try:
        update_data = chapter_data.dict(exclude_unset=True)
        result = await chapter_service.update_chapter(chapter_id, update_data)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))

        return {
            "message": "Chapter updated successfully",
            "chapter_id": chapter_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update chapter {chapter_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/")
async def list_chapters(
    specialty: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """List chapters with filtering"""
    try:
        result = await chapter_service.list_chapters(
            specialty=specialty,
            status=status,
            limit=limit,
            offset=offset
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to list chapters"))

        return {
            "chapters": result["chapters"],
            "total": result["total"],
            "limit": limit,
            "offset": offset
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list chapters: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/")
async def create_chapter(chapter_data: ChapterCreate):
    """Create a new chapter"""
    try:
        result = await chapter_service.create_chapter(
            title=chapter_data.title,
            content=chapter_data.content,
            specialty=chapter_data.specialty,
            auto_enhance=chapter_data.auto_enhance
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Creation failed"))

        return {
            "message": "Chapter created successfully",
            "chapter": result["chapter"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create chapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{chapter_id}")
async def delete_chapter(chapter_id: str):
    """Delete chapter"""
    try:
        result = await chapter_service.delete_chapter(chapter_id)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Deletion failed"))

        return {"message": f"Chapter {chapter_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete chapter {chapter_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

