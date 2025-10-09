"""
Schema Markup Auto-Generator
Automatically generates copy-paste ready Schema.org JSON-LD markup
"""

import os
import logging
import json
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse

from app.models.entity_models import (
    SchemaMarkup,
    SchemaGenerationRequest,
    SchemaGenerationResponse,
    NAPData
)

logger = logging.getLogger(__name__)


class SchemaGenerator:
    """Generate Schema.org JSON-LD markup for entity optimization"""

    def __init__(self):
        """Initialize schema generator"""
        self.schema_context = "https://schema.org"

        # Business type mappings to schema types
        self.business_type_map = {
            "restaurant": "Restaurant",
            "cafe": "CafeOrCoffeeShop",
            "plumbing": "Plumber",
            "plumber": "Plumber",
            "electrician": "Electrician",
            "electrical": "Electrician",
            "hvac": "HVACBusiness",
            "lawyer": "Attorney",
            "attorney": "Attorney",
            "legal": "Attorney",
            "dentist": "Dentist",
            "dental": "Dentist",
            "doctor": "Physician",
            "medical": "MedicalBusiness",
            "real estate": "RealEstateAgent",
            "realtor": "RealEstateAgent",
            "hotel": "Hotel",
            "store": "Store",
            "shop": "Store",
            "retail": "Store",
            "cleaning": "HomeAndConstructionBusiness",
            "construction": "GeneralContractor",
            "contractor": "GeneralContractor",
            "landscaping": "HomeAndConstructionBusiness",
            "roofing": "RoofingContractor",
            "painting": "HomeAndConstructionBusiness",
            "auto repair": "AutoRepair",
            "mechanic": "AutoRepair",
            "salon": "BeautySalon",
            "barber": "BarberShop",
            "gym": "ExerciseGym",
            "fitness": "HealthClub",
            "accounting": "AccountingService",
            "accountant": "AccountingService",
            "insurance": "InsuranceAgency",
        }

    async def generate_schemas(
        self,
        request: SchemaGenerationRequest,
        site_data: Optional[Dict] = None
    ) -> SchemaGenerationResponse:
        """
        Generate all applicable schema markups for a site

        Args:
            request: Schema generation request
            site_data: Optional pre-analyzed site data

        Returns:
            Response with generated schemas
        """
        try:
            # Detect business type if not provided
            business_type = request.business_type or await self._detect_business_type(
                request.site_url,
                site_data
            )

            # Generate requested schema types
            schemas = []
            recommendations = []

            for schema_type in request.generate_types:
                if schema_type == "Organization":
                    schema = await self._generate_organization_schema(
                        request.site_url,
                        site_data,
                        business_type
                    )
                    schemas.append(schema)

                elif schema_type == "LocalBusiness":
                    schema = await self._generate_local_business_schema(
                        request.site_url,
                        site_data,
                        business_type
                    )
                    schemas.append(schema)

                elif schema_type == "Service":
                    service_schemas = await self._generate_service_schemas(
                        request.site_url,
                        site_data,
                        business_type
                    )
                    schemas.extend(service_schemas)

                elif schema_type == "Product":
                    product_schemas = await self._generate_product_schemas(
                        request.site_url,
                        site_data
                    )
                    schemas.extend(product_schemas)

                elif schema_type == "FAQ":
                    faq_schema = await self._generate_faq_schema(
                        request.site_url,
                        site_data
                    )
                    if faq_schema:
                        schemas.append(faq_schema)

                elif schema_type == "BreadcrumbList":
                    breadcrumb_schema = await self._generate_breadcrumb_schema(
                        request.site_url,
                        site_data
                    )
                    if breadcrumb_schema:
                        schemas.append(breadcrumb_schema)

            # Generate recommendations
            recommendations = self._generate_schema_recommendations(
                schemas,
                business_type,
                site_data
            )

            return SchemaGenerationResponse(
                schemas=schemas,
                detected_business_type=business_type,
                recommendations=recommendations,
                generated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error generating schemas: {str(e)}")
            raise

    async def _detect_business_type(
        self,
        site_url: str,
        site_data: Optional[Dict]
    ) -> str:
        """Detect business type from site data"""
        if not site_data:
            return "Organization"

        # Check existing schema
        if site_data.get("existing_schema"):
            for schema in site_data["existing_schema"]:
                if schema.get("@type"):
                    return schema["@type"]

        # Check content for business type indicators
        content = (site_data.get("content", "") + " " +
                  site_data.get("title", "") + " " +
                  site_data.get("meta_description", "")).lower()

        for keyword, schema_type in self.business_type_map.items():
            if keyword in content:
                return schema_type

        # Check if has address/phone (local business indicators)
        if site_data.get("address") or site_data.get("phone"):
            return "LocalBusiness"

        return "Organization"

    async def _generate_organization_schema(
        self,
        site_url: str,
        site_data: Optional[Dict],
        business_type: str
    ) -> SchemaMarkup:
        """Generate Organization schema"""
        parsed_url = urlparse(site_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        schema = {
            "@context": self.schema_context,
            "@type": "Organization",
            "name": site_data.get("business_name", parsed_url.netloc) if site_data else parsed_url.netloc,
            "url": base_url,
        }

        # Add optional fields if available
        if site_data:
            if site_data.get("description"):
                schema["description"] = site_data["description"]

            if site_data.get("logo"):
                schema["logo"] = urljoin(base_url, site_data["logo"])

            if site_data.get("phone"):
                schema["telephone"] = site_data["phone"]

            if site_data.get("email"):
                schema["email"] = site_data["email"]

            if site_data.get("address"):
                schema["address"] = self._format_address(site_data["address"])

            if site_data.get("social_profiles"):
                schema["sameAs"] = site_data["social_profiles"]

        # Validate and create markup
        validation = self._validate_schema(schema, "Organization")
        html_snippet = self._create_html_snippet(schema)

        return SchemaMarkup(
            schema_type="Organization",
            json_ld=schema,
            html_snippet=html_snippet,
            validation_status=validation["status"],
            validation_messages=validation["messages"],
            rich_snippet_eligible=validation["rich_snippet_eligible"],
            implementation_instructions=self._get_implementation_instructions("Organization")
        )

    async def _generate_local_business_schema(
        self,
        site_url: str,
        site_data: Optional[Dict],
        business_type: str
    ) -> SchemaMarkup:
        """Generate LocalBusiness schema"""
        parsed_url = urlparse(site_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Use specific business type if detected
        schema_type = business_type if business_type != "Organization" else "LocalBusiness"

        schema = {
            "@context": self.schema_context,
            "@type": schema_type,
            "name": site_data.get("business_name", parsed_url.netloc) if site_data else parsed_url.netloc,
            "url": base_url,
        }

        # Add local business specific fields
        if site_data:
            if site_data.get("description"):
                schema["description"] = site_data["description"]

            if site_data.get("logo"):
                schema["image"] = urljoin(base_url, site_data["logo"])

            if site_data.get("phone"):
                schema["telephone"] = site_data["phone"]

            if site_data.get("email"):
                schema["email"] = site_data["email"]

            # Address is critical for LocalBusiness
            if site_data.get("address"):
                schema["address"] = self._format_address(site_data["address"])

            # Hours of operation
            if site_data.get("hours"):
                schema["openingHoursSpecification"] = self._format_hours(site_data["hours"])

            # Price range
            if site_data.get("price_range"):
                schema["priceRange"] = site_data["price_range"]

            # Service area
            if site_data.get("service_area"):
                schema["areaServed"] = site_data["service_area"]

            # Reviews/ratings
            if site_data.get("rating"):
                schema["aggregateRating"] = {
                    "@type": "AggregateRating",
                    "ratingValue": site_data["rating"],
                    "reviewCount": site_data.get("review_count", 0)
                }

            if site_data.get("social_profiles"):
                schema["sameAs"] = site_data["social_profiles"]

        # Validate and create markup
        validation = self._validate_schema(schema, schema_type)
        html_snippet = self._create_html_snippet(schema)

        return SchemaMarkup(
            schema_type=schema_type,
            json_ld=schema,
            html_snippet=html_snippet,
            validation_status=validation["status"],
            validation_messages=validation["messages"],
            rich_snippet_eligible=validation["rich_snippet_eligible"],
            implementation_instructions=self._get_implementation_instructions("LocalBusiness")
        )

    async def _generate_service_schemas(
        self,
        site_url: str,
        site_data: Optional[Dict],
        business_type: str
    ) -> List[SchemaMarkup]:
        """Generate Service schemas"""
        schemas = []

        if not site_data or not site_data.get("services"):
            return schemas

        parsed_url = urlparse(site_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        for service in site_data.get("services", [])[:5]:  # Top 5 services
            schema = {
                "@context": self.schema_context,
                "@type": "Service",
                "name": service.get("name", ""),
                "provider": {
                    "@type": business_type or "Organization",
                    "name": site_data.get("business_name", parsed_url.netloc)
                },
                "serviceType": service.get("type", service.get("name", "")),
            }

            if service.get("description"):
                schema["description"] = service["description"]

            if service.get("price"):
                schema["offers"] = {
                    "@type": "Offer",
                    "price": service["price"],
                    "priceCurrency": "USD"
                }

            if service.get("area_served"):
                schema["areaServed"] = service["area_served"]

            validation = self._validate_schema(schema, "Service")
            html_snippet = self._create_html_snippet(schema)

            schemas.append(SchemaMarkup(
                schema_type="Service",
                json_ld=schema,
                html_snippet=html_snippet,
                validation_status=validation["status"],
                validation_messages=validation["messages"],
                rich_snippet_eligible=validation["rich_snippet_eligible"],
                implementation_instructions=self._get_implementation_instructions("Service")
            ))

        return schemas

    async def _generate_product_schemas(
        self,
        site_url: str,
        site_data: Optional[Dict]
    ) -> List[SchemaMarkup]:
        """Generate Product schemas"""
        schemas = []

        if not site_data or not site_data.get("products"):
            return schemas

        for product in site_data.get("products", [])[:5]:  # Top 5 products
            schema = {
                "@context": self.schema_context,
                "@type": "Product",
                "name": product.get("name", ""),
            }

            if product.get("description"):
                schema["description"] = product["description"]

            if product.get("image"):
                schema["image"] = product["image"]

            if product.get("brand"):
                schema["brand"] = {
                    "@type": "Brand",
                    "name": product["brand"]
                }

            if product.get("price"):
                schema["offers"] = {
                    "@type": "Offer",
                    "price": product["price"],
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock"
                }

            if product.get("rating"):
                schema["aggregateRating"] = {
                    "@type": "AggregateRating",
                    "ratingValue": product["rating"],
                    "reviewCount": product.get("review_count", 0)
                }

            validation = self._validate_schema(schema, "Product")
            html_snippet = self._create_html_snippet(schema)

            schemas.append(SchemaMarkup(
                schema_type="Product",
                json_ld=schema,
                html_snippet=html_snippet,
                validation_status=validation["status"],
                validation_messages=validation["messages"],
                rich_snippet_eligible=validation["rich_snippet_eligible"],
                implementation_instructions=self._get_implementation_instructions("Product")
            ))

        return schemas

    async def _generate_faq_schema(
        self,
        site_url: str,
        site_data: Optional[Dict]
    ) -> Optional[SchemaMarkup]:
        """Generate FAQ schema"""
        if not site_data or not site_data.get("faqs"):
            return None

        faqs = site_data.get("faqs", [])
        if not faqs:
            return None

        schema = {
            "@context": self.schema_context,
            "@type": "FAQPage",
            "mainEntity": []
        }

        for faq in faqs[:10]:  # Max 10 FAQs
            if faq.get("question") and faq.get("answer"):
                schema["mainEntity"].append({
                    "@type": "Question",
                    "name": faq["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq["answer"]
                    }
                })

        if not schema["mainEntity"]:
            return None

        validation = self._validate_schema(schema, "FAQPage")
        html_snippet = self._create_html_snippet(schema)

        return SchemaMarkup(
            schema_type="FAQPage",
            json_ld=schema,
            html_snippet=html_snippet,
            validation_status=validation["status"],
            validation_messages=validation["messages"],
            rich_snippet_eligible=validation["rich_snippet_eligible"],
            implementation_instructions=self._get_implementation_instructions("FAQ")
        )

    async def _generate_breadcrumb_schema(
        self,
        site_url: str,
        site_data: Optional[Dict]
    ) -> Optional[SchemaMarkup]:
        """Generate BreadcrumbList schema"""
        if not site_data or not site_data.get("breadcrumbs"):
            return None

        breadcrumbs = site_data.get("breadcrumbs", [])
        if not breadcrumbs:
            return None

        parsed_url = urlparse(site_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        schema = {
            "@context": self.schema_context,
            "@type": "BreadcrumbList",
            "itemListElement": []
        }

        for idx, crumb in enumerate(breadcrumbs, 1):
            schema["itemListElement"].append({
                "@type": "ListItem",
                "position": idx,
                "name": crumb.get("name", ""),
                "item": urljoin(base_url, crumb.get("url", ""))
            })

        validation = self._validate_schema(schema, "BreadcrumbList")
        html_snippet = self._create_html_snippet(schema)

        return SchemaMarkup(
            schema_type="BreadcrumbList",
            json_ld=schema,
            html_snippet=html_snippet,
            validation_status=validation["status"],
            validation_messages=validation["messages"],
            rich_snippet_eligible=validation["rich_snippet_eligible"],
            implementation_instructions=self._get_implementation_instructions("BreadcrumbList")
        )

    def _format_address(self, address: Any) -> Dict:
        """Format address for schema"""
        if isinstance(address, dict):
            return {
                "@type": "PostalAddress",
                "streetAddress": address.get("street", ""),
                "addressLocality": address.get("city", ""),
                "addressRegion": address.get("state", ""),
                "postalCode": address.get("zip", ""),
                "addressCountry": address.get("country", "US")
            }

        # Try to parse string address
        if isinstance(address, str):
            return {
                "@type": "PostalAddress",
                "streetAddress": address
            }

        return {
            "@type": "PostalAddress",
            "streetAddress": str(address)
        }

    def _format_hours(self, hours: Any) -> List[Dict]:
        """Format hours of operation for schema"""
        if isinstance(hours, list):
            return hours

        if isinstance(hours, str):
            # Try to parse common formats
            # e.g., "Mon-Fri: 9am-5pm"
            return [{
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "09:00",
                "closes": "17:00"
            }]

        return []

    def _validate_schema(self, schema: Dict, schema_type: str) -> Dict:
        """Validate schema markup"""
        messages = []
        status = "valid"
        rich_snippet_eligible = True

        # Check required fields by schema type
        required_fields = {
            "Organization": ["name", "url"],
            "LocalBusiness": ["name", "address"],
            "Service": ["name", "provider"],
            "Product": ["name", "offers"],
            "FAQPage": ["mainEntity"],
            "BreadcrumbList": ["itemListElement"]
        }

        for field in required_fields.get(schema_type, []):
            if field not in schema or not schema[field]:
                messages.append(f"Missing required field: {field}")
                status = "error"
                rich_snippet_eligible = False

        # Check recommended fields
        recommended_fields = {
            "Organization": ["description", "logo", "telephone"],
            "LocalBusiness": ["description", "image", "telephone", "openingHoursSpecification"],
            "Service": ["description", "areaServed"],
            "Product": ["description", "image", "aggregateRating"],
            "FAQPage": [],
            "BreadcrumbList": []
        }

        for field in recommended_fields.get(schema_type, []):
            if field not in schema or not schema[field]:
                messages.append(f"Recommended field missing: {field}")
                if status == "valid":
                    status = "warning"

        # LocalBusiness specific validation
        if schema_type in ["LocalBusiness", "Plumber", "Electrician", "Restaurant"]:
            if "address" not in schema:
                messages.append("Address is critical for local business schema")
                status = "error"
                rich_snippet_eligible = False

            if "telephone" not in schema:
                messages.append("Phone number recommended for local businesses")
                if status == "valid":
                    status = "warning"

        if not messages:
            messages.append("Schema markup is valid and complete")

        return {
            "status": status,
            "messages": messages,
            "rich_snippet_eligible": rich_snippet_eligible
        }

    def _create_html_snippet(self, schema: Dict) -> str:
        """Create copy-paste ready HTML snippet"""
        json_str = json.dumps(schema, indent=2, ensure_ascii=False)

        return f'''<script type="application/ld+json">
{json_str}
</script>'''

    def _get_implementation_instructions(self, schema_type: str) -> str:
        """Get implementation instructions for schema type"""
        instructions = {
            "Organization": """
**Implementation Instructions:**

1. Copy the JSON-LD code above
2. Paste it in your website's <head> section, before the closing </head> tag
3. Place it on your homepage for maximum effect
4. Test using Google's Rich Results Test: https://search.google.com/test/rich-results

**Best Practices:**
- Keep organization schema on every page
- Ensure name and URL match exactly across all pages
- Update logo and social profiles regularly
""",
            "LocalBusiness": """
**Implementation Instructions:**

1. Copy the JSON-LD code above
2. Paste it in your website's <head> section
3. Place it on your homepage and contact page
4. Ensure NAP (Name, Address, Phone) matches Google Business Profile exactly
5. Test using Google's Rich Results Test: https://search.google.com/test/rich-results

**Best Practices:**
- Keep address format consistent across all citations
- Add opening hours for better local visibility
- Include service area if you serve multiple locations
- Add photos and logo for rich snippets
""",
            "Service": """
**Implementation Instructions:**

1. Copy the JSON-LD code above
2. Paste it in the <head> section of your service pages
3. Create one schema per service offering
4. Link to your organization schema via provider field
5. Test using Google's Rich Results Test

**Best Practices:**
- Be specific with service descriptions
- Include pricing if possible
- Add service area for local services
- Update regularly as services change
""",
            "Product": """
**Implementation Instructions:**

1. Copy the JSON-LD code above
2. Paste it in the <head> section of product pages
3. One schema per product
4. Ensure price and availability are current
5. Test using Google's Rich Results Test

**Best Practices:**
- Include high-quality images
- Add reviews and ratings when available
- Keep prices up to date
- Specify availability status
- Add brand information
""",
            "FAQ": """
**Implementation Instructions:**

1. Copy the JSON-LD code above
2. Paste it in the <head> section of FAQ pages
3. Ensure questions and answers are visible on the page
4. Test using Google's Rich Results Test

**Best Practices:**
- Minimum 2 FAQs, maximum 10 per page
- Keep answers concise (under 300 words)
- Use natural question phrasing
- Ensure FAQ content matches schema exactly
""",
            "BreadcrumbList": """
**Implementation Instructions:**

1. Copy the JSON-LD code above
2. Paste it in the <head> section of all pages with breadcrumbs
3. Ensure breadcrumb trail is visible on page
4. Test using Google's Rich Results Test

**Best Practices:**
- Start with homepage (position 1)
- Include current page as last item
- Keep URLs absolute, not relative
- Match visible breadcrumb trail exactly
"""
        }

        return instructions.get(schema_type, "Copy and paste into your website's <head> section.")

    def _generate_schema_recommendations(
        self,
        schemas: List[SchemaMarkup],
        business_type: str,
        site_data: Optional[Dict]
    ) -> List[str]:
        """Generate recommendations for schema implementation"""
        recommendations = []

        # Check what's missing
        schema_types_generated = {s.schema_type for s in schemas}

        if "Organization" not in schema_types_generated and "LocalBusiness" not in schema_types_generated:
            recommendations.append(
                "Add Organization or LocalBusiness schema to establish your entity"
            )

        if business_type in ["Plumber", "Electrician", "Restaurant"] and "LocalBusiness" not in schema_types_generated:
            recommendations.append(
                f"Add LocalBusiness schema - critical for {business_type} businesses"
            )

        if site_data:
            if site_data.get("services") and "Service" not in schema_types_generated:
                recommendations.append(
                    "Add Service schema to highlight your offerings"
                )

            if site_data.get("products") and "Product" not in schema_types_generated:
                recommendations.append(
                    "Add Product schema to enable rich product snippets"
                )

            if site_data.get("faqs") and "FAQPage" not in schema_types_generated:
                recommendations.append(
                    "Add FAQ schema to appear in FAQ rich results"
                )

        # Check for validation issues
        for schema in schemas:
            if schema.validation_status == "error":
                recommendations.append(
                    f"Fix validation errors in {schema.schema_type} schema"
                )
            elif schema.validation_status == "warning":
                recommendations.append(
                    f"Add recommended fields to {schema.schema_type} schema for better results"
                )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "Excellent! All recommended schemas are in place and valid"
            )
            recommendations.append(
                "Test all schemas using Google Rich Results Test"
            )
            recommendations.append(
                "Monitor Google Search Console for rich result performance"
            )

        return recommendations
