"""Research APIs for PubMed and Google Scholar integration"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

from ..core.config import settings

logger = logging.getLogger(__name__)

class ResearchAPIManager:
    """Manager for research APIs including PubMed and Google Scholar"""

    def __init__(self):
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.scholar_available = bool(settings.scholar_api_key or settings.serpapi_key)

    async def search_pubmed(
        self,
        query: str,
        max_results: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        article_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Search PubMed for medical literature"""

        try:
            # Build search query
            search_terms = [query]

            # Add date filters
            if year_from or year_to:
                if year_from and year_to:
                    search_terms.append(f"{year_from}:{year_to}[pdat]")
                elif year_from:
                    search_terms.append(f"{year_from}:3000[pdat]")
                elif year_to:
                    search_terms.append(f"1900:{year_to}[pdat]")

            # Add article type filters
            if article_types:
                for article_type in article_types:
                    search_terms.append(f"{article_type}[ptyp]")

            full_query = " AND ".join(search_terms)

            async with aiohttp.ClientSession() as session:
                # Step 1: Search for PMIDs
                search_params = {
                    "db": "pubmed",
                    "term": full_query,
                    "retmax": max_results,
                    "retmode": "json"
                }

                if settings.pubmed_email:
                    search_params["email"] = settings.pubmed_email
                if settings.pubmed_api_key:
                    search_params["api_key"] = settings.pubmed_api_key

                async with session.get(
                    f"{self.pubmed_base_url}/esearch.fcgi",
                    params=search_params
                ) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"PubMed search failed: {response.status}",
                            "results": []
                        }

                    search_data = await response.json()
                    pmids = search_data.get("esearchresult", {}).get("idlist", [])

                    if not pmids:
                        return {
                            "success": True,
                            "results": [],
                            "total_count": 0,
                            "query": query
                        }

                # Step 2: Fetch article details
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "xml"
                }

                if settings.pubmed_email:
                    fetch_params["email"] = settings.pubmed_email
                if settings.pubmed_api_key:
                    fetch_params["api_key"] = settings.pubmed_api_key

                async with session.get(
                    f"{self.pubmed_base_url}/efetch.fcgi",
                    params=fetch_params
                ) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"PubMed fetch failed: {response.status}",
                            "results": []
                        }

                    xml_content = await response.text()
                    articles = self._parse_pubmed_xml(xml_content)

                    return {
                        "success": True,
                        "results": articles,
                        "total_count": len(articles),
                        "query": query,
                        "source": "pubmed"
                    }

        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    async def search_google_scholar(
        self,
        query: str,
        max_results: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search Google Scholar using SerpAPI"""

        if not settings.serpapi_key:
            return {
                "success": False,
                "error": "Google Scholar API not configured (SERPAPI_KEY required)",
                "results": []
            }

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "engine": "google_scholar",
                    "q": query,
                    "api_key": settings.serpapi_key,
                    "num": max_results
                }

                if year_from:
                    params["as_ylo"] = year_from
                if year_to:
                    params["as_yhi"] = year_to

                async with session.get(
                    "https://serpapi.com/search.json",
                    params=params
                ) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"Google Scholar search failed: {response.status}",
                            "results": []
                        }

                    data = await response.json()
                    organic_results = data.get("organic_results", [])

                    # Parse results
                    articles = []
                    for result in organic_results:
                        article = {
                            "title": result.get("title", ""),
                            "authors": result.get("publication_info", {}).get("authors", []),
                            "abstract": result.get("snippet", ""),
                            "publication_info": result.get("publication_info", {}),
                            "link": result.get("link", ""),
                            "cited_by_count": result.get("inline_links", {}).get("cited_by", {}).get("total", 0),
                            "year": self._extract_year_from_publication_info(result.get("publication_info", {})),
                            "source": "google_scholar"
                        }
                        articles.append(article)

                    return {
                        "success": True,
                        "results": articles,
                        "total_count": len(articles),
                        "query": query,
                        "source": "google_scholar"
                    }

        except Exception as e:
            logger.error(f"Google Scholar search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    async def search_multiple_sources(
        self,
        query: str,
        sources: List[str] = None,
        max_results_per_source: int = 5
    ) -> Dict[str, Any]:
        """Search multiple research sources simultaneously"""

        if not sources:
            sources = ["pubmed"]
            if self.scholar_available:
                sources.append("google_scholar")

        # Execute searches concurrently
        tasks = []
        if "pubmed" in sources:
            tasks.append(self.search_pubmed(query, max_results_per_source))
        if "google_scholar" in sources and self.scholar_available:
            tasks.append(self.search_google_scholar(query, max_results_per_source))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        combined_results = []
        source_results = {}
        total_count = 0

        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get("success"):
                source = sources[i]
                source_results[source] = result
                combined_results.extend(result["results"])
                total_count += result["total_count"]

        # Sort by relevance (basic implementation)
        combined_results.sort(key=lambda x: x.get("cited_by_count", 0), reverse=True)

        return {
            "success": True,
            "results": combined_results,
            "total_count": total_count,
            "sources_searched": list(source_results.keys()),
            "source_results": source_results,
            "query": query
        }

    async def get_article_details(self, pmid: str) -> Dict[str, Any]:
        """Get detailed information about a specific PubMed article"""

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "db": "pubmed",
                    "id": pmid,
                    "retmode": "xml"
                }

                if settings.pubmed_email:
                    params["email"] = settings.pubmed_email
                if settings.pubmed_api_key:
                    params["api_key"] = settings.pubmed_api_key

                async with session.get(
                    f"{self.pubmed_base_url}/efetch.fcgi",
                    params=params
                ) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"Failed to fetch article details: {response.status}"
                        }

                    xml_content = await response.text()
                    articles = self._parse_pubmed_xml(xml_content, detailed=True)

                    if articles:
                        return {
                            "success": True,
                            "article": articles[0]
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Article not found"
                        }

        except Exception as e:
            logger.error(f"Failed to get article details for PMID {pmid}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_pubmed_xml(self, xml_content: str, detailed: bool = False) -> List[Dict[str, Any]]:
        """Parse PubMed XML response"""

        try:
            root = ET.fromstring(xml_content)
            articles = []

            for article_elem in root.findall(".//PubmedArticle"):
                article = {}

                # Basic information
                title_elem = article_elem.find(".//ArticleTitle")
                article["title"] = title_elem.text if title_elem is not None else ""

                # Authors
                authors = []
                for author_elem in article_elem.findall(".//Author"):
                    lastname = author_elem.find("LastName")
                    forename = author_elem.find("ForeName")
                    if lastname is not None:
                        author_name = lastname.text
                        if forename is not None:
                            author_name = f"{forename.text} {author_name}"
                        authors.append(author_name)

                article["authors"] = authors

                # Abstract
                abstract_elem = article_elem.find(".//Abstract/AbstractText")
                article["abstract"] = abstract_elem.text if abstract_elem is not None else ""

                # Publication info
                journal_elem = article_elem.find(".//Journal/Title")
                article["journal"] = journal_elem.text if journal_elem is not None else ""

                # Publication date
                pub_date = article_elem.find(".//PubDate")
                if pub_date is not None:
                    year_elem = pub_date.find("Year")
                    month_elem = pub_date.find("Month")
                    article["publication_year"] = year_elem.text if year_elem is not None else ""
                    article["publication_month"] = month_elem.text if month_elem is not None else ""

                # PMID
                pmid_elem = article_elem.find(".//PMID")
                article["pmid"] = pmid_elem.text if pmid_elem is not None else ""

                # DOI
                doi_elem = article_elem.find(".//ELocationID[@EIdType='doi']")
                article["doi"] = doi_elem.text if doi_elem is not None else ""

                # If detailed, add more information
                if detailed:
                    # Keywords
                    keywords = []
                    for keyword_elem in article_elem.findall(".//Keyword"):
                        if keyword_elem.text:
                            keywords.append(keyword_elem.text)
                    article["keywords"] = keywords

                    # MeSH terms
                    mesh_terms = []
                    for mesh_elem in article_elem.findall(".//MeshHeading/DescriptorName"):
                        if mesh_elem.text:
                            mesh_terms.append(mesh_elem.text)
                    article["mesh_terms"] = mesh_terms

                article["source"] = "pubmed"
                articles.append(article)

            return articles

        except Exception as e:
            logger.error(f"Failed to parse PubMed XML: {e}")
            return []

    def _extract_year_from_publication_info(self, publication_info: Dict[str, Any]) -> Optional[int]:
        """Extract publication year from Google Scholar publication info"""

        try:
            # Try to extract year from summary string
            summary = publication_info.get("summary", "")
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', summary)
            if year_match:
                return int(year_match.group())
        except:
            pass

        return None

    def get_available_sources(self) -> Dict[str, Any]:
        """Get available research sources"""

        return {
            "available_sources": {
                "pubmed": {
                    "name": "PubMed",
                    "description": "NCBI PubMed database of biomedical literature",
                    "available": True,
                    "features": ["abstracts", "mesh_terms", "keywords", "doi"]
                },
                "google_scholar": {
                    "name": "Google Scholar",
                    "description": "Academic literature search engine",
                    "available": self.scholar_available,
                    "features": ["citations", "full_text_links", "related_articles"]
                }
            },
            "article_types": [
                "journal article", "review", "systematic review",
                "meta-analysis", "case reports", "clinical trial"
            ],
            "specialties": [
                "neurosurgery", "cardiology", "oncology", "neurology",
                "radiology", "internal medicine", "surgery"
            ]
        }

# Global research API manager instance
research_api = ResearchAPIManager()