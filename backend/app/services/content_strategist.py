"""
AI-powered content strategy generator
Uses OpenAI GPT-4 to create actionable content plans
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import os
import logging
from openai import OpenAI

from app.models.keyword import KeywordData
from app.models.cluster import KeywordCluster
from app.models.content_strategy import (
    ContentStrategy,
    ContentPillar,
    ContentItem,
    ContentType,
    Priority,
    Difficulty,
    ContentStatus
)

logger = logging.getLogger(__name__)


class ContentStrategist:
    """Generate comprehensive content strategies from keyword data"""

    def __init__(self, openai_api_key: str = None):
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=api_key)

    async def generate_strategy(
        self,
        seed_keyword: str,
        clusters: List[KeywordCluster],
        opportunities: List[Dict[str, Any]],
        niche_analysis: Dict[str, Any],
        options: Dict[str, Any] = None
    ) -> ContentStrategy:
        """
        Generate complete content strategy

        Args:
            seed_keyword: Main topic/niche
            clusters: Keyword clusters from analysis
            opportunities: Top keyword opportunities
            niche_analysis: Market analysis data
            options: Strategy preferences (timeline, content types, etc.)

        Returns:
            ContentStrategy with pillars, topics, and calendar
        """
        logger.info(f"Generating content strategy for '{seed_keyword}'")

        # Default options
        if options is None:
            options = {}

        # Build AI prompt
        prompt = self._build_strategy_prompt(
            seed_keyword=seed_keyword,
            clusters=clusters,
            opportunities=opportunities[:20],  # Top 20 only
            content_gaps=niche_analysis.get('content_gaps', []),
            market_size=niche_analysis.get('market_size', 'medium'),
            competition=niche_analysis.get('competition_level', 'medium'),
            options=options
        )

        # Generate strategy with GPT-4
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert SEO content strategist.
                        Generate comprehensive, actionable content strategies based on keyword research data.
                        Focus on practical implementation, content pillar architecture, and realistic timelines.
                        Always return valid JSON."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=3000
            )

            strategy_data = json.loads(response.choices[0].message.content)
            logger.info("AI strategy generated successfully")

        except Exception as e:
            logger.error(f"Error generating strategy with OpenAI: {e}")
            # Fallback to template strategy
            strategy_data = self._generate_fallback_strategy(seed_keyword, clusters, opportunities)

        # Transform to ContentStrategy model
        strategy = self._parse_strategy_response(
            strategy_data=strategy_data,
            seed_keyword=seed_keyword,
            clusters=clusters,
            opportunities=opportunities
        )

        logger.info(f"Strategy created with {len(strategy.pillars)} pillars and {len(strategy.content_items)} items")
        return strategy

    def _build_strategy_prompt(
        self,
        seed_keyword: str,
        clusters: List[KeywordCluster],
        opportunities: List[Dict[str, Any]],
        content_gaps: List[Dict],
        market_size: str,
        competition: str,
        options: Dict[str, Any]
    ) -> str:
        """Build detailed prompt for GPT-4"""

        # Format clusters
        cluster_summary = "\n".join([
            f"- {c.cluster_name} ({c.total_keywords} keywords, {c.total_search_volume:,} total volume)"
            for c in clusters[:10]  # Top 10 clusters
        ])

        # Format top opportunities
        opportunity_summary = "\n".join([
            f"- {o.get('keyword', '')} (Vol: {o.get('search_volume', 0):,}, Diff: {o.get('keyword_difficulty', 0)}, Score: {o.get('opportunity_score', 0):.1f})"
            for o in opportunities[:15]
        ])

        # Format content gaps
        gaps_summary = "\n".join([
            f"- {gap.get('gap_type', '')}: {gap.get('description', '')}"
            for gap in content_gaps[:5]
        ])

        timeline = options.get('timeline_weeks', 12)
        content_types = options.get('content_types', ['blog_post', 'guide', 'video'])

        prompt = f"""
Generate a comprehensive content strategy for: "{seed_keyword}"

NICHE ANALYSIS:
- Market Size: {market_size}
- Competition Level: {competition}
- Target Timeline: {timeline} weeks

KEYWORD CLUSTERS:
{cluster_summary}

TOP KEYWORD OPPORTUNITIES:
{opportunity_summary}

CONTENT GAPS IDENTIFIED:
{gaps_summary}

REQUIREMENTS:
1. Create 3-5 content pillars based on keyword clusters
2. For each pillar, generate 8-12 specific content topics
3. Assign priority (high/medium/low) to each topic
4. Suggest content type (blog_post, guide, video, infographic, etc.)
5. Estimate difficulty and timeframe for each piece
6. Create a realistic {timeline}-week editorial calendar
7. Include quick wins (easy topics to start with)
8. Provide SEO optimization tips for each pillar

