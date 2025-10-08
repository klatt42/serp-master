"""
Platform-Specific Content Template Generator
Create ready-to-use content frameworks for each platform
"""

from typing import List, Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ContentPlatform(str, Enum):
    """Supported content platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    BLOG = "blog"
    AMAZON = "amazon"
    REDDIT = "reddit"
    INSTAGRAM = "instagram"


class TemplateGenerator:
    """Generate platform-specific content templates"""

    def generate_content_template(
        self,
        platform: str,
        keyword: str,
        intent: str,
        content_type: Optional[str] = None
    ) -> Dict:
        """
        Generate customized content template for platform

        Returns complete content template with structure and suggestions
        """
        try:
            if platform == "youtube":
                template = self._get_youtube_template(keyword, intent)
            elif platform == "tiktok":
                template = self._get_tiktok_template(keyword, intent)
            elif platform == "blog":
                template = self._get_blog_template(keyword, intent)
            elif platform == "instagram":
                template = self._get_instagram_template(keyword, intent)
            elif platform == "reddit":
                template = self._get_reddit_template(keyword, intent)
            else:
                template = self._get_generic_template(platform, keyword, intent)

            # Add metadata
            template["metadata"] = {
                "keyword": keyword,
                "intent": intent,
                "platform": platform,
                "content_type": content_type or "standard",
                "estimated_creation_time": self._estimate_creation_time(platform)
            }

            return template

        except Exception as e:
            logger.error(f"Template generation error: {str(e)}")
            raise

    def _get_youtube_template(self, keyword: str, intent: str) -> Dict:
        """YouTube video template"""
        return {
            "platform": "youtube",
            "structure": {
                "intro": {
                    "duration": "0-15 seconds",
                    "purpose": "Hook viewer attention",
                    "elements": ["Problem statement", "Promise of solution"]
                },
                "main_content": {
                    "duration": "5-15 minutes",
                    "purpose": "Deliver value",
                    "elements": ["Main points (3-5)", "Examples", "Visual aids"]
                },
                "conclusion": {
                    "duration": "30-60 seconds",
                    "purpose": "Call to action",
                    "elements": ["Summary", "CTA (subscribe/like/comment)"]
                }
            },
            "title_suggestions": [
                f"How to {keyword} (Complete Guide)",
                f"{keyword}: Everything You Need to Know",
                f"The Ultimate {keyword} Tutorial",
                f"{keyword} Explained in 10 Minutes",
                f"Top 5 {keyword} Tips That Work"
            ],
            "script_outline": {
                "hook": f"Are you struggling with {keyword}? In this video, I'll show you...",
                "main_points": [
                    f"What is {keyword} and why it matters",
                    f"Step-by-step process for {keyword}",
                    f"Pro tips for mastering {keyword}",
                    f"Common mistakes to avoid",
                    f"Real results you can expect"
                ],
                "cta": f"If you found this {keyword} tutorial helpful, subscribe!"
            },
            "metadata_requirements": {
                "title": "60 characters max, keyword at start",
                "description": "First 150 chars most important, include timestamps",
                "tags": "10-15 relevant tags",
                "thumbnail": "1280x720px, faces + text"
            }
        }

    def _get_tiktok_template(self, keyword: str, intent: str) -> Dict:
        """TikTok short-form video template"""
        return {
            "platform": "tiktok",
            "structure": {
                "hook": {
                    "duration": "0-3 seconds",
                    "purpose": "Stop the scroll",
                    "elements": ["Visual surprise", "Bold statement"]
                },
                "content": {
                    "duration": "15-45 seconds",
                    "purpose": "Deliver quick value",
                    "elements": ["One clear point", "Visual demonstration"]
                },
                "cta": {
                    "duration": "2-5 seconds",
                    "purpose": "Engagement",
                    "elements": ["Follow", "Save", "Comment prompt"]
                }
            },
            "hook_variations": [
                f"POV: You just discovered the secret to {keyword}",
                f"Wait until you see this {keyword} hack",
                f"3 {keyword} mistakes you're probably making",
                f"This {keyword} tip changed everything",
                f"Nobody talks about this {keyword} trick"
            ],
            "content_beats": [
                {"second": 0, "action": "Visual hook", "text": "Bold text"},
                {"second": 3, "action": "Problem", "text": "Relatable scenario"},
                {"second": 10, "action": "Solution", "text": "Show method"},
                {"second": 20, "action": "Demo", "text": "Quick results"},
                {"second": 28, "action": "CTA", "text": "Follow for part 2"}
            ],
            "metadata_requirements": {
                "caption": "150 characters, hook in first line",
                "hashtags": "3-5 relevant + trending",
                "format": "Vertical 9:16, 1080x1920px"
            }
        }

    def _get_blog_template(self, keyword: str, intent: str) -> Dict:
        """Blog/article template"""
        return {
            "platform": "blog",
            "structure": {
                "headline": {
                    "purpose": "SEO + Click appeal",
                    "elements": ["Target keyword", "Benefit statement"]
                },
                "introduction": {
                    "length": "100-150 words",
                    "purpose": "Hook reader",
                    "elements": ["Problem", "Promise", "Preview"]
                },
                "body": {
                    "length": "1500-2500 words",
                    "purpose": "Comprehensive info",
                    "elements": ["H2 subheadings", "Short paragraphs", "Bullet points"]
                },
                "conclusion": {
                    "length": "100-200 words",
                    "purpose": "Summary + CTA",
                    "elements": ["Key takeaways", "Next steps"]
                }
            },
            "headline_formulas": [
                f"The Complete Guide to {keyword} [2025]",
                f"{keyword}: 7 Proven Strategies",
                f"How to Master {keyword} (Even as a Beginner)",
                f"{keyword} vs Alternatives: Which Is Best?",
                f"The Ultimate {keyword} Checklist"
            ],
            "content_outline": {
                "h1": f"The Complete Guide to {keyword}",
                "sections": [
                    {"h2": f"What is {keyword}?", "content": "Define clearly"},
                    {"h2": f"Why {keyword} Matters", "content": "Benefits + stats"},
                    {"h2": f"How to Get Started", "content": "Step-by-step"},
                    {"h2": f"Common Mistakes", "content": "Pitfalls + solutions"},
                    {"h2": f"Best Practices", "content": "Pro tips"},
                    {"h2": "Conclusion", "content": "Summary + action plan"}
                ]
            },
            "metadata_requirements": {
                "meta_title": "55-60 characters",
                "meta_description": "150-160 characters",
                "featured_image": "1200x630px"
            }
        }

    def _get_instagram_template(self, keyword: str, intent: str) -> Dict:
        """Instagram post template"""
        return {
            "platform": "instagram",
            "structure": {
                "image": "Square 1080x1080px or Story 1080x1920px",
                "caption": "First 125 chars visible, hook essential",
                "hashtags": "Mix of popular and niche (10-30 tags)"
            },
            "caption_formulas": [
                f"5 {keyword} tips you need to know 👇",
                f"The truth about {keyword} that nobody tells you...",
                f"How I mastered {keyword} in 30 days",
                f"Your {keyword} questions answered"
            ]
        }

    def _get_reddit_template(self, keyword: str, intent: str) -> Dict:
        """Reddit post template"""
        return {
            "platform": "reddit",
            "structure": {
                "title": "Authentic, value-first approach",
                "body": "Detailed, helpful response",
                "tone": "Conversational, not promotional"
            },
            "title_examples": [
                f"My experience with {keyword} - what worked",
                f"Asked to share my {keyword} journey",
                f"Common {keyword} questions answered",
                f"{keyword} resources that helped me"
            ]
        }

    def _get_generic_template(self, platform: str, keyword: str, intent: str) -> Dict:
        """Generic template fallback"""
        return {
            "platform": platform,
            "keyword": keyword,
            "intent": intent,
            "structure": "Customize based on platform best practices",
            "recommendation": "Research platform-specific guidelines"
        }

    def _estimate_creation_time(self, platform: str) -> str:
        """Estimate content creation time"""
        time_estimates = {
            "youtube": "4-8 hours (filming + editing)",
            "tiktok": "30-60 minutes (quick edit)",
            "blog": "3-5 hours (research + writing)",
            "instagram": "1-2 hours (design + caption)",
            "reddit": "30-45 minutes (authentic response)"
        }
        return time_estimates.get(platform, "2-4 hours")

    def batch_generate_templates(
        self,
        content_plan: List[Dict]
    ) -> List[Dict]:
        """Generate templates for entire content plan"""
        templates = []

        for item in content_plan:
            template = self.generate_content_template(
                platform=item["platform"],
                keyword=item["keyword"],
                intent=item.get("intent", "research")
            )
            templates.append(template)

        return templates
