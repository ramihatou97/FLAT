"""
Document Processing API Endpoints
Text extraction, analysis, and AI-powered document processing
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
from pydantic import BaseModel

from ..services.document_processor import document_processor
from ..services.multi_ai_manager import multi_ai_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class DocumentAnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str = "comprehensive"  # comprehensive, summary, key_points, terminology
    ai_provider: Optional[str] = None
    include_citations: bool = True
    max_length: int = 2000

class DocumentSummaryRequest(BaseModel):
    document_id: str
    summary_type: str = "executive"  # executive, detailed, bullet_points, abstract
    target_audience: str = "medical_professional"  # medical_professional, student, general
    ai_provider: Optional[str] = "claude"

class DocumentSearchRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    search_type: str = "semantic"  # semantic, keyword, citation
    max_results: int = 20
    include_snippets: bool = True

class DocumentComparisonRequest(BaseModel):
    document_ids: List[str]
    comparison_type: str = "content"  # content, methodology, conclusions, terminology
    ai_provider: Optional[str] = "gemini"

@router.post("/analyze")
async def analyze_document(request: DocumentAnalysisRequest):
    """Perform AI-powered analysis of a document"""

    try:
        logger.info(f"🔍 Starting document analysis for: {request.document_id}")

        # Get document content
        document_result = await document_processor.get_document_content(request.document_id)
        if not document_result["success"]:
            raise HTTPException(status_code=404, detail="Document not found or processing failed")

        content = document_result["content"]
        metadata = document_result["metadata"]

        # Prepare analysis prompt based on type
        analysis_prompts = {
            "comprehensive": f"""
            Perform a comprehensive medical analysis of this document:

            Title: {metadata.get('title', 'Unknown')}
            Type: {metadata.get('document_type', 'Unknown')}

            Content:
            {content}

            Please provide:
            1. Executive Summary (2-3 sentences)
            2. Key Medical Concepts and Terminology
            3. Main Clinical Findings or Conclusions
            4. Methodology (if applicable)
            5. Clinical Relevance and Applications
            6. Limitations or Considerations
            7. Related Topics for Further Study

            Format your response clearly with headers for each section.
            """,

            "summary": f"""
            Create a concise medical summary of this document:

            {content}

            Focus on:
            - Main medical concepts
            - Key findings or conclusions
            - Clinical relevance

            Keep the summary under {request.max_length} words.
            """,

            "key_points": f"""
            Extract the key medical points from this document:

            {content}

            Present as a bulleted list of the most important:
            - Clinical findings
            - Medical concepts
            - Diagnostic information
            - Treatment recommendations
            - Research conclusions
            """,

            "terminology": f"""
            Identify and explain medical terminology from this document:

            {content}

            For each medical term, provide:
            - Term definition
            - Clinical context
            - Related concepts
            - Common usage in medical practice
            """
        }

        prompt = analysis_prompts.get(request.analysis_type, analysis_prompts["comprehensive"])

        # Generate analysis using AI
        ai_result = await multi_ai_manager.generate_content(
            prompt=prompt,
            provider=request.ai_provider or "gemini",
            context_type="medical",
            max_tokens=2500,
            temperature=0.3
        )

        if not ai_result["success"]:
            raise HTTPException(status_code=400, detail=f"AI analysis failed: {ai_result['error']}")

        # Store analysis result
        analysis_result = await document_processor.store_analysis(
            document_id=request.document_id,
            analysis_type=request.analysis_type,
            analysis_content=ai_result["content"],
            metadata={
                "ai_provider": ai_result.get("provider", "unknown"),
                "model": ai_result.get("model", "unknown"),
                "tokens_used": ai_result.get("tokens_used", 0),
                "analysis_timestamp": ai_result.get("timestamp")
            }
        )

        return {
            "success": True,
            "document_id": request.document_id,
            "analysis_type": request.analysis_type,
            "analysis": ai_result["content"],
            "metadata": {
                "document_title": metadata.get("title"),
                "document_type": metadata.get("document_type"),
                "ai_provider": ai_result.get("provider"),
                "analysis_length": len(ai_result["content"]),
                "processing_time": ai_result.get("processing_time", 0)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Document analysis failed")

@router.post("/summarize")
async def summarize_document(request: DocumentSummaryRequest):
    """Generate AI-powered summary of a document"""

    try:
        logger.info(f"📝 Creating summary for document: {request.document_id}")

        # Get document content
        document_result = await document_processor.get_document_content(request.document_id)
        if not document_result["success"]:
            raise HTTPException(status_code=404, detail="Document not found")

        content = document_result["content"]
        metadata = document_result["metadata"]

        # Prepare summary prompts
        summary_prompts = {
            "executive": f"""
            Create an executive summary of this medical document for {request.target_audience}:

            {content}

            Provide a 3-4 paragraph executive summary that includes:
            1. Main purpose and scope
            2. Key findings or main points
            3. Clinical implications
            4. Actionable conclusions

            Target audience: {request.target_audience}
            """,

            "detailed": f"""
            Create a detailed summary of this medical document:

            {content}

            Include:
            - Background and context
            - Methodology (if applicable)
            - Main findings and results
            - Clinical significance
            - Limitations and considerations
            - Future directions
            """,

            "bullet_points": f"""
            Summarize this medical document in bullet points:

            {content}

            Organize into:
            • Background/Context (2-3 points)
            • Key Findings (4-5 points)
            • Clinical Implications (2-3 points)
            • Conclusions (1-2 points)
            """,

            "abstract": f"""
            Create a structured abstract for this medical document:

            {content}

            Format as a medical abstract with sections:
            - Background/Objective
            - Methods (if applicable)
            - Results/Findings
            - Conclusions

            Limit to 250-300 words total.
            """
        }

        prompt = summary_prompts.get(request.summary_type, summary_prompts["executive"])

        # Generate summary using AI
        ai_result = await multi_ai_manager.generate_content(
            prompt=prompt,
            provider=request.ai_provider,
            context_type="medical",
            max_tokens=1500,
            temperature=0.4
        )

        if not ai_result["success"]:
            raise HTTPException(status_code=400, detail=f"Summary generation failed: {ai_result['error']}")

        return {
            "success": True,
            "document_id": request.document_id,
            "summary_type": request.summary_type,
            "summary": ai_result["content"],
            "metadata": {
                "document_title": metadata.get("title"),
                "target_audience": request.target_audience,
                "ai_provider": ai_result.get("provider"),
                "word_count": len(ai_result["content"].split()),
                "summary_timestamp": ai_result.get("timestamp")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document summarization failed: {e}")
        raise HTTPException(status_code=500, detail="Document summarization failed")

@router.post("/search")
async def search_documents(request: DocumentSearchRequest):
    """Search through processed documents using various methods"""

    try:
        logger.info(f"🔍 Searching documents with query: {request.query}")

        search_result = await document_processor.search_documents(
            query=request.query,
            document_ids=request.document_ids,
            search_type=request.search_type,
            max_results=request.max_results,
            include_snippets=request.include_snippets
        )

        if not search_result["success"]:
            raise HTTPException(status_code=400, detail=search_result["error"])

        return {
            "success": True,
            "query": request.query,
            "search_type": request.search_type,
            "results": search_result["results"],
            "total_found": search_result["total_found"],
            "search_metadata": {
                "documents_searched": search_result.get("documents_searched", 0),
                "search_time_ms": search_result.get("search_time_ms", 0),
                "relevance_threshold": search_result.get("relevance_threshold", 0.0)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail="Document search failed")

@router.post("/compare")
async def compare_documents(request: DocumentComparisonRequest):
    """Compare multiple documents using AI analysis"""

    try:
        logger.info(f"📊 Comparing {len(request.document_ids)} documents")

        if len(request.document_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 documents required for comparison")

        if len(request.document_ids) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 documents can be compared at once")

        # Get content for all documents
        documents_content = []
        for doc_id in request.document_ids:
            doc_result = await document_processor.get_document_content(doc_id)
            if doc_result["success"]:
                documents_content.append({
                    "id": doc_id,
                    "title": doc_result["metadata"].get("title", f"Document {doc_id}"),
                    "content": doc_result["content"][:3000]  # Limit content for comparison
                })

        if len(documents_content) < 2:
            raise HTTPException(status_code=400, detail="Could not retrieve content for comparison")

        # Prepare comparison prompt
        comparison_prompts = {
            "content": f"""
            Compare the following medical documents and provide a detailed analysis:

            {chr(10).join([f"Document {i+1}: {doc['title']}{chr(10)}{doc['content']}{chr(10)}" for i, doc in enumerate(documents_content)])}

            Provide a comparison covering:
            1. Content Similarities
            2. Key Differences
            3. Complementary Information
            4. Conflicting Information (if any)
            5. Clinical Relevance Comparison
            6. Recommended Reading Order
            """,

            "methodology": f"""
            Compare the methodologies used in these medical documents:

            {chr(10).join([f"Document {i+1}: {doc['title']}{chr(10)}{doc['content']}{chr(10)}" for i, doc in enumerate(documents_content)])}

            Analyze:
            1. Research Methods Used
            2. Study Design Comparison
            3. Data Collection Approaches
            4. Analysis Techniques
            5. Strengths and Limitations
            6. Methodological Quality Assessment
            """,

            "conclusions": f"""
            Compare the conclusions and findings from these medical documents:

            {chr(10).join([f"Document {i+1}: {doc['title']}{chr(10)}{doc['content']}{chr(10)}" for i, doc in enumerate(documents_content)])}

            Compare:
            1. Main Conclusions
            2. Supporting Evidence
            3. Clinical Implications
            4. Agreement/Disagreement Between Documents
            5. Evidence Quality
            6. Practice Recommendations
            """
        }

        prompt = comparison_prompts.get(request.comparison_type, comparison_prompts["content"])

        # Generate comparison using AI
        ai_result = await multi_ai_manager.generate_content(
            prompt=prompt,
            provider=request.ai_provider,
            context_type="medical",
            max_tokens=3000,
            temperature=0.3
        )

        if not ai_result["success"]:
            raise HTTPException(status_code=400, detail=f"Comparison generation failed: {ai_result['error']}")

        return {
            "success": True,
            "comparison_type": request.comparison_type,
            "documents_compared": [{"id": doc["id"], "title": doc["title"]} for doc in documents_content],
            "comparison_analysis": ai_result["content"],
            "metadata": {
                "ai_provider": ai_result.get("provider"),
                "documents_count": len(documents_content),
                "analysis_timestamp": ai_result.get("timestamp"),
                "comparison_length": len(ai_result["content"])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document comparison failed: {e}")
        raise HTTPException(status_code=500, detail="Document comparison failed")

@router.get("/extract/{document_id}")
async def extract_text(document_id: str):
    """Extract and return processed text from a document"""

    try:
        result = await document_processor.get_document_content(document_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail="Document not found or processing failed")

        return {
            "success": True,
            "document_id": document_id,
            "content": result["content"],
            "metadata": result["metadata"],
            "extraction_info": {
                "content_length": len(result["content"]),
                "word_count": len(result["content"].split()),
                "extraction_method": result.get("extraction_method", "unknown"),
                "processing_timestamp": result.get("processing_timestamp")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Text extraction failed")

@router.get("/processing-status/{document_id}")
async def get_processing_status(document_id: str):
    """Get the processing status of a document"""

    try:
        status = await document_processor.get_processing_status(document_id)

        if not status["success"]:
            raise HTTPException(status_code=404, detail="Document not found")

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get processing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing status")

@router.post("/reprocess/{document_id}")
async def reprocess_document(document_id: str):
    """Reprocess a document (extract text, update metadata)"""

    try:
        logger.info(f"🔄 Reprocessing document: {document_id}")

        result = await document_processor.reprocess_document(document_id)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "success": True,
            "message": "Document reprocessing initiated",
            "document_id": document_id,
            "processing_info": result.get("processing_info", {})
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document reprocessing failed: {e}")
        raise HTTPException(status_code=500, detail="Document reprocessing failed")

@router.get("/analytics/processing")
async def get_processing_analytics():
    """Get analytics about document processing"""

    try:
        analytics = await document_processor.get_processing_analytics()

        return {
            "success": True,
            "analytics": analytics,
            "timestamp": analytics.get("timestamp")
        }

    except Exception as e:
        logger.error(f"Failed to get processing analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing analytics")