CONTENT TYPES AVAILABLE: {', '.join(content_types)}

Return response as JSON with this structure:
{{
  "pillars": [
    {{
      "name": "Pillar name",
      "description": "What this pillar covers",
      "keywords": ["keyword1", "keyword2"],
      "priority": "high",
      "total_opportunity": 50000
    }}
  ],
  "content_items": [
    {{
      "title": "Content title",
      "pillar": "Pillar name",
      "content_type": "blog_post",
      "target_keyword": "main keyword",
      "supporting_keywords": ["keyword1", "keyword2"],
      "priority": "high",
      "estimated_difficulty": "medium",
      "estimated_hours": 8,
      "week_number": 1,
      "optimization_tips": ["tip1", "tip2"]
    }}
  ],
  "quick_wins": ["Quick win topic 1", "Quick win topic 2"],
  "implementation_notes": "Key recommendations for execution",
  "success_metrics": ["Metric 1", "Metric 2"]
}}
"""
        return prompt

    def _generate_fallback_strategy(
        self,
        seed_keyword: str,
        clusters: List[KeywordCluster],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate basic strategy when AI fails"""
        logger.info("Using fallback strategy generation")

        pillars = []
        for i, cluster in enumerate(clusters[:4]):
            pillars.append({
                "name": cluster.cluster_name,
                "description": cluster.theme.description,
                "keywords": cluster.keywords[:5],
                "priority": "high" if i < 2 else "medium",
                "total_opportunity": cluster.total_search_volume
            })

        content_items = []
        for i, opp in enumerate(opportunities[:20]):
            week = (i // 2) + 1
            pillar_name = pillars[i % len(pillars)]["name"] if pillars else "Content"

            content_items.append({
                "title": f"Guide to {opp.get('keyword', '')}",
                "pillar": pillar_name,
                "content_type": "blog_post",
                "target_keyword": opp.get('keyword', ''),
                "supporting_keywords": [],
                "priority": "high" if i < 5 else "medium",
                "estimated_difficulty": "medium",
                "estimated_hours": 6,
                "week_number": week,
                "optimization_tips": ["Include target keyword in title", "Use long-form content (2000+ words)"]
            })

        return {
            "pillars": pillars,
            "content_items": content_items,
            "quick_wins": [item["title"] for item in content_items[:3]],
            "implementation_notes": "Focus on high-priority content first, build authority gradually",
            "success_metrics": ["Organic traffic growth", "Keyword rankings", "Conversion rate"]
        }

    def _parse_strategy_response(
        self,
        strategy_data: Dict[str, Any],
        seed_keyword: str,
        clusters: List[KeywordCluster],
        opportunities: List[Dict[str, Any]]
    ) -> ContentStrategy:
        """Transform AI response to ContentStrategy model"""

        # Create content pillars
        pillars = [
            ContentPillar(
                id=f"pillar_{i}",
                name=p['name'],
                description=p['description'],
                keywords=p.get('keywords', []),
                priority=Priority(p.get('priority', 'medium')),
                total_opportunity=p.get('total_opportunity', 0),
                cluster_ids=[c.cluster_id for c in clusters if c.cluster_name == p['name']][:3]
            )
            for i, p in enumerate(strategy_data.get('pillars', []))
        ]

        # Create content items
        start_date = datetime.now()
        items = []
        for item_data in strategy_data.get('content_items', []):
            week = item_data.get('week_number', 1)
            publish_date = start_date + timedelta(weeks=week-1)

            items.append(ContentItem(
                id=f"item_{len(items)}",
                title=item_data['title'],
                pillar_name=item_data['pillar'],
                content_type=ContentType(item_data.get('content_type', 'blog_post')),
                target_keyword=item_data['target_keyword'],
                supporting_keywords=item_data.get('supporting_keywords', []),
                priority=Priority(item_data.get('priority', 'medium')),
                estimated_difficulty=Difficulty(item_data.get('estimated_difficulty', 'medium')),
                estimated_hours=item_data.get('estimated_hours', 4),
                scheduled_date=publish_date,
                optimization_tips=item_data.get('optimization_tips', []),
                status=ContentStatus.PLANNED
            ))

        # Build strategy
        strategy = ContentStrategy(
            seed_keyword=seed_keyword,
            generated_at=datetime.now(),
            pillars=pillars,
            content_items=items,
            quick_wins=strategy_data.get('quick_wins', []),
            implementation_notes=strategy_data.get('implementation_notes', ''),
            success_metrics=strategy_data.get('success_metrics', []),
            total_pieces=len(items),
            estimated_total_hours=sum(i.estimated_hours for i in items),
            timeline_weeks=max([item_data.get('week_number', 1) for item_data in strategy_data.get('content_items', [])]) if strategy_data.get('content_items') else 12
        )

        return strategy
