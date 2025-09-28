"""Simplified AI service with real OpenAI integration"""

from typing import Optional, Dict, Any
import logging
import aiohttp
import json

from ..core.config import settings

logger = logging.getLogger(__name__)

class AIManager:
    """Simple AI manager with OpenAI integration"""

    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"

    async def generate_content(
        self,
        prompt: str,
        context_type: str = "medical",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate medical content using OpenAI"""

        if not self.openai_api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "content": ""
            }

        # Build medical prompt
        medical_prompt = self._build_medical_prompt(prompt, context_type)

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a medical expert assistant. Provide accurate, evidence-based medical information."
                        },
                        {
                            "role": "user",
                            "content": medical_prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }

                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:

                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]

                        return {
                            "success": True,
                            "content": content,
                            "model": "gpt-4",
                            "usage": data.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "content": ""
                        }

        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }

    def _build_medical_prompt(self, prompt: str, context_type: str) -> str:
        """Build a medical-focused prompt"""

        context_templates = {
            "medical": "Generate medical content that is accurate, evidence-based, and appropriately formatted:",
            "synthesis": "Synthesize medical information from multiple sources into coherent content:",
            "chapter": "Create a medical chapter section with proper structure and clinical details:",
            "analysis": "Analyze the medical content and provide expert insights:",
        }

        context = context_templates.get(context_type, context_templates["medical"])

        return f"""
{context}

{prompt}

Requirements:
- Use proper medical terminology
- Include evidence-based information where applicable
- Structure content clearly with appropriate sections
- Maintain clinical accuracy and relevance
- Format in markdown when appropriate

Content:
"""

# Global AI manager instance
ai_manager = AIManager()
