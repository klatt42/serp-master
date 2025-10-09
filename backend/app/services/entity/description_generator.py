"""
Business Description Generator
AI-powered business description optimization using GPT-4
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re
from openai import AsyncOpenAI

from app.models.entity_models import (
    BusinessDescriptionVariation,
    BusinessDescriptionRequest,
    BusinessDescriptionResponse
)

logger = logging.getLogger(__name__)


class BusinessDescriptionGenerator:
    """Generate entity-optimized business descriptions"""

    def __init__(self):
        """Initialize description generator"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set - GPT-4 features will use fallback")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)

        self.max_description_length = 200
        self.min_description_length = 150

    async def generate_descriptions(
        self,
        request: BusinessDescriptionRequest
    ) -> BusinessDescriptionResponse:
        """
        Generate optimized business descriptions

        Args:
            request: Business description generation request

        Returns:
            Response with multiple description variations
        """
        try:
            # Step 1: Analyze existing content
            analysis = await self._analyze_existing_content(request)

            # Step 2: Identify business type
            business_type = await self._identify_business_type(analysis, request)

            # Step 3: Extract location info
            location_info = await self._extract_location_info(analysis, request)

            # Step 4: Generate optimized descriptions
            variations = await self._generate_variations(
                analysis,
                business_type,
                location_info,
                request
            )

            # Step 5: Score each variation
            scored_variations = []
            for desc in variations:
                scored_var = await self._score_description(
                    desc,
                    request.target_keywords or [],
                    location_info
                )
                scored_variations.append(scored_var)

            # Sort by overall score
            scored_variations.sort(key=lambda x: x.overall_score, reverse=True)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                scored_variations,
                analysis,
                business_type
            )

            return BusinessDescriptionResponse(
                variations=scored_variations,
                analysis={
                    "business_type": business_type,
                    "location": location_info,
                    "existing_description": request.existing_description,
                    "detected_services": analysis.get("services", []),
                    "detected_keywords": analysis.get("keywords", [])
                },
                recommendations=recommendations,
                generated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error generating descriptions: {str(e)}")
            raise

    async def _analyze_existing_content(
        self,
        request: BusinessDescriptionRequest
    ) -> Dict:
        """Analyze existing website content"""
        analysis = {
            "business_name": request.business_name or "Unknown Business",
            "industry": request.industry,
            "services": [],
            "keywords": request.target_keywords or [],
            "location": request.location,
            "value_props": []
        }

        # Extract from existing description if provided
        if request.existing_description:
            # Extract potential services
            services = self._extract_services(request.existing_description)
            analysis["services"] = services

            # Extract keywords
            if not analysis["keywords"]:
                analysis["keywords"] = self._extract_keywords(request.existing_description)

        return analysis

    def _extract_services(self, text: str) -> List[str]:
        """Extract service mentions from text"""
        services = []

        # Common service indicators
        service_patterns = [
            r'((?:professional|expert|certified)\s+\w+\s+(?:services?|solutions?))',
            r'((?:residential|commercial)\s+\w+)',
            r'(\w+\s+(?:repair|maintenance|installation|restoration|cleaning))',
        ]

        for pattern in service_patterns:
            matches = re.findall(pattern, text.lower())
            services.extend(matches)

        return list(set(services))[:5]  # Top 5 unique services

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during'
        }

        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]

        # Count frequency
        from collections import Counter
        word_counts = Counter(keywords)

        # Return top 10 most common
        return [word for word, _ in word_counts.most_common(10)]

    async def _identify_business_type(
        self,
        analysis: Dict,
        request: BusinessDescriptionRequest
    ) -> str:
        """Identify business type from analysis"""
        if request.industry:
            return request.industry

        # Try to infer from services
        services = analysis.get("services", [])
        if services:
            # Check for common business types
            if any('resto' in s or 'water' in s or 'damage' in s for s in services):
                return "restoration services"
            elif any('plumb' in s for s in services):
                return "plumbing services"
            elif any('electric' in s for s in services):
                return "electrical services"
            elif any('clean' in s for s in services):
                return "cleaning services"

        return "professional services"

    async def _extract_location_info(
        self,
        analysis: Dict,
        request: BusinessDescriptionRequest
    ) -> Optional[str]:
        """Extract location information"""
        if request.location:
            return request.location

        # Try to extract from existing description
        if request.existing_description:
            # Look for city, state patterns
            location_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s+([A-Z]{2})\b'
            match = re.search(location_pattern, request.existing_description)
            if match:
                return f"{match.group(1)}, {match.group(2)}"

        return analysis.get("location")

    async def _generate_variations(
        self,
        analysis: Dict,
        business_type: str,
        location: Optional[str],
        request: BusinessDescriptionRequest
    ) -> List[str]:
        """Generate multiple description variations"""
        variations = []

        # If OpenAI client available, use GPT-4
        if self.client:
            try:
                variations = await self._generate_with_gpt4(
                    analysis,
                    business_type,
                    location,
                    request
                )
            except Exception as e:
                logger.warning(f"GPT-4 generation failed: {str(e)}, using templates")
                variations = self._generate_with_templates(
                    analysis,
                    business_type,
                    location,
                    request
                )
        else:
            # Use template-based generation
            variations = self._generate_with_templates(
                analysis,
                business_type,
                location,
                request
            )

        return variations[:5]  # Top 5 variations

    async def _generate_with_gpt4(
        self,
        analysis: Dict,
        business_type: str,
        location: Optional[str],
        request: BusinessDescriptionRequest
    ) -> List[str]:
        """Generate descriptions using GPT-4"""
        business_name = analysis["business_name"]
        services = analysis.get("services", [])
        keywords = analysis.get("keywords", [])

        prompt = f"""Generate 5 SEO-optimized business descriptions for entity recognition.

Business Information:
- Name: {business_name}
- Type: {business_type}
- Location: {location or 'Not specified'}
- Services: {', '.join(services) if services else 'General services'}
- Keywords: {', '.join(keywords[:5]) if keywords else 'None'}

Requirements:
1. Each description should be 150-200 characters
2. Include business name and type clearly
3. Mention location if provided (important for local SEO)
4. Include 1-2 primary services/keywords
5. Add unique value proposition or authority signal
6. Optimize for Google entity recognition
7. Make it compelling and clear

Generate 5 different variations, each on a new line, no numbering."""

        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert SEO copywriter specializing in entity optimization and local search."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=800
        )

        content = response.choices[0].message.content
        variations = [line.strip() for line in content.split('\n') if line.strip()]

        # Filter to valid lengths
        valid_variations = [
            v for v in variations
            if self.min_description_length <= len(v) <= self.max_description_length
        ]

        return valid_variations if valid_variations else variations[:5]

    def _generate_with_templates(
        self,
        analysis: Dict,
        business_type: str,
        location: Optional[str],
        request: BusinessDescriptionRequest
    ) -> List[str]:
        """Generate descriptions using templates (fallback)"""
        business_name = analysis["business_name"]
        services = analysis.get("services", [])[:2]  # Top 2 services
        keywords = analysis.get("keywords", [])[:2]  # Top 2 keywords

        variations = []

        # Template 1: Standard entity description
        if location:
            desc1 = f"{business_name} - Professional {business_type} in {location}. " \
                   f"Expert {', '.join(services[:2]) if services else business_type}. " \
                   f"Licensed, insured, and trusted locally."
        else:
            desc1 = f"{business_name} - Leading {business_type} provider. " \
                   f"Specializing in {', '.join(services[:2]) if services else 'quality solutions'}. " \
                   f"Professional, certified, and experienced."
        variations.append(desc1)

        # Template 2: Service-focused
        if services:
            desc2 = f"{business_name} offers professional {services[0]} services" \
                   f"{f' in {location}' if location else ''}. " \
                   f"Certified {business_type} with proven expertise. " \
                   f"Fast response and quality results guaranteed."
        else:
            desc2 = f"{business_name} provides expert {business_type}" \
                   f"{f' in {location}' if location else ''}. " \
                   f"Professional solutions with guaranteed satisfaction. " \
                   f"Licensed and insured."
        variations.append(desc2)

        # Template 3: Authority-focused
        desc3 = f"Trusted {business_type}: {business_name}" \
               f"{f' serving {location}' if location else ''}. " \
               f"Years of experience, certified professionals, " \
               f"{'specializing in ' + services[0] if services else 'comprehensive solutions'}."
        variations.append(desc3)

        # Template 4: Value proposition
        if location:
            desc4 = f"{location}'s premier {business_type} - {business_name}. " \
                   f"Expert team specializing in {services[0] if services else 'professional services'}. " \
                   f"Licensed, certified, and locally trusted."
        else:
            desc4 = f"Professional {business_type} - {business_name}. " \
                   f"Industry-leading expertise in {services[0] if services else 'comprehensive solutions'}. " \
                   f"Certified professionals, guaranteed results."
        variations.append(desc4)

        # Template 5: Keyword-rich
        keywords_str = ', '.join(keywords[:3]) if keywords else business_type
        desc5 = f"{business_name}: {keywords_str}" \
               f"{f' in {location}' if location else ''}. " \
               f"Professional {business_type} with certified expertise. " \
               f"Quality service and customer satisfaction guaranteed."
        variations.append(desc5)

        return variations

    async def _score_description(
        self,
        description: str,
        keywords: List[str],
        location: Optional[str]
    ) -> BusinessDescriptionVariation:
        """Score a description variation"""
        char_count = len(description)

        # SEO score (keyword presence, length, structure)
        seo_score = 0
        keywords_included = []

        for keyword in keywords:
            if keyword.lower() in description.lower():
                seo_score += 15
                keywords_included.append(keyword)

        # Length score
        if self.min_description_length <= char_count <= self.max_description_length:
            seo_score += 25
        elif char_count < self.min_description_length:
            seo_score += 10
        else:
            seo_score += 15

        # Has proper structure (business name + description)
        if any(char.isupper() for char in description[:30]):  # Business name likely capitalized
            seo_score += 10

        seo_score = min(100, seo_score)

        # Local relevance score
        local_score = 0
        location_mentioned = False

        if location:
            if location.lower() in description.lower():
                local_score = 100
                location_mentioned = True
            else:
                local_score = 30  # Penalize missing location
        else:
            local_score = 50  # Neutral if no location provided

        # Entity clarity score
        entity_score = 50  # Base score

        # Has business type/industry mention
        business_types = ['services', 'company', 'business', 'provider', 'professional', 'expert']
        if any(bt in description.lower() for bt in business_types):
            entity_score += 20

        # Has clear value proposition
        value_words = ['trusted', 'certified', 'licensed', 'expert', 'professional', 'quality', 'leading']
        value_count = sum(1 for vw in value_words if vw in description.lower())
        entity_score += min(30, value_count * 10)

        entity_score = min(100, entity_score)

        # Readability score
        readability = 50  # Base

        # Sentence count
        sentences = description.count('.') + description.count('!') + description.count('?')
        if 2 <= sentences <= 4:
            readability += 25
        elif sentences == 1:
            readability += 15

        # Average word length
        words = description.split()
        avg_word_len = sum(len(w) for w in words) / len(words) if words else 0
        if 4 <= avg_word_len <= 7:
            readability += 25

        readability = min(100, readability)

        # Overall score (weighted average)
        overall = int(
            seo_score * 0.35 +
            local_score * 0.25 +
            entity_score * 0.25 +
            readability * 0.15
        )

        return BusinessDescriptionVariation(
            description=description,
            character_count=char_count,
            seo_score=seo_score,
            local_relevance_score=local_score,
            entity_clarity_score=entity_score,
            readability_score=readability,
            overall_score=overall,
            keywords_included=keywords_included,
            location_mentioned=location_mentioned
        )

    def _generate_recommendations(
        self,
        variations: List[BusinessDescriptionVariation],
        analysis: Dict,
        business_type: str
    ) -> List[str]:
        """Generate recommendations for description optimization"""
        recommendations = []

        if not variations:
            return ["Generate business descriptions using the tool above"]

        best = variations[0]

        # Check for improvements
        if best.seo_score < 70:
            recommendations.append(
                "Include more target keywords naturally in the description"
            )

        if best.local_relevance_score < 70:
            recommendations.append(
                "Add your city/location to improve local search visibility"
            )

        if best.entity_clarity_score < 70:
            recommendations.append(
                "Include your business type and key services more clearly"
            )

        if best.readability_score < 60:
            recommendations.append(
                "Simplify language for better readability"
            )

        if best.character_count > 200:
            recommendations.append(
                "Shorten description to 150-200 characters for better display in search results"
            )

        # Add positive recommendations
        if best.overall_score >= 80:
            recommendations.append(
                "Excellent! Use this description for your meta description and Google Business Profile"
            )
        elif best.overall_score >= 70:
            recommendations.append(
                "Good description. Consider minor tweaks for keyword optimization"
            )

        return recommendations if recommendations else [
            "Great descriptions! Select the one that best represents your business"
        ]
