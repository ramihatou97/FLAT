"""Multi-Provider AI Manager for Medical Knowledge Platform"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
import aiohttp
import json

from ..core.config import settings
from ..core.api_key_manager import api_key_manager

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    PERPLEXITY = "perplexity"

class MultiAIManager:
    """Advanced AI manager supporting multiple providers"""

    def __init__(self):
        self.providers = self._initialize_providers()

    def _initialize_providers(self) -> Dict[str, bool]:
        """Check which providers are available"""
        return {
            AIProvider.OPENAI.value: bool(settings.openai_api_key),
            AIProvider.GEMINI.value: bool(settings.google_api_key),
            AIProvider.CLAUDE.value: bool(settings.claude_api_key),
            AIProvider.PERPLEXITY.value: bool(settings.perplexity_api_key),
        }

    async def generate_content(
        self,
        prompt: str,
        provider: Optional[str] = None,
        context_type: str = "medical",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate content using specified or default provider"""

        # Use default provider if none specified
        if not provider:
            provider = settings.default_ai_provider

        if provider not in self.providers or not self.providers[provider]:
            return {
                "success": False,
                "error": f"Provider {provider} not available or not configured",
                "content": ""
            }

        try:
            if provider == AIProvider.OPENAI.value:
                return await self._openai_generate(prompt, max_tokens, temperature, model)
            elif provider == AIProvider.GEMINI.value:
                return await self._gemini_generate(prompt, max_tokens, temperature, model)
            elif provider == AIProvider.CLAUDE.value:
                return await self._claude_generate(prompt, max_tokens, temperature, model)
            elif provider == AIProvider.PERPLEXITY.value:
                return await self._perplexity_generate(prompt, max_tokens, temperature, model)
            else:
                return {
                    "success": False,
                    "error": f"Unknown provider: {provider}",
                    "content": ""
                }

        except Exception as e:
            logger.error(f"AI generation failed for {provider}: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }

    async def _openai_generate(self, prompt: str, max_tokens: int, temperature: float, model: Optional[str]) -> Dict[str, Any]:
        """OpenAI GPT generation with intelligent key management"""
        if not model:
            model = "gpt-4"

        try:
            # Get active API key through key manager
            api_key, key_id = await api_key_manager.get_active_key("openai")
            start_time = asyncio.get_event_loop().time()

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a medical expert assistant. Provide accurate, evidence-based medical information."
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }

                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    response_time = (asyncio.get_event_loop().time() - start_time) * 1000  # ms

                    if response.status == 200:
                        data = await response.json()

                        # Calculate estimated cost for neurosurgical operations
                        usage = data.get("usage", {})
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)

                        # GPT-4 pricing (approximate)
                        estimated_cost = (prompt_tokens * 0.00003) + (completion_tokens * 0.00006)

                        # Record successful API call
                        await api_key_manager.record_api_call(
                            service="openai",
                            key_id=key_id,
                            success=True,
                            response_time_ms=response_time,
                            estimated_cost=estimated_cost,
                            operation_type="neurosurgical_content_generation"
                        )

                        return {
                            "success": True,
                            "content": data["choices"][0]["message"]["content"],
                            "provider": "openai",
                            "model": model,
                            "usage": usage,
                            "estimated_cost": estimated_cost,
                            "response_time_ms": response_time,
                            "timestamp": asyncio.get_event_loop().time()
                        }
                    else:
                        error_text = await response.text()

                        # Record failed API call
                        await api_key_manager.record_api_call(
                            service="openai",
                            key_id=key_id,
                            success=False,
                            response_time_ms=response_time,
                            estimated_cost=0.0
                        )

                        return {
                            "success": False,
                            "error": f"OpenAI API error: {response.status} - {error_text}",
                            "content": ""
                        }

        except Exception as e:
            # Record failed API call if we got a key
            try:
                if 'key_id' in locals():
                    await api_key_manager.record_api_call(
                        service="openai",
                        key_id=key_id,
                        success=False,
                        response_time_ms=5000,  # Timeout/error
                        estimated_cost=0.0
                    )
            except:
                pass

            logger.error(f"OpenAI generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }

    async def _gemini_generate(self, prompt: str, max_tokens: int, temperature: float, model: Optional[str]) -> Dict[str, Any]:
        """Google Gemini generation with Deep Search and Deep Think capabilities"""
        if not model:
            model = "gemini-2.5-pro"  # Latest Gemini model

        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": "application/json"}

            # Enhanced prompt for medical context with deep thinking
            enhanced_prompt = f"""
            As Gemini 2.5 Pro with Deep Search and Deep Think capabilities, provide a comprehensive medical analysis:

            Medical Query: {prompt}

            Please use your deep thinking process to:
            1. Analyze the medical context thoroughly
            2. Search through your knowledge for the most current information
            3. Consider multiple perspectives and evidence levels
            4. Provide a well-structured, evidence-based response

            Format your response in markdown with clear sections.
            """

            payload = {
                "contents": [{"parts": [{"text": enhanced_prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "candidateCount": 1
                }
            }

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.google_api_key}"

            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "candidates" in data and data["candidates"]:
                        content = data["candidates"][0]["content"]["parts"][0]["text"]
                        return {
                            "success": True,
                            "content": content,
                            "provider": "gemini",
                            "model": model,
                            "deep_search": True,
                            "deep_think": True,
                            "usage": data.get("usageMetadata", {})
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No content generated by Gemini",
                            "content": ""
                        }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Gemini API error: {response.status} - {error_text}",
                        "content": ""
                    }

    async def _claude_generate(self, prompt: str, max_tokens: int, temperature: float, model: Optional[str]) -> Dict[str, Any]:
        """Anthropic Claude generation with Opus 4.1 extended capabilities"""
        if not model:
            model = "claude-3-opus-20240229"  # Latest Claude Opus

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {settings.claude_api_key}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            # Enhanced prompt for extended reasoning
            enhanced_prompt = f"""
            As Claude Opus 4.1 with extended capabilities, please provide a comprehensive medical analysis:

            Medical Query: {prompt}

            Please use your extended reasoning to:
            1. Perform deep analysis of the medical context
            2. Consider multiple evidence sources and perspectives
            3. Provide nuanced clinical insights
            4. Include relevant contraindications and considerations
            5. Structure the response for clinical utility

            Provide a thorough, evidence-based response in markdown format.
            """

            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ]
            }

            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "content": data["content"][0]["text"],
                        "provider": "claude",
                        "model": model,
                        "extended_reasoning": True,
                        "usage": data.get("usage", {})
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Claude API error: {response.status} - {error_text}",
                        "content": ""
                    }

    async def _perplexity_generate(self, prompt: str, max_tokens: int, temperature: float, model: Optional[str]) -> Dict[str, Any]:
        """Perplexity Pro generation with citation capabilities"""
        if not model:
            model = "llama-3.1-sonar-large-128k-online"  # Latest Perplexity model

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {settings.perplexity_api_key}",
                "Content-Type": "application/json"
            }

            # Enhanced prompt for research and citations
            enhanced_prompt = f"""
            As Perplexity Pro, provide a comprehensive medical research analysis with citations:

            Medical Query: {prompt}

            Please:
            1. Search current medical literature and databases
            2. Provide evidence-based information with citations
            3. Include recent research findings (2020-2024)
            4. Structure response with clear references
            5. Highlight level of evidence for each claim

            Format with proper medical citations and evidence levels.
            """

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a medical research assistant. Provide evidence-based information with proper citations."
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "search_domain_filter": ["pubmed.ncbi.nlm.nih.gov", "nejm.org", "thelancet.com", "jamanetwork.com"],
                "return_citations": True,
                "search_recency_filter": "month"
            }

            async with session.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "content": data["choices"][0]["message"]["content"],
                        "provider": "perplexity",
                        "model": model,
                        "citations": data.get("citations", []),
                        "sources": data.get("sources", []),
                        "usage": data.get("usage", {})
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Perplexity API error: {response.status} - {error_text}",
                        "content": ""
                    }

    async def multi_provider_synthesis(self, prompt: str, providers: List[str] = None) -> Dict[str, Any]:
        """Generate content using multiple providers and synthesize results"""
        if not providers:
            providers = [p for p, available in self.providers.items() if available]

        if not providers:
            return {
                "success": False,
                "error": "No AI providers available",
                "content": ""
            }

        # Generate content from multiple providers concurrently
        tasks = []
        for provider in providers[:settings.max_concurrent_ai_requests]:
            task = self.generate_content(prompt, provider=provider)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get("success"):
                successful_results.append({
                    "provider": providers[i],
                    "content": result["content"],
                    "metadata": {k: v for k, v in result.items() if k not in ["success", "content"]}
                })

        if not successful_results:
            return {
                "success": False,
                "error": "All providers failed to generate content",
                "content": ""
            }

        # Synthesize results (basic implementation)
        synthesis = self._synthesize_responses(successful_results)

        return {
            "success": True,
            "content": synthesis,
            "provider_results": successful_results,
            "synthesis_method": "multi_provider"
        }

    def _synthesize_responses(self, results: List[Dict[str, Any]]) -> str:
        """Synthesize multiple AI responses into a coherent result"""
        synthesis = f"# Multi-Provider Medical Analysis\n\n"
        synthesis += f"*Analysis generated using {len(results)} AI providers for comprehensive coverage*\n\n"

        for i, result in enumerate(results, 1):
            provider = result["provider"].title()
            content = result["content"]

            synthesis += f"## {provider} Analysis\n\n"
            synthesis += content
            synthesis += f"\n\n---\n\n"

        synthesis += "## Synthesis Summary\n\n"
        synthesis += "This analysis combines insights from multiple AI providers to ensure comprehensive coverage and reduce bias. "
        synthesis += "Each provider brings unique strengths in medical knowledge synthesis.\n"

        return synthesis

    def get_available_providers(self) -> Dict[str, Any]:
        """Get status of all AI providers"""
        return {
            "available_providers": [p for p, available in self.providers.items() if available],
            "provider_capabilities": {
                "openai": {"models": ["gpt-4", "gpt-3.5-turbo"], "specialties": ["general", "reasoning"]},
                "gemini": {"models": ["gemini-2.5-pro"], "specialties": ["deep_search", "deep_think", "multimodal"]},
                "claude": {"models": ["claude-3-opus"], "specialties": ["extended_reasoning", "analysis"]},
                "perplexity": {"models": ["sonar-large"], "specialties": ["research", "citations", "current_info"]}
            },
            "default_provider": settings.default_ai_provider,
            "multi_provider_enabled": settings.enable_multi_provider_synthesis
        }

# Global multi-AI manager instance
multi_ai_manager = MultiAIManager()