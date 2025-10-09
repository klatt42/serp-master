"""
About Page Optimizer
Analyzes and optimizes About pages for entity recognition
"""

import logging
import re
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from collections import Counter

from app.models.entity_models import (
    AboutPageMetrics,
    AboutPageOptimizationRequest,
    AboutPageOptimizationResponse
)

logger = logging.getLogger(__name__)


class AboutPageOptimizer:
    """Optimize About pages for entity recognition and trust"""

    def __init__(self):
        """Initialize about page optimizer"""
        # Trust signal keywords
        self.trust_signals = {
            "experience": [
                "years of experience", "since", "founded", "established",
                "decades", "experienced", "veteran", "expertise"
            ],
            "credentials": [
                "certified", "licensed", "accredited", "qualified",
                "trained", "certified professional", "board certified"
            ],
            "team": [
                "team", "employees", "staff", "professionals",
                "specialists", "experts", "our people"
            ],
            "achievements": [
                "award", "recognition", "achievement", "milestone",
                "success", "accomplishment", "distinguished", "honored"
            ],
            "scale": [
                "clients served", "projects completed", "customers",
                "satisfied clients", "successful projects"
            ],
            "location": [
                "based in", "located in", "serving", "headquarters",
                "office in", "local", "community"
            ],
            "values": [
                "mission", "vision", "values", "commitment", "dedicated",
                "focused", "believe", "philosophy"
            ],
            "quality": [
                "quality", "excellence", "best", "top-rated", "leading",
                "premier", "superior", "exceptional"
            ]
        }

        # Required elements for a complete About page
        self.required_elements = [
            "business_story",
            "team_information",
            "credentials",
            "contact_information",
            "value_proposition"
        ]

    async def optimize_about_page(
        self,
        request: AboutPageOptimizationRequest,
        site_data: Optional[Dict] = None
    ) -> AboutPageOptimizationResponse:
        """
        Analyze and optimize About page

        Args:
            request: About page optimization request
            site_data: Optional pre-analyzed site data

        Returns:
            Response with optimization recommendations
        """
        try:
            # Get About page content
            about_content = await self._get_about_content(
                request.site_url,
                request.about_page_url,
                site_data
            )

            # Calculate metrics
            metrics = self._calculate_metrics(about_content, site_data)

            # Identify missing elements
            missing_elements = self._identify_missing_elements(
                about_content,
                metrics
            )

            # Generate content suggestions
            content_suggestions = self._generate_content_suggestions(
                about_content,
                missing_elements,
                metrics
            )

            # Identify schema opportunities
            schema_opportunities = self._identify_schema_opportunities(
                about_content,
                site_data
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                metrics,
                missing_elements,
                schema_opportunities
            )

            return AboutPageOptimizationResponse(
                current_metrics=metrics,
                missing_elements=missing_elements,
                content_suggestions=content_suggestions,
                schema_opportunities=schema_opportunities,
                recommendations=recommendations,
                analyzed_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error optimizing about page: {str(e)}")
            raise

    async def _get_about_content(
        self,
        site_url: str,
        about_page_url: Optional[str],
        site_data: Optional[Dict]
    ) -> str:
        """Get About page content"""
        if site_data and site_data.get("about_content"):
            return site_data["about_content"]

        # If no about content provided, return empty
        # In production, this would crawl the about page
        return ""

    def _calculate_metrics(
        self,
        content: str,
        site_data: Optional[Dict]
    ) -> AboutPageMetrics:
        """Calculate About page quality metrics"""
        # Word count
        words = content.split()
        word_count = len(words)

        # Entity mentions (business name repetition)
        entity_mentions = 0
        if site_data and site_data.get("business_name"):
            business_name = site_data["business_name"]
            entity_mentions = len(re.findall(
                r'\b' + re.escape(business_name) + r'\b',
                content,
                re.IGNORECASE
            ))

        # Trust signals count
        trust_signals_count = self._count_trust_signals(content)

        # Team members mentioned
        team_members_mentioned = self._count_team_members(content)

        # Achievements mentioned
        achievements_mentioned = self._count_achievements(content)

        # Contact info complete
        contact_info_complete = self._check_contact_info(content, site_data)

        # Visual content count (would be from HTML analysis)
        visual_content_count = site_data.get("about_images_count", 0) if site_data else 0

        # Calculate overall quality score
        overall_quality_score = self._calculate_quality_score(
            word_count,
            entity_mentions,
            trust_signals_count,
            team_members_mentioned,
            achievements_mentioned,
            contact_info_complete,
            visual_content_count
        )

        return AboutPageMetrics(
            word_count=word_count,
            entity_mentions=entity_mentions,
            trust_signals_count=trust_signals_count,
            team_members_mentioned=team_members_mentioned,
            achievements_mentioned=achievements_mentioned,
            contact_info_complete=contact_info_complete,
            visual_content_count=visual_content_count,
            overall_quality_score=overall_quality_score
        )

    def _count_trust_signals(self, content: str) -> int:
        """Count trust signals in content"""
        content_lower = content.lower()
        count = 0

        for category, signals in self.trust_signals.items():
            for signal in signals:
                if signal in content_lower:
                    count += 1

        return count

    def _count_team_members(self, content: str) -> int:
        """Count team member mentions"""
        # Look for common patterns
        patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+,\s+(?:CEO|CTO|CFO|Founder|Director|Manager)',
            r'(?:CEO|CTO|CFO|Founder|Director|Manager):\s+[A-Z][a-z]+\s+[A-Z][a-z]+',
            r'\b(?:our|the)\s+(?:CEO|founder|director|manager|president)',
        ]

        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content)
            count += len(matches)

        return min(count, 20)  # Cap at reasonable number

    def _count_achievements(self, content: str) -> int:
        """Count achievement mentions"""
        achievement_patterns = [
            r'\b(?:won|received|earned|awarded)\s+(?:the\s+)?[A-Z][a-zA-Z\s]+(?:Award|Prize|Recognition)',
            r'\b[A-Z][a-zA-Z\s]+(?:Award|Prize)\b',
            r'\b(?:top|best|leading|premier)\s+\w+\b',
        ]

        count = 0
        for pattern in achievement_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            count += len(matches)

        return min(count, 15)  # Cap at reasonable number

    def _check_contact_info(
        self,
        content: str,
        site_data: Optional[Dict]
    ) -> bool:
        """Check if contact information is complete"""
        has_phone = bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content))
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content))
        has_address = bool(re.search(r'\b\d+\s+\w+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b', content, re.IGNORECASE))

        # Also check site_data
        if site_data:
            has_phone = has_phone or bool(site_data.get("phone"))
            has_email = has_email or bool(site_data.get("email"))
            has_address = has_address or bool(site_data.get("address"))

        # Need at least 2 of 3
        return sum([has_phone, has_email, has_address]) >= 2

    def _calculate_quality_score(
        self,
        word_count: int,
        entity_mentions: int,
        trust_signals: int,
        team_members: int,
        achievements: int,
        contact_complete: bool,
        visual_content: int
    ) -> int:
        """Calculate overall quality score (0-100)"""
        score = 0

        # Word count score (0-25 points)
        if word_count >= 800:
            score += 25
        elif word_count >= 500:
            score += 20
        elif word_count >= 300:
            score += 15
        elif word_count >= 150:
            score += 10
        else:
            score += 5

        # Entity mentions score (0-15 points)
        if entity_mentions >= 5:
            score += 15
        elif entity_mentions >= 3:
            score += 12
        elif entity_mentions >= 1:
            score += 8
        else:
            score += 0

        # Trust signals score (0-20 points)
        if trust_signals >= 10:
            score += 20
        elif trust_signals >= 6:
            score += 15
        elif trust_signals >= 3:
            score += 10
        else:
            score += 5

        # Team members score (0-15 points)
        if team_members >= 5:
            score += 15
        elif team_members >= 3:
            score += 12
        elif team_members >= 1:
            score += 8
        else:
            score += 0

        # Achievements score (0-10 points)
        if achievements >= 5:
            score += 10
        elif achievements >= 3:
            score += 7
        elif achievements >= 1:
            score += 4
        else:
            score += 0

        # Contact info score (0-10 points)
        if contact_complete:
            score += 10

        # Visual content score (0-5 points)
        if visual_content >= 5:
            score += 5
        elif visual_content >= 3:
            score += 4
        elif visual_content >= 1:
            score += 2

        return min(100, score)

    def _identify_missing_elements(
        self,
        content: str,
        metrics: AboutPageMetrics
    ) -> List[str]:
        """Identify missing content elements"""
        missing = []

        # Check for origin story
        if not re.search(r'\b(?:founded|started|began|established|origin|history)\b', content, re.IGNORECASE):
            missing.append("Origin story or company history")

        # Check for mission/vision
        if not re.search(r'\b(?:mission|vision|purpose|why we|believe)\b', content, re.IGNORECASE):
            missing.append("Mission, vision, or purpose statement")

        # Check for team information
        if metrics.team_members_mentioned == 0:
            missing.append("Team member profiles or bios")

        # Check for credentials
        if not re.search(r'\b(?:certified|licensed|qualified|credentials|education)\b', content, re.IGNORECASE):
            missing.append("Professional credentials or certifications")

        # Check for contact info
        if not metrics.contact_info_complete:
            missing.append("Complete contact information (phone, email, address)")

        # Check for achievements
        if metrics.achievements_mentioned == 0:
            missing.append("Awards, achievements, or notable milestones")

        # Check for experience indicators
        if not re.search(r'\b(?:years|since|experience|established)\b', content, re.IGNORECASE):
            missing.append("Years of experience or founding date")

        # Check for value proposition
        if not re.search(r'\b(?:unique|different|why choose|our approach|what sets us)\b', content, re.IGNORECASE):
            missing.append("Unique value proposition or differentiators")

        # Check for service area
        if not re.search(r'\b(?:serving|based in|located|area|region|local)\b', content, re.IGNORECASE):
            missing.append("Service area or geographic location")

        # Check for visual content
        if metrics.visual_content_count == 0:
            missing.append("Team photos, office images, or visual content")

        return missing

    def _generate_content_suggestions(
        self,
        content: str,
        missing_elements: List[str],
        metrics: AboutPageMetrics
    ) -> List[Dict[str, str]]:
        """Generate specific content suggestions"""
        suggestions = []

        # Suggest sections for missing elements
        for element in missing_elements:
            if "origin story" in element.lower():
                suggestions.append({
                    "section": "Company History",
                    "content": "Add a section describing how and why your business was founded. Include the year, founder names, and the problem you set out to solve.",
                    "priority": "high",
                    "estimated_length": "150-250 words"
                })

            elif "mission" in element.lower():
                suggestions.append({
                    "section": "Mission & Values",
                    "content": "Define your company's mission, core values, and what drives your work. Make it authentic and specific to your business.",
                    "priority": "high",
                    "estimated_length": "100-200 words"
                })

            elif "team" in element.lower():
                suggestions.append({
                    "section": "Our Team",
                    "content": "Include profiles of key team members with names, titles, credentials, and brief bios. Add professional photos.",
                    "priority": "high",
                    "estimated_length": "50-100 words per person"
                })

            elif "credentials" in element.lower():
                suggestions.append({
                    "section": "Credentials & Certifications",
                    "content": "List professional licenses, certifications, industry accreditations, and qualifications that establish your expertise.",
                    "priority": "high",
                    "estimated_length": "100-150 words"
                })

            elif "contact" in element.lower():
                suggestions.append({
                    "section": "Contact Information",
                    "content": "Ensure your About page includes phone number, email address, and physical address (if applicable). Consider adding a contact form.",
                    "priority": "high",
                    "estimated_length": "N/A"
                })

            elif "achievements" in element.lower():
                suggestions.append({
                    "section": "Awards & Recognition",
                    "content": "Highlight awards, industry recognition, notable clients, or significant milestones that demonstrate your credibility.",
                    "priority": "medium",
                    "estimated_length": "100-200 words"
                })

            elif "experience" in element.lower():
                suggestions.append({
                    "section": "Experience",
                    "content": "Specify how long you've been in business, years of combined team experience, or number of projects completed.",
                    "priority": "medium",
                    "estimated_length": "50-100 words"
                })

            elif "value proposition" in element.lower():
                suggestions.append({
                    "section": "What Sets Us Apart",
                    "content": "Clearly articulate what makes your business different from competitors. Focus on unique approaches, specializations, or guarantees.",
                    "priority": "high",
                    "estimated_length": "150-250 words"
                })

            elif "service area" in element.lower():
                suggestions.append({
                    "section": "Service Area",
                    "content": "Clearly state your geographic service area, whether local, regional, or national. Important for local SEO.",
                    "priority": "medium",
                    "estimated_length": "50-100 words"
                })

            elif "visual content" in element.lower():
                suggestions.append({
                    "section": "Visual Elements",
                    "content": "Add professional photos of your team, office/workspace, completed projects, or work in progress. Builds trust and engagement.",
                    "priority": "medium",
                    "estimated_length": "N/A"
                })

        # Length suggestions
        if metrics.word_count < 500:
            suggestions.append({
                "section": "Content Expansion",
                "content": f"Your About page is only {metrics.word_count} words. Aim for 500-1000 words to provide comprehensive information and improve SEO.",
                "priority": "high",
                "estimated_length": f"{500 - metrics.word_count}+ more words needed"
            })

        # Entity mention suggestions
        if metrics.entity_mentions < 3:
            suggestions.append({
                "section": "Entity Mentions",
                "content": "Mention your business name naturally throughout the page (aim for 3-5 times) to strengthen entity recognition.",
                "priority": "medium",
                "estimated_length": "N/A"
            })

        return suggestions

    def _identify_schema_opportunities(
        self,
        content: str,
        site_data: Optional[Dict]
    ) -> List[str]:
        """Identify schema markup opportunities"""
        opportunities = []

        # Organization schema
        opportunities.append(
            "Add Organization schema with founding date, founder, number of employees"
        )

        # Check for team members
        if re.search(r'\b(?:CEO|founder|director|team)\b', content, re.IGNORECASE):
            opportunities.append(
                "Add Person schema for key team members with name, role, credentials"
            )

        # Check for timeline/milestones
        if re.search(r'\b(?:founded|since|established|\d{4})\b', content):
            opportunities.append(
                "Consider adding Event schema for company milestones"
            )

        # Check for awards
        if re.search(r'\b(?:award|recognition|achievement)\b', content, re.IGNORECASE):
            opportunities.append(
                "Mark up awards and achievements with schema for enhanced visibility"
            )

        # FAQ schema if Q&A present
        if re.search(r'\b(?:question|answer|faq|why|how|what)\b', content, re.IGNORECASE):
            opportunities.append(
                "Add FAQ schema if you have Q&A content on your About page"
            )

        return opportunities

    def _generate_recommendations(
        self,
        metrics: AboutPageMetrics,
        missing_elements: List[str],
        schema_opportunities: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Overall assessment
        if metrics.overall_quality_score >= 80:
            recommendations.append({
                "priority": "low",
                "category": "overall",
                "title": "Excellent About Page",
                "description": f"Your About page scores {metrics.overall_quality_score}/100. Focus on minor enhancements and schema markup.",
                "action_items": []
            })
        elif metrics.overall_quality_score >= 60:
            recommendations.append({
                "priority": "medium",
                "category": "overall",
                "title": "Good About Page with Room for Improvement",
                "description": f"Your About page scores {metrics.overall_quality_score}/100. Address the missing elements below to strengthen entity recognition.",
                "action_items": []
            })
        else:
            recommendations.append({
                "priority": "high",
                "category": "overall",
                "title": "About Page Needs Significant Improvement",
                "description": f"Your About page scores {metrics.overall_quality_score}/100. This is a critical page for entity SEO - prioritize improvements.",
                "action_items": []
            })

        # Content length recommendations
        if metrics.word_count < 500:
            recommendations.append({
                "priority": "high",
                "category": "content",
                "title": "Expand Content Length",
                "description": f"At {metrics.word_count} words, your About page is too short. Aim for 500-1000 words.",
                "action_items": [
                    "Add detailed company history",
                    "Include team member bios",
                    "Expand on your unique value proposition",
                    "Add more about your credentials and experience"
                ]
            })

        # Trust signals
        if metrics.trust_signals_count < 5:
            recommendations.append({
                "priority": "high",
                "category": "trust",
                "title": "Add More Trust Signals",
                "description": f"Only {metrics.trust_signals_count} trust signals detected. Add credentials, experience indicators, and quality statements.",
                "action_items": [
                    "Mention years in business",
                    "List certifications and licenses",
                    "Include client testimonials or case studies",
                    "Add team credentials and qualifications"
                ]
            })

        # Missing elements
        if missing_elements:
            recommendations.append({
                "priority": "high",
                "category": "content",
                "title": "Add Missing Key Elements",
                "description": f"{len(missing_elements)} critical elements are missing from your About page.",
                "action_items": missing_elements[:7]  # Top 7
            })

        # Schema opportunities
        if schema_opportunities:
            recommendations.append({
                "priority": "medium",
                "category": "schema",
                "title": "Implement Schema Markup",
                "description": "Add structured data to help Google understand your entity better.",
                "action_items": schema_opportunities
            })

        # Team information
        if metrics.team_members_mentioned == 0:
            recommendations.append({
                "priority": "high",
                "category": "team",
                "title": "Add Team Information",
                "description": "Team member profiles with credentials strengthen entity recognition and build trust.",
                "action_items": [
                    "Create profiles for founders and key team members",
                    "Include names, titles, and credentials",
                    "Add professional photos",
                    "Mention relevant experience and expertise"
                ]
            })

        # Contact information
        if not metrics.contact_info_complete:
            recommendations.append({
                "priority": "high",
                "category": "contact",
                "title": "Complete Contact Information",
                "description": "Complete NAP (Name, Address, Phone) is critical for entity recognition.",
                "action_items": [
                    "Add phone number",
                    "Add email address",
                    "Add physical address (if applicable)",
                    "Ensure consistency with other pages"
                ]
            })

        # Visual content
        if metrics.visual_content_count < 3:
            recommendations.append({
                "priority": "medium",
                "category": "visual",
                "title": "Add Visual Content",
                "description": "Photos humanize your business and increase engagement.",
                "action_items": [
                    "Add team photos",
                    "Include office/workspace images",
                    "Show your work or products",
                    "Add founder/leadership photos"
                ]
            })

        return recommendations
