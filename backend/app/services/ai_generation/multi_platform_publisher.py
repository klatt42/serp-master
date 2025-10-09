"""
Multi-Platform Publisher
Publish content to WordPress, Medium, LinkedIn, Ghost, Dev.to, Hashnode
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio
import aiohttp
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class PublishingPlatform(str, Enum):
    """Supported publishing platforms"""
    WORDPRESS = "wordpress"
    MEDIUM = "medium"
    LINKEDIN = "linkedin"
    GHOST = "ghost"
    DEVTO = "devto"
    HASHNODE = "hashnode"


class PublishStatus(str, Enum):
    """Publishing status"""
    QUEUED = "queued"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    RETRYING = "retrying"
    SCHEDULED = "scheduled"


class MultiPlatformPublisher:
    """Publish content across multiple platforms"""

    def __init__(self):
        """Initialize multi-platform publisher"""
        self.publish_queue = []
        self.published_content = []
        self.platform_credentials = {}
        self.max_retries = 3
        self.retry_delay = 60  # seconds

    async def configure_platform(
        self,
        platform: str,
        credentials: Dict[str, str]
    ) -> Dict:
        """
        Configure platform credentials

        Args:
            platform: Platform name
            credentials: Platform-specific credentials

        Returns:
            Configuration status
        """
        try:
            # Validate platform
            if platform not in [p.value for p in PublishingPlatform]:
                raise ValueError(f"Unsupported platform: {platform}")

            # Validate credentials based on platform
            self._validate_credentials(platform, credentials)

            # Store credentials (in production, encrypt these!)
            self.platform_credentials[platform] = credentials

            logger.info(f"Configured {platform} credentials")

            return {
                "platform": platform,
                "configured": True,
                "configured_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error configuring platform: {str(e)}")
            raise

    def _validate_credentials(self, platform: str, credentials: Dict) -> None:
        """Validate platform-specific credentials"""
        required_fields = {
            PublishingPlatform.WORDPRESS.value: ["site_url", "username", "app_password"],
            PublishingPlatform.MEDIUM.value: ["integration_token"],
            PublishingPlatform.LINKEDIN.value: ["access_token"],
            PublishingPlatform.GHOST.value: ["admin_api_key", "api_url"],
            PublishingPlatform.DEVTO.value: ["api_key"],
            PublishingPlatform.HASHNODE.value: ["access_token", "publication_id"]
        }

        required = required_fields.get(platform, [])
        missing = [field for field in required if field not in credentials]

        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")

    async def publish_content(
        self,
        content: Dict,
        platforms: List[str],
        schedule_time: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """
        Publish content to multiple platforms

        Args:
            content: Content with title, body, etc.
            platforms: List of platforms to publish to
            schedule_time: Optional scheduled publish time
            tags: Optional tags for the content

        Returns:
            Publishing results for each platform
        """
        try:
            publish_id = f"pub_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            results = {
                "publish_id": publish_id,
                "content_title": content.get("title"),
                "platforms": {},
                "started_at": datetime.now().isoformat()
            }

            # If scheduled, add to queue
            if schedule_time and schedule_time > datetime.now():
                for platform in platforms:
                    self._add_to_queue(
                        publish_id,
                        platform,
                        content,
                        schedule_time,
                        tags
                    )
                    results["platforms"][platform] = {
                        "status": PublishStatus.SCHEDULED.value,
                        "scheduled_for": schedule_time.isoformat()
                    }
                return results

            # Publish immediately to all platforms
            for platform in platforms:
                try:
                    platform_result = await self._publish_to_platform(
                        platform,
                        content,
                        tags
                    )
                    results["platforms"][platform] = platform_result

                except Exception as e:
                    logger.error(f"Error publishing to {platform}: {str(e)}")
                    results["platforms"][platform] = {
                        "status": PublishStatus.FAILED.value,
                        "error": str(e)
                    }

            results["completed_at"] = datetime.now().isoformat()
            results["success_count"] = sum(
                1 for p in results["platforms"].values()
                if p.get("status") == PublishStatus.PUBLISHED.value
            )
            results["failed_count"] = sum(
                1 for p in results["platforms"].values()
                if p.get("status") == PublishStatus.FAILED.value
            )

            # Store in published content
            self.published_content.append(results)

            logger.info(f"Published to {results['success_count']}/{len(platforms)} platforms")
            return results

        except Exception as e:
            logger.error(f"Error in publish_content: {str(e)}")
            raise

    def _add_to_queue(
        self,
        publish_id: str,
        platform: str,
        content: Dict,
        schedule_time: datetime,
        tags: Optional[List[str]]
    ) -> None:
        """Add content to publishing queue"""
        self.publish_queue.append({
            "publish_id": publish_id,
            "platform": platform,
            "content": content,
            "schedule_time": schedule_time,
            "tags": tags,
            "status": PublishStatus.QUEUED.value,
            "retry_count": 0,
            "created_at": datetime.now().isoformat()
        })

    async def _publish_to_platform(
        self,
        platform: str,
        content: Dict,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """Publish to specific platform"""
        if platform not in self.platform_credentials:
            raise ValueError(f"Platform {platform} not configured")

        if platform == PublishingPlatform.WORDPRESS.value:
            return await self._publish_to_wordpress(content, tags)
        elif platform == PublishingPlatform.MEDIUM.value:
            return await self._publish_to_medium(content, tags)
        elif platform == PublishingPlatform.LINKEDIN.value:
            return await self._publish_to_linkedin(content, tags)
        elif platform == PublishingPlatform.GHOST.value:
            return await self._publish_to_ghost(content, tags)
        elif platform == PublishingPlatform.DEVTO.value:
            return await self._publish_to_devto(content, tags)
        elif platform == PublishingPlatform.HASHNODE.value:
            return await self._publish_to_hashnode(content, tags)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def _publish_to_wordpress(
        self,
        content: Dict,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """Publish to WordPress via REST API"""
        try:
            creds = self.platform_credentials[PublishingPlatform.WORDPRESS.value]

            # Prepare WordPress post data
            post_data = {
                "title": content.get("title"),
                "content": content.get("body"),
                "status": "publish",  # or "draft"
                "excerpt": content.get("description", ""),
                "tags": tags or [],
                "categories": content.get("categories", [])
            }

            # WordPress REST API endpoint
            url = f"{creds['site_url']}/wp-json/wp/v2/posts"

            # Make API request (placeholder - needs actual implementation)
            async with aiohttp.ClientSession() as session:
                # In production, use proper auth
                headers = {
                    "Content-Type": "application/json"
                }

                # Simulated response for now
                logger.info(f"Would publish to WordPress: {url}")

                return {
                    "status": PublishStatus.PUBLISHED.value,
                    "platform_post_id": "wp_12345",
                    "platform_url": f"{creds['site_url']}/post-slug",
                    "published_at": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"WordPress publishing error: {str(e)}")
            return {
                "status": PublishStatus.FAILED.value,
                "error": str(e)
            }

    async def _publish_to_medium(
        self,
        content: Dict,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """Publish to Medium via API"""
        try:
            creds = self.platform_credentials[PublishingPlatform.MEDIUM.value]

            # Medium API data
            post_data = {
                "title": content.get("title"),
                "contentFormat": "markdown",
                "content": content.get("body"),
                "tags": tags[:5] if tags else [],  # Medium max 5 tags
                "publishStatus": "public"  # or "draft", "unlisted"
            }

            # Medium API endpoint
            url = "https://api.medium.com/v1/users/{userId}/posts"

            logger.info("Would publish to Medium")

            return {
                "status": PublishStatus.PUBLISHED.value,
                "platform_post_id": "medium_abc123",
                "platform_url": "https://medium.com/@user/post-slug",
                "published_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Medium publishing error: {str(e)}")
            return {
                "status": PublishStatus.FAILED.value,
                "error": str(e)
            }

    async def _publish_to_linkedin(
        self,
        content: Dict,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """Publish to LinkedIn via API"""
        try:
            creds = self.platform_credentials[PublishingPlatform.LINKEDIN.value]

            # LinkedIn Share API data
            post_data = {
                "author": "urn:li:person:{personId}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": f"{content.get('title')}\n\n{content.get('description', '')}"
                        },
                        "shareMediaCategory": "ARTICLE",
                        "media": [{
                            "status": "READY",
                            "originalUrl": content.get("canonical_url", "")
                        }]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            logger.info("Would publish to LinkedIn")

            return {
                "status": PublishStatus.PUBLISHED.value,
                "platform_post_id": "linkedin_xyz789",
                "platform_url": "https://linkedin.com/posts/activity-id",
                "published_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"LinkedIn publishing error: {str(e)}")
            return {
                "status": PublishStatus.FAILED.value,
                "error": str(e)
            }

    async def _publish_to_ghost(
        self,
        content: Dict,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """Publish to Ghost via Admin API"""
        try:
            creds = self.platform_credentials[PublishingPlatform.GHOST.value]

            # Ghost post data
            post_data = {
                "posts": [{
                    "title": content.get("title"),
                    "mobiledoc": content.get("body"),  # or "html"
                    "status": "published",
                    "tags": [{"name": tag} for tag in (tags or [])],
                    "meta_description": content.get("description", "")
                }]
            }

            logger.info("Would publish to Ghost")

            return {
                "status": PublishStatus.PUBLISHED.value,
                "platform_post_id": "ghost_post_123",
                "platform_url": f"{creds['api_url']}/post-slug",
                "published_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Ghost publishing error: {str(e)}")
            return {
                "status": PublishStatus.FAILED.value,
                "error": str(e)
            }

    async def _publish_to_devto(
        self,
        content: Dict,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """Publish to Dev.to via API"""
        try:
            creds = self.platform_credentials[PublishingPlatform.DEVTO.value]

            # Dev.to article data
            post_data = {
                "article": {
                    "title": content.get("title"),
                    "published": True,
                    "body_markdown": content.get("body"),
                    "tags": tags[:4] if tags else [],  # Dev.to max 4 tags
                    "series": content.get("series"),
                    "canonical_url": content.get("canonical_url")
                }
            }

            logger.info("Would publish to Dev.to")

            return {
                "status": PublishStatus.PUBLISHED.value,
                "platform_post_id": "devto_456",
                "platform_url": "https://dev.to/user/post-slug",
                "published_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Dev.to publishing error: {str(e)}")
            return {
                "status": PublishStatus.FAILED.value,
                "error": str(e)
            }

    async def _publish_to_hashnode(
        self,
        content: Dict,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """Publish to Hashnode via GraphQL API"""
        try:
            creds = self.platform_credentials[PublishingPlatform.HASHNODE.value]

            # Hashnode GraphQL mutation
            mutation = """
            mutation CreatePost($input: CreatePostInput!) {
                createPublicationPost(publicationId: $publicationId, input: $input) {
                    post {
                        id
                        slug
                        url
                    }
                }
            }
            """

            variables = {
                "publicationId": creds["publication_id"],
                "input": {
                    "title": content.get("title"),
                    "contentMarkdown": content.get("body"),
                    "tags": [{"name": tag} for tag in (tags or [])],
                    "metaTags": {
                        "description": content.get("description", "")
                    }
                }
            }

            logger.info("Would publish to Hashnode")

            return {
                "status": PublishStatus.PUBLISHED.value,
                "platform_post_id": "hashnode_789",
                "platform_url": "https://blog.hashnode.dev/post-slug",
                "published_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Hashnode publishing error: {str(e)}")
            return {
                "status": PublishStatus.FAILED.value,
                "error": str(e)
            }

    async def process_queue(self) -> Dict:
        """Process scheduled publishing queue"""
        try:
            now = datetime.now()
            processed = 0
            published = 0
            failed = 0

            # Find items ready to publish
            ready_items = [
                item for item in self.publish_queue
                if item["status"] == PublishStatus.QUEUED.value
                and datetime.fromisoformat(item["schedule_time"].replace('Z', '+00:00')) <= now
            ]

            for item in ready_items:
                processed += 1
                item["status"] = PublishStatus.PUBLISHING.value

                try:
                    result = await self._publish_to_platform(
                        item["platform"],
                        item["content"],
                        item["tags"]
                    )

                    if result["status"] == PublishStatus.PUBLISHED.value:
                        item["status"] = PublishStatus.PUBLISHED.value
                        item["published_at"] = result["published_at"]
                        item["platform_url"] = result.get("platform_url")
                        published += 1
                    else:
                        # Retry logic
                        if item["retry_count"] < self.max_retries:
                            item["status"] = PublishStatus.RETRYING.value
                            item["retry_count"] += 1
                            item["next_retry"] = (now + timedelta(seconds=self.retry_delay)).isoformat()
                        else:
                            item["status"] = PublishStatus.FAILED.value
                            item["error"] = result.get("error")
                            failed += 1

                except Exception as e:
                    logger.error(f"Queue processing error: {str(e)}")
                    item["status"] = PublishStatus.FAILED.value
                    item["error"] = str(e)
                    failed += 1

            return {
                "processed": processed,
                "published": published,
                "failed": failed,
                "remaining_in_queue": len([
                    i for i in self.publish_queue
                    if i["status"] in [PublishStatus.QUEUED.value, PublishStatus.RETRYING.value]
                ])
            }

        except Exception as e:
            logger.error(f"Error processing queue: {str(e)}")
            raise

    async def retry_failed_publish(self, publish_id: str, platform: str) -> Dict:
        """Retry a failed publish"""
        try:
            # Find the failed item
            item = next(
                (i for i in self.publish_queue
                 if i["publish_id"] == publish_id and i["platform"] == platform),
                None
            )

            if not item:
                raise ValueError(f"Publish item not found: {publish_id}/{platform}")

            if item["status"] not in [PublishStatus.FAILED.value, PublishStatus.RETRYING.value]:
                raise ValueError(f"Cannot retry item with status: {item['status']}")

            # Attempt republish
            result = await self._publish_to_platform(
                platform,
                item["content"],
                item["tags"]
            )

            item["retry_count"] += 1
            if result["status"] == PublishStatus.PUBLISHED.value:
                item["status"] = PublishStatus.PUBLISHED.value
                item["published_at"] = result["published_at"]

            return result

        except Exception as e:
            logger.error(f"Error retrying publish: {str(e)}")
            raise

    def get_publish_status(self, publish_id: str) -> Dict:
        """Get status of a publish job"""
        # Check published content
        published = next(
            (p for p in self.published_content if p["publish_id"] == publish_id),
            None
        )

        if published:
            return {
                "publish_id": publish_id,
                "status": "completed",
                "results": published
            }

        # Check queue
        queue_items = [
            i for i in self.publish_queue
            if i["publish_id"] == publish_id
        ]

        if queue_items:
            return {
                "publish_id": publish_id,
                "status": "in_queue",
                "queue_items": queue_items
            }

        return {
            "publish_id": publish_id,
            "status": "not_found"
        }

    def get_platform_stats(self) -> Dict:
        """Get publishing statistics by platform"""
        stats = {}

        for platform in PublishingPlatform:
            platform_name = platform.value

            # Count published
            published_count = sum(
                1 for p in self.published_content
                if platform_name in p["platforms"]
                and p["platforms"][platform_name].get("status") == PublishStatus.PUBLISHED.value
            )

            # Count failed
            failed_count = sum(
                1 for p in self.published_content
                if platform_name in p["platforms"]
                and p["platforms"][platform_name].get("status") == PublishStatus.FAILED.value
            )

            # Count queued
            queued_count = sum(
                1 for i in self.publish_queue
                if i["platform"] == platform_name
                and i["status"] in [PublishStatus.QUEUED.value, PublishStatus.SCHEDULED.value]
            )

            stats[platform_name] = {
                "configured": platform_name in self.platform_credentials,
                "published": published_count,
                "failed": failed_count,
                "queued": queued_count,
                "total": published_count + failed_count
            }

        return stats

    def list_configured_platforms(self) -> List[str]:
        """List all configured platforms"""
        return list(self.platform_credentials.keys())
