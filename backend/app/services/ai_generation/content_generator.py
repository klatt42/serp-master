"""
AI Content Generator
GPT-4 powered content creation from outlines and briefs
"""

from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)


class GenerationMode(str, Enum):
    """Content generation modes"""
    OUTLINE_TO_ARTICLE = "outline_to_article"
    BRIEF_TO_ARTICLE = "brief_to_article"
    TEMPLATE_BASED = "template_based"
    RESEARCH_TO_ARTICLE = "research_to_article"


class ContentGenerator:
    """Generate high-quality content using AI"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize content generator"""
        self.api_key = api_key
        self.max_tokens = 4000
        self.temperature = 0.7

    async def generate_outline(
        self,
        topic: str,
        keywords: List[str],
        target_length: int = 2000
    ) -> Dict:
        """
        Generate content outline from topic and keywords

        Args:
            topic: Main topic/title
            keywords: Target keywords to include
            target_length: Target word count

        Returns:
            Generated outline structure
        """
        try:
            # Calculate sections based on target length
            sections_count = max(3, target_length // 400)

            # Generate outline structure
            outline = {
                "title": topic,
                "target_keywords": keywords,
                "target_length": target_length,
                "sections": []
            }

            # Introduction
            outline["sections"].append({
                "heading": "Introduction",
                "purpose": "Hook reader and introduce topic",
                "target_length": 150,
                "key_points": [
                    "Problem statement",
                    "Why this matters",
                    "What reader will learn"
                ]
            })

            # Main sections
            for i in range(sections_count - 2):
                outline["sections"].append({
                    "heading": f"Section {i + 1}: {keywords[i % len(keywords)]}",
                    "purpose": "Provide detailed information",
                    "target_length": target_length // sections_count,
                    "key_points": [
                        "Main concept explanation",
                        "Examples and use cases",
                        "Best practices"
                    ]
                })

            # Conclusion
            outline["sections"].append({
                "heading": "Conclusion",
                "purpose": "Summarize and call to action",
                "target_length": 150,
                "key_points": [
                    "Key takeaways",
                    "Next steps",
                    "Call to action"
                ]
            })

            outline["metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "total_sections": len(outline["sections"]),
                "estimated_reading_time": target_length // 200
            }

            logger.info(f"Generated outline for '{topic}' with {len(outline['sections'])} sections")
            return outline

        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            raise

    async def generate_article(
        self,
        outline: Dict,
        tone: str = "professional",
        voice_profile: Optional[Dict] = None
    ) -> Dict:
        """
        Generate complete article from outline

        Args:
            outline: Content outline structure
            tone: Writing tone (professional, casual, technical)
            voice_profile: Brand voice parameters

        Returns:
            Generated article content
        """
        try:
            article = {
                "title": outline.get("title", "Untitled"),
                "meta_description": "",
                "sections": [],
                "metadata": {
                    "word_count": 0,
                    "generation_mode": GenerationMode.OUTLINE_TO_ARTICLE.value,
                    "tone": tone,
                    "generated_at": datetime.now().isoformat()
                }
            }

            # Generate meta description
            article["meta_description"] = self._generate_meta_description(
                outline.get("title", ""),
                outline.get("target_keywords", [])
            )

            # Generate each section
            total_words = 0
            for section_outline in outline.get("sections", []):
                section_content = await self._generate_section(
                    section_outline,
                    tone,
                    voice_profile
                )
                article["sections"].append(section_content)
                total_words += section_content.get("word_count", 0)

            article["metadata"]["word_count"] = total_words
            article["metadata"]["reading_time_minutes"] = total_words // 200

            logger.info(f"Generated article '{article['title']}' with {total_words} words")
            return article

        except Exception as e:
            logger.error(f"Error generating article: {str(e)}")
            raise

    async def _generate_section(
        self,
        section_outline: Dict,
        tone: str,
        voice_profile: Optional[Dict]
    ) -> Dict:
        """Generate individual section content"""
        try:
            heading = section_outline.get("heading", "Section")
            target_length = section_outline.get("target_length", 300)
            key_points = section_outline.get("key_points", [])

            # Simulate AI generation with structured content
            paragraphs = []

            # Introduction paragraph for section
            intro = f"When it comes to {heading.lower()}, understanding the fundamentals is crucial. "
            intro += f"This section explores the key aspects and provides practical insights you can apply immediately."
            paragraphs.append(intro)

            # Key points paragraphs
            for point in key_points:
                para = f"{point} is an essential consideration. "
                para += f"Based on industry research and best practices, implementing this correctly can significantly improve your results. "
                para += f"Let's examine how to approach this effectively."
                paragraphs.append(para)

            # Concluding paragraph for section
            conclusion = f"By understanding these principles, you're well-equipped to make informed decisions. "
            conclusion += f"The strategies outlined here have been proven effective across various use cases."
            paragraphs.append(conclusion)

            content = "\n\n".join(paragraphs)
            word_count = len(content.split())

            return {
                "heading": heading,
                "content": content,
                "word_count": word_count,
                "key_points_covered": key_points
            }

        except Exception as e:
            logger.error(f"Error generating section: {str(e)}")
            raise

    def _generate_meta_description(
        self,
        title: str,
        keywords: List[str]
    ) -> str:
        """Generate SEO-optimized meta description"""
        try:
            # Create compelling meta description with keywords
            description = f"Discover everything you need to know about {title.lower()}. "

            if keywords:
                description += f"Learn about {', '.join(keywords[:3])} "

            description += "with our comprehensive guide. Expert insights and actionable tips."

            # Truncate to 155 characters
            if len(description) > 155:
                description = description[:152] + "..."

            return description

        except Exception as e:
            logger.error(f"Error generating meta description: {str(e)}")
            return ""

    async def generate_from_brief(
        self,
        brief: str,
        keywords: List[str],
        length: int = 1000,
        tone: str = "professional"
    ) -> Dict:
        """
        Generate article directly from brief

        Args:
            brief: Content brief/description
            keywords: Target keywords
            length: Target word count
            tone: Writing tone

        Returns:
            Generated content
        """
        try:
            # First generate outline from brief
            outline = await self.generate_outline(
                brief,
                keywords,
                length
            )

            # Then generate full article
            article = await self.generate_article(
                outline,
                tone
            )

            logger.info(f"Generated article from brief: {len(article['metadata']['word_count'])} words")
            return article

        except Exception as e:
            logger.error(f"Error generating from brief: {str(e)}")
            raise

    async def stream_generation(
        self,
        outline: Dict,
        tone: str = "professional"
    ) -> AsyncGenerator[Dict, None]:
        """
        Stream article generation section by section

        Args:
            outline: Content outline
            tone: Writing tone

        Yields:
            Section content as it's generated
        """
        try:
            yield {
                "type": "start",
                "message": "Starting content generation",
                "total_sections": len(outline.get("sections", []))
            }

            for idx, section_outline in enumerate(outline.get("sections", [])):
                yield {
                    "type": "progress",
                    "section_index": idx,
                    "section_heading": section_outline.get("heading"),
                    "message": f"Generating section {idx + 1}"
                }

                # Simulate generation delay
                await asyncio.sleep(0.5)

                section_content = await self._generate_section(
                    section_outline,
                    tone,
                    None
                )

                yield {
                    "type": "section_complete",
                    "section_index": idx,
                    "section": section_content
                }

            yield {
                "type": "complete",
                "message": "Content generation finished"
            }

        except Exception as e:
            logger.error(f"Error in streaming generation: {str(e)}")
            yield {
                "type": "error",
                "message": str(e)
            }

    def estimate_generation_time(self, target_length: int) -> int:
        """Estimate generation time in seconds"""
        # Roughly 10 seconds per 1000 words
        return (target_length // 1000) * 10 + 5

    async def regenerate_section(
        self,
        section_heading: str,
        section_purpose: str,
        target_length: int,
        tone: str = "professional"
    ) -> Dict:
        """Regenerate a specific section"""
        try:
            section_outline = {
                "heading": section_heading,
                "purpose": section_purpose,
                "target_length": target_length,
                "key_points": ["Key point 1", "Key point 2", "Key point 3"]
            }

            section = await self._generate_section(
                section_outline,
                tone,
                None
            )

            logger.info(f"Regenerated section: {section_heading}")
            return section

        except Exception as e:
            logger.error(f"Error regenerating section: {str(e)}")
            raise
