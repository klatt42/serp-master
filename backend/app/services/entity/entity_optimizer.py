"""
Entity Optimizer Orchestrator
Coordinates all entity optimization services
"""

import logging
from typing import Dict, Optional
from datetime import datetime

from app.models.entity_models import (
    EntityOptimizationRequest,
    EntityOptimizationResponse,
    EntityOptimizationScore,
    BusinessDescriptionRequest,
    SchemaGenerationRequest,
    RelationshipAnalysisRequest,
    AboutPageOptimizationRequest,
    NAPValidationRequest
)

from app.services.entity.description_generator import BusinessDescriptionGenerator
from app.services.entity.schema_generator import SchemaGenerator
from app.services.entity.relationship_analyzer import RelationshipAnalyzer
from app.services.entity.about_optimizer import AboutPageOptimizer
from app.services.entity.nap_validator import NAPValidator

logger = logging.getLogger(__name__)


class EntityOptimizer:
    """Orchestrate all entity optimization features"""

    def __init__(self):
        """Initialize entity optimizer"""
        self.description_generator = BusinessDescriptionGenerator()
        self.schema_generator = SchemaGenerator()
        self.relationship_analyzer = RelationshipAnalyzer()
        self.about_optimizer = AboutPageOptimizer()
        self.nap_validator = NAPValidator()

    async def optimize_entity(
        self,
        request: EntityOptimizationRequest,
        site_data: Optional[Dict] = None
    ) -> EntityOptimizationResponse:
        """
        Perform comprehensive entity optimization

        Args:
            request: Entity optimization request
            site_data: Optional pre-analyzed site data

        Returns:
            Complete entity optimization response
        """
        try:
            # Initialize results
            business_descriptions = None
            schema_markups = None
            relationships = None
            about_page_analysis = None
            nap_validation = None

            # Run requested optimizations
            if request.include_description:
                logger.info("Generating business descriptions...")
                desc_request = BusinessDescriptionRequest(
                    site_url=request.site_url,
                    business_name=request.business_name,
                    industry=site_data.get("industry") if site_data else None,
                    location=site_data.get("location") if site_data else None,
                    target_keywords=site_data.get("keywords") if site_data else None,
                    existing_description=site_data.get("meta_description") if site_data else None
                )
                business_descriptions = await self.description_generator.generate_descriptions(desc_request)

            if request.include_schema:
                logger.info("Generating schema markups...")
                schema_request = SchemaGenerationRequest(
                    site_url=request.site_url,
                    business_type=site_data.get("business_type") if site_data else None,
                    generate_types=["Organization", "LocalBusiness", "Service", "FAQ", "BreadcrumbList"]
                )
                schema_markups = await self.schema_generator.generate_schemas(schema_request, site_data)

            if request.include_relationships:
                logger.info("Analyzing entity relationships...")
                rel_request = RelationshipAnalysisRequest(
                    site_url=request.site_url
                )
                relationships = await self.relationship_analyzer.analyze_relationships(rel_request, site_data)

            if request.include_about_page:
                logger.info("Optimizing About page...")
                about_request = AboutPageOptimizationRequest(
                    site_url=request.site_url
                )
                about_page_analysis = await self.about_optimizer.optimize_about_page(about_request, site_data)

            if request.include_nap:
                logger.info("Validating NAP consistency...")
                nap_request = NAPValidationRequest(
                    site_url=request.site_url
                )
                nap_validation = await self.nap_validator.validate_nap(nap_request, site_data)

            # Calculate scores
            scores = self._calculate_scores(
                business_descriptions,
                schema_markups,
                relationships,
                about_page_analysis,
                nap_validation
            )

            # Identify quick wins
            quick_wins = self._identify_quick_wins(
                business_descriptions,
                schema_markups,
                relationships,
                about_page_analysis,
                nap_validation
            )

            # Prioritize actions
            priority_actions = self._prioritize_actions(
                scores,
                business_descriptions,
                schema_markups,
                relationships,
                about_page_analysis,
                nap_validation
            )

            return EntityOptimizationResponse(
                scores=scores,
                business_descriptions=business_descriptions,
                schema_markups=schema_markups,
                relationships=relationships,
                about_page_analysis=about_page_analysis,
                nap_validation=nap_validation,
                quick_wins=quick_wins,
                priority_actions=priority_actions,
                analyzed_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error in entity optimization: {str(e)}")
            raise

    def _calculate_scores(
        self,
        business_descriptions,
        schema_markups,
        relationships,
        about_page_analysis,
        nap_validation
    ) -> EntityOptimizationScore:
        """Calculate optimization scores"""
        # Description score
        description_score = 0
        if business_descriptions and business_descriptions.variations:
            description_score = business_descriptions.variations[0].overall_score

        # Schema score
        schema_score = 0
        if schema_markups and schema_markups.schemas:
            valid_schemas = [s for s in schema_markups.schemas if s.validation_status == "valid"]
            eligible_schemas = [s for s in schema_markups.schemas if s.rich_snippet_eligible]

            if schema_markups.schemas:
                schema_score = int(
                    (len(valid_schemas) / len(schema_markups.schemas)) * 50 +
                    (len(eligible_schemas) / len(schema_markups.schemas)) * 50
                )

        # Relationship score
        relationship_score = 0
        if relationships and relationships.relationships:
            total_rels = len(relationships.relationships)
            high_authority = len([r for r in relationships.relationships if r.authority_score >= 8])
            schema_opportunities = len([r for r in relationships.relationships if r.schema_opportunity])

            if total_rels > 0:
                relationship_score = int(
                    min(100, (total_rels * 10) + (high_authority * 15) + (schema_opportunities * 5))
                )

        # About page score
        about_page_score = 0
        if about_page_analysis:
            about_page_score = about_page_analysis.current_metrics.overall_quality_score

        # NAP consistency score
        nap_consistency_score = 0
        if nap_validation:
            nap_consistency_score = nap_validation.consistency_score

        # Overall score (weighted average)
        overall_score = int(
            description_score * 0.20 +
            schema_score * 0.25 +
            relationship_score * 0.15 +
            about_page_score * 0.25 +
            nap_consistency_score * 0.15
        )

        return EntityOptimizationScore(
            overall_score=overall_score,
            description_score=description_score,
            schema_score=schema_score,
            relationship_score=relationship_score,
            about_page_score=about_page_score,
            nap_consistency_score=nap_consistency_score
        )

    def _identify_quick_wins(
        self,
        business_descriptions,
        schema_markups,
        relationships,
        about_page_analysis,
        nap_validation
    ) -> list:
        """Identify quick win opportunities"""
        quick_wins = []

        # Business description quick wins
        if business_descriptions and business_descriptions.variations:
            best_desc = business_descriptions.variations[0]
            if best_desc.overall_score >= 80:
                quick_wins.append({
                    "category": "description",
                    "title": "Copy Optimized Business Description",
                    "description": f"Use the top-scoring description (score: {best_desc.overall_score}/100) for your meta description and Google Business Profile",
                    "effort": "5 minutes",
                    "impact": "Immediate improvement in search appearance"
                })

        # Schema markup quick wins
        if schema_markups and schema_markups.schemas:
            ready_schemas = [s for s in schema_markups.schemas if s.validation_status == "valid"]
            if ready_schemas:
                quick_wins.append({
                    "category": "schema",
                    "title": "Implement Schema Markup",
                    "description": f"{len(ready_schemas)} ready-to-use schema markups available. Copy-paste into your website's <head> section.",
                    "effort": "10-15 minutes",
                    "impact": "Enhanced search visibility and rich snippets"
                })

        # Relationship quick wins
        if relationships and relationships.relationships:
            high_value = [r for r in relationships.relationships if r.authority_score >= 8]
            if high_value and len(high_value) >= 3:
                quick_wins.append({
                    "category": "relationships",
                    "title": "Showcase High-Authority Credentials",
                    "description": f"You have {len(high_value)} high-authority relationships. Add these to your homepage footer or create a credentials section.",
                    "effort": "15 minutes",
                    "impact": "Increased trust and authority signals"
                })

        # About page quick wins
        if about_page_analysis:
            if about_page_analysis.current_metrics.overall_quality_score < 60:
                if about_page_analysis.content_suggestions:
                    top_suggestion = about_page_analysis.content_suggestions[0]
                    quick_wins.append({
                        "category": "about_page",
                        "title": f"Add {top_suggestion['section']}",
                        "description": top_suggestion['content'],
                        "effort": top_suggestion.get('estimated_length', '10-15 minutes'),
                        "impact": "Better entity recognition and trust"
                    })

        # NAP quick wins
        if nap_validation and nap_validation.consistency_score < 90:
            if nap_validation.inconsistencies:
                quick_wins.append({
                    "category": "nap",
                    "title": "Fix NAP Inconsistencies",
                    "description": f"{len(nap_validation.inconsistencies)} inconsistencies detected. Standardize your business name, address, and phone across all pages.",
                    "effort": "20-30 minutes",
                    "impact": "Critical for local SEO and entity recognition"
                })

        return quick_wins

    def _prioritize_actions(
        self,
        scores: EntityOptimizationScore,
        business_descriptions,
        schema_markups,
        relationships,
        about_page_analysis,
        nap_validation
    ) -> list:
        """Prioritize optimization actions"""
        actions = []

        # Priority 1: Critical issues (score < 50)
        if scores.nap_consistency_score < 50:
            actions.append({
                "priority": 1,
                "category": "nap",
                "title": "🔴 CRITICAL: Fix NAP Inconsistencies",
                "description": "NAP inconsistencies severely hurt local SEO and entity recognition",
                "action": "Standardize Name, Address, Phone across all pages and citations",
                "expected_impact": "High"
            })

        if scores.schema_score < 50:
            actions.append({
                "priority": 1,
                "category": "schema",
                "title": "🔴 CRITICAL: Add Schema Markup",
                "description": "Missing or invalid schema markup prevents rich snippets",
                "action": "Implement Organization and LocalBusiness schema",
                "expected_impact": "High"
            })

        # Priority 2: Important improvements (score 50-70)
        if 50 <= scores.about_page_score < 70:
            actions.append({
                "priority": 2,
                "category": "about_page",
                "title": "🟡 IMPORTANT: Improve About Page",
                "description": "About page needs more entity signals and trust indicators",
                "action": "Add team bios, credentials, and company history",
                "expected_impact": "Medium-High"
            })

        if 50 <= scores.description_score < 70:
            actions.append({
                "priority": 2,
                "category": "description",
                "title": "🟡 IMPORTANT: Optimize Business Description",
                "description": "Business description needs better keyword optimization",
                "action": "Use the generated descriptions for meta tags and profiles",
                "expected_impact": "Medium"
            })

        # Priority 3: Optimizations (score 70-90)
        if 70 <= scores.relationship_score < 90:
            actions.append({
                "priority": 3,
                "category": "relationships",
                "title": "🟢 OPTIMIZE: Expand Authority Relationships",
                "description": "Good relationships, but room to grow",
                "action": "Add more certifications, partnerships, or industry affiliations",
                "expected_impact": "Medium"
            })

        if 70 <= scores.schema_score < 90:
            actions.append({
                "priority": 3,
                "category": "schema",
                "title": "🟢 OPTIMIZE: Expand Schema Coverage",
                "description": "Add additional schema types for better visibility",
                "action": "Implement Service, FAQ, and Product schemas where applicable",
                "expected_impact": "Medium"
            })

        # Priority 4: Excellence (score >= 90)
        if scores.overall_score >= 90:
            actions.append({
                "priority": 4,
                "category": "maintenance",
                "title": "✅ MAINTAIN: Entity Optimization Excellent",
                "description": "Your entity optimization is excellent",
                "action": "Monitor and maintain consistency, update as business evolves",
                "expected_impact": "Low (maintenance)"
            })

        # Sort by priority
        actions.sort(key=lambda x: x["priority"])

        return actions
