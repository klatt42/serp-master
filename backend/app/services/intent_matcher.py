"""
Intent Matcher - Classify keywords by user intent and map to platforms
Categorizes keywords into: Discovery, Research, Decision intents
"""

from typing import List, Dict
from enum import Enum


class UserIntent(str, Enum):
    """User intent categories"""
    DISCOVERY = "discovery"      # TikTok, Instagram - exploring/awareness
    RESEARCH = "research"         # YouTube, Blog - learning/comparison
    DECISION = "decision"         # Amazon, Google - ready to buy/act
    VALIDATION = "validation"     # Reddit, Reviews - social proof


class IntentMatcher:
    """Match keywords to user intent and recommend platforms"""

    # Intent signal patterns
    DISCOVERY_SIGNALS = [
        "trending", "popular", "viral", "new", "latest",
        "ideas", "inspiration", "cool", "interesting"
    ]

    RESEARCH_SIGNALS = [
        "how to", "guide", "tutorial", "learn", "explained",
        "review", "comparison", "vs", "best", "top", "tips"
    ]

    DECISION_SIGNALS = [
        "buy", "price", "cheap", "deal", "discount", "sale",
        "near me", "location", "contact", "hire", "service"
    ]

    VALIDATION_SIGNALS = [
        "review", "opinion", "experience", "worth it", "legit",
        "recommend", "thoughts", "should i", "advice"
    ]

    # Platform-intent mapping
    PLATFORM_INTENT_MAP = {
        UserIntent.DISCOVERY: ["tiktok", "instagram", "pinterest"],
        UserIntent.RESEARCH: ["youtube", "blog", "google"],
        UserIntent.DECISION: ["amazon", "google", "local_search"],
        UserIntent.VALIDATION: ["reddit", "reviews", "forums"]
    }

    def classify_intent(self, keyword: str) -> Dict:
        """
        Classify keyword by user intent

        Args:
            keyword: Search keyword to classify

        Returns:
            Dict with primary intent, confidence, and recommended platforms
        """
        keyword_lower = keyword.lower()

        # Calculate intent scores
        intent_scores = {
            UserIntent.DISCOVERY: self._calculate_intent_score(
                keyword_lower, self.DISCOVERY_SIGNALS
            ),
            UserIntent.RESEARCH: self._calculate_intent_score(
                keyword_lower, self.RESEARCH_SIGNALS
            ),
            UserIntent.DECISION: self._calculate_intent_score(
                keyword_lower, self.DECISION_SIGNALS
            ),
            UserIntent.VALIDATION: self._calculate_intent_score(
                keyword_lower, self.VALIDATION_SIGNALS
            )
        }

        # Determine primary intent
        primary_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[primary_intent]

        # Get secondary intents (score > 0.3)
        secondary_intents = [
            intent for intent, score in intent_scores.items()
            if score > 0.3 and intent != primary_intent
        ]

        # Recommend platforms
        recommended_platforms = self._recommend_platforms(
            primary_intent, secondary_intents
        )

        return {
            "keyword": keyword,
            "primary_intent": primary_intent,
            "confidence": round(confidence, 2),
            "intent_scores": {k.value: round(v, 2) for k, v in intent_scores.items()},
            "secondary_intents": [i.value for i in secondary_intents],
            "recommended_platforms": recommended_platforms,
            "content_strategy": self._generate_content_strategy(
                primary_intent, recommended_platforms
            )
        }

    def _calculate_intent_score(self, keyword: str, signals: List[str]) -> float:
        """Calculate intent score based on signal matches"""
        if not signals:
            return 0.0

        matches = sum(1 for signal in signals if signal in keyword)

        # Base score from matches
        base_score = matches / len(signals)

        # Boost score if signal is at start of keyword (stronger signal)
        start_boost = 0.2 if any(keyword.startswith(signal) for signal in signals) else 0

        return min(base_score + start_boost, 1.0)

    def _recommend_platforms(
        self,
        primary_intent: UserIntent,
        secondary_intents: List[UserIntent]
    ) -> List[Dict]:
        """Recommend platforms based on intents"""
        recommendations = []

        # Primary platforms (high priority)
        primary_platforms = self.PLATFORM_INTENT_MAP.get(primary_intent, [])
        for platform in primary_platforms:
            recommendations.append({
                "platform": platform,
                "priority": "high",
                "intent_match": primary_intent.value,
                "reason": f"Strong match for {primary_intent.value} intent"
            })

        # Secondary platforms (medium priority)
        for intent in secondary_intents:
            secondary_platforms = self.PLATFORM_INTENT_MAP.get(intent, [])
            for platform in secondary_platforms:
                # Avoid duplicates
                if not any(r["platform"] == platform for r in recommendations):
                    recommendations.append({
                        "platform": platform,
                        "priority": "medium",
                        "intent_match": intent.value,
                        "reason": f"Good match for {intent.value} intent"
                    })

        return recommendations

    def _generate_content_strategy(
        self,
        intent: UserIntent,
        platforms: List[Dict]
    ) -> Dict:
        """Generate content strategy based on intent"""
        strategies = {
            UserIntent.DISCOVERY: {
                "content_type": "Short-form, visual content",
                "format": "15-60 second videos, eye-catching images",
                "goal": "Brand awareness and engagement",
                "cta": "Follow for more, engage with content",
                "key_metrics": ["views", "shares", "saves"]
            },
            UserIntent.RESEARCH: {
                "content_type": "Educational, in-depth content",
                "format": "Long-form videos, comprehensive blog posts",
                "goal": "Establish authority and trust",
                "cta": "Subscribe, save for later, share",
                "key_metrics": ["watch time", "engagement rate", "backlinks"]
            },
            UserIntent.DECISION: {
                "content_type": "Conversion-focused content",
                "format": "Product reviews, comparisons, CTAs",
                "goal": "Drive purchases or conversions",
                "cta": "Buy now, get quote, contact us",
                "key_metrics": ["conversion rate", "click-through rate", "revenue"]
            },
            UserIntent.VALIDATION: {
                "content_type": "Social proof, testimonials",
                "format": "Reviews, community discussions, case studies",
                "goal": "Build trust and credibility",
                "cta": "Read reviews, join community",
                "key_metrics": ["engagement", "sentiment", "trust score"]
            }
        }

        base_strategy = strategies.get(intent, {})
        base_strategy["recommended_platforms"] = [p["platform"] for p in platforms if p["priority"] == "high"]

        return base_strategy

    def batch_classify(self, keywords: List[str]) -> Dict:
        """
        Classify multiple keywords and generate insights

        Args:
            keywords: List of keywords to classify

        Returns:
            Dict with classifications and aggregated insights
        """
        classifications = []
        intent_distribution = {intent: 0 for intent in UserIntent}
        platform_recommendations = {}

        for keyword in keywords:
            classification = self.classify_intent(keyword)
            classifications.append(classification)

            # Track intent distribution
            intent_distribution[UserIntent(classification["primary_intent"])] += 1

            # Track platform recommendations
            for rec in classification["recommended_platforms"]:
                platform = rec["platform"]
                if platform not in platform_recommendations:
                    platform_recommendations[platform] = {
                        "count": 0,
                        "keywords": []
                    }
                platform_recommendations[platform]["count"] += 1
                platform_recommendations[platform]["keywords"].append(keyword)

        # Calculate percentages
        total = len(keywords)
        intent_percentages = {
            intent.value: round((count / total) * 100, 1)
            for intent, count in intent_distribution.items()
        }

        return {
            "classifications": classifications,
            "insights": {
                "total_keywords": total,
                "intent_distribution": intent_percentages,
                "top_platforms": sorted(
                    platform_recommendations.items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )[:5],
                "content_mix_recommendation": self._recommend_content_mix(
                    intent_distribution
                )
            }
        }

    def _recommend_content_mix(self, intent_distribution: Dict) -> Dict:
        """Recommend content distribution across intents"""
        total = sum(intent_distribution.values())

        recommendations = {}
        for intent, count in intent_distribution.items():
            percentage = (count / total) * 100 if total > 0 else 0

            if percentage > 30:
                recommendations[intent.value] = {
                    "current": round(percentage, 1),
                    "recommended": round(percentage, 1),
                    "action": "Maintain current focus"
                }
            elif percentage < 15:
                recommendations[intent.value] = {
                    "current": round(percentage, 1),
                    "recommended": 20.0,
                    "action": "Increase content for this intent"
                }
            else:
                recommendations[intent.value] = {
                    "current": round(percentage, 1),
                    "recommended": round(percentage, 1),
                    "action": "Current balance is good"
                }

        return recommendations
