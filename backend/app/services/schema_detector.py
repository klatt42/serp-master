"""
Schema Markup Detector
Detects and validates structured data (JSON-LD, Microdata, RDFa) for AEO scoring
"""

import json
import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class SchemaDetector:
    """
    Detects and scores schema markup implementation
    Supports JSON-LD, Microdata, and RDFa formats

    Scoring breakdown (10 points total):
    - Organization schema: 3 points
    - LocalBusiness schema: 3 points
    - FAQPage schema: 2 points
    - Product/Service schema: 2 points
    """

    # Schema types we're looking for
    SCHEMA_TYPES = {
        "Organization": {
            "points": 3,
            "required_fields": ["name", "url"],
            "recommended_fields": ["logo", "description", "sameAs"]
        },
        "LocalBusiness": {
            "points": 3,
            "required_fields": ["name", "address"],
            "recommended_fields": ["telephone", "openingHours", "geo"]
        },
        "FAQPage": {
            "points": 2,
            "required_fields": ["mainEntity"],
            "recommended_fields": []
        },
        "Product": {
            "points": 2,
            "required_fields": ["name"],
            "recommended_fields": ["offers", "brand", "image"]
        },
        "Service": {
            "points": 2,
            "required_fields": ["name", "provider"],
            "recommended_fields": ["offers", "areaServed"]
        },
        "Article": {
            "points": 1,
            "required_fields": ["headline", "author"],
            "recommended_fields": ["datePublished", "image"]
        },
        "BreadcrumbList": {
            "points": 1,
            "required_fields": ["itemListElement"],
            "recommended_fields": []
        }
    }

    def detect_schemas(self, html_content: str) -> Dict[str, Any]:
        """
        Main method to detect all schema types in HTML

        Args:
            html_content: Raw HTML content to analyze

        Returns:
            Dictionary with detected schemas and score
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')

            detected_schemas = []

            # Detect JSON-LD schemas
            jsonld_schemas = self._detect_jsonld(soup)
            detected_schemas.extend(jsonld_schemas)

            # Detect Microdata schemas
            microdata_schemas = self._detect_microdata(soup)
            detected_schemas.extend(microdata_schemas)

            # Detect RDFa schemas
            rdfa_schemas = self._detect_rdfa(soup)
            detected_schemas.extend(rdfa_schemas)

            # Calculate score
            score_data = self._calculate_schema_score(detected_schemas)

            # Identify missing schemas
            missing_schemas = self._identify_missing_schemas(detected_schemas)

            # Generate recommendations
            recommendations = self._generate_recommendations(detected_schemas, missing_schemas)

            return {
                "schema_score": score_data["total_score"],
                "max_score": 10,
                "detected_schemas": detected_schemas,
                "missing_schemas": missing_schemas,
                "recommendations": recommendations,
                "breakdown": score_data["breakdown"]
            }

        except Exception as e:
            logger.error(f"Error detecting schemas: {str(e)}")
            return {
                "schema_score": 0,
                "max_score": 10,
                "error": str(e),
                "detected_schemas": [],
                "missing_schemas": list(self.SCHEMA_TYPES.keys()),
                "recommendations": ["Fix HTML parsing errors before adding schema markup"]
            }

    def _detect_jsonld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Detect JSON-LD schema markup"""
        schemas = []

        # Find all JSON-LD script tags
        jsonld_scripts = soup.find_all('script', type='application/ld+json')

        for script in jsonld_scripts:
            try:
                # Parse JSON content
                schema_data = json.loads(script.string)

                # Handle both single schema and array of schemas
                if isinstance(schema_data, list):
                    for item in schema_data:
                        schemas.extend(self._process_jsonld_item(item))
                else:
                    schemas.extend(self._process_jsonld_item(schema_data))

            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON-LD: {str(e)}")
                continue

        return schemas

    def _process_jsonld_item(self, item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a single JSON-LD item"""
        schemas = []

        if not isinstance(item, dict):
            return schemas

        # Get schema type
        schema_type = item.get('@type', '')

        # Handle graph objects
        if '@graph' in item:
            for graph_item in item['@graph']:
                schemas.extend(self._process_jsonld_item(graph_item))
            return schemas

        # Check if this is a schema type we're tracking
        for tracked_type, config in self.SCHEMA_TYPES.items():
            if schema_type == tracked_type or (isinstance(schema_type, list) and tracked_type in schema_type):
                # Validate the schema
                validation = self._validate_schema(item, tracked_type)

                schemas.append({
                    "type": tracked_type,
                    "format": "JSON-LD",
                    "present": True,
                    "valid": validation["valid"],
                    "fields": list(item.keys()),
                    "missing_required": validation["missing_required"],
                    "missing_recommended": validation["missing_recommended"],
                    "points": config["points"] if validation["valid"] else config["points"] // 2,
                    "data": item
                })

        return schemas

    def _detect_microdata(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Detect Microdata schema markup"""
        schemas = []

        # Find all elements with itemscope
        items = soup.find_all(attrs={"itemscope": True})

        for item in items:
            itemtype = item.get('itemtype', '')

            # Extract schema type from itemtype URL
            if itemtype:
                # Handle both full URLs and short names
                if 'schema.org/' in itemtype:
                    schema_type = itemtype.split('schema.org/')[-1].strip('/')
                else:
                    schema_type = itemtype

                # Check if this is a tracked schema type
                if schema_type in self.SCHEMA_TYPES:
                    # Extract properties
                    props = {}
                    for prop in item.find_all(attrs={"itemprop": True}):
                        prop_name = prop.get('itemprop')
                        prop_value = prop.get('content', prop.text.strip())
                        props[prop_name] = prop_value

                    # Validate
                    validation = self._validate_schema(props, schema_type)
                    config = self.SCHEMA_TYPES[schema_type]

                    schemas.append({
                        "type": schema_type,
                        "format": "Microdata",
                        "present": True,
                        "valid": validation["valid"],
                        "fields": list(props.keys()),
                        "missing_required": validation["missing_required"],
                        "missing_recommended": validation["missing_recommended"],
                        "points": config["points"] if validation["valid"] else config["points"] // 2,
                        "data": props
                    })

        return schemas

    def _detect_rdfa(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Detect RDFa schema markup"""
        schemas = []

        # Find all elements with typeof attribute
        items = soup.find_all(attrs={"typeof": True})

        for item in items:
            schema_type = item.get('typeof', '')

            # Check if this is a tracked schema type
            if schema_type in self.SCHEMA_TYPES:
                # Extract properties
                props = {}
                for prop in item.find_all(attrs={"property": True}):
                    prop_name = prop.get('property')
                    prop_value = prop.get('content', prop.text.strip())
                    props[prop_name] = prop_value

                # Validate
                validation = self._validate_schema(props, schema_type)
                config = self.SCHEMA_TYPES[schema_type]

                schemas.append({
                    "type": schema_type,
                    "format": "RDFa",
                    "present": True,
                    "valid": validation["valid"],
                    "fields": list(props.keys()),
                    "missing_required": validation["missing_required"],
                    "missing_recommended": validation["missing_recommended"],
                    "points": config["points"] if validation["valid"] else config["points"] // 2,
                    "data": props
                })

        return schemas

    def _validate_schema(self, schema_data: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """
        Validate that schema has required and recommended fields

        Args:
            schema_data: The schema object to validate
            schema_type: The type of schema (Organization, LocalBusiness, etc.)

        Returns:
            Validation result with missing fields
        """
        config = self.SCHEMA_TYPES.get(schema_type, {})
        required_fields = config.get("required_fields", [])
        recommended_fields = config.get("recommended_fields", [])

        # Check for required fields
        missing_required = []
        for field in required_fields:
            if field not in schema_data or not schema_data[field]:
                missing_required.append(field)

        # Check for recommended fields
        missing_recommended = []
        for field in recommended_fields:
            if field not in schema_data or not schema_data[field]:
                missing_recommended.append(field)

        # Schema is valid if all required fields are present
        valid = len(missing_required) == 0

        return {
            "valid": valid,
            "missing_required": missing_required,
            "missing_recommended": missing_recommended
        }

    def _calculate_schema_score(self, detected_schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total schema score"""
        total_score = 0
        breakdown = {}

        # Track which schema types we've scored (avoid double-counting)
        scored_types = set()

        for schema in detected_schemas:
            schema_type = schema["type"]

            # Only count each schema type once (highest score if multiple)
            if schema_type not in scored_types:
                points = schema.get("points", 0)
                total_score += points
                scored_types.add(schema_type)

                breakdown[schema_type] = {
                    "points": points,
                    "format": schema["format"],
                    "valid": schema["valid"]
                }
            elif schema_type in breakdown:
                # If we found a better implementation, use it
                if schema.get("points", 0) > breakdown[schema_type]["points"]:
                    total_score = total_score - breakdown[schema_type]["points"] + schema.get("points", 0)
                    breakdown[schema_type] = {
                        "points": schema.get("points", 0),
                        "format": schema["format"],
                        "valid": schema["valid"]
                    }

        # Cap at max score
        total_score = min(total_score, 10)

        return {
            "total_score": total_score,
            "breakdown": breakdown
        }

    def _identify_missing_schemas(self, detected_schemas: List[Dict[str, Any]]) -> List[str]:
        """Identify which important schemas are missing"""
        detected_types = {schema["type"] for schema in detected_schemas}

        # Focus on high-value missing schemas
        important_schemas = ["Organization", "LocalBusiness", "FAQPage", "Product", "Service"]

        missing = []
        for schema_type in important_schemas:
            if schema_type not in detected_types:
                missing.append(schema_type)

        return missing

    def _generate_recommendations(
        self,
        detected_schemas: List[Dict[str, Any]],
        missing_schemas: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Check for missing high-value schemas
        if "Organization" in missing_schemas:
            recommendations.append(
                "Add Organization schema to establish your business entity (+3 points). "
                "Include name, url, logo, and description fields."
            )

        if "LocalBusiness" in missing_schemas:
            recommendations.append(
                "Add LocalBusiness schema for local SEO (+3 points). "
                "Include address, telephone, and opening hours."
            )

        if "FAQPage" in missing_schemas:
            recommendations.append(
                "Add FAQPage schema to improve voice search visibility (+2 points). "
                "Structure your FAQ content with proper markup."
            )

        # Check for invalid schemas (missing required fields)
        for schema in detected_schemas:
            if not schema["valid"] and schema["missing_required"]:
                recommendations.append(
                    f"{schema['type']} schema is incomplete. "
                    f"Add required fields: {', '.join(schema['missing_required'])} "
                    f"to gain full {self.SCHEMA_TYPES[schema['type']]['points']} points."
                )

        # Check for schemas missing recommended fields
        for schema in detected_schemas:
            if schema["valid"] and schema["missing_recommended"]:
                recommendations.append(
                    f"Enhance {schema['type']} schema with: {', '.join(schema['missing_recommended'][:2])} "
                    f"for better AI understanding."
                )

        # If everything is perfect
        if not recommendations:
            recommendations.append(
                "Excellent schema implementation! Your structured data is helping AI understand your content."
            )

        return recommendations
