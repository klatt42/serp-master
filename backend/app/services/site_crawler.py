"""
Site Crawler Service
Manages website crawling using DataForSEO On-Page API
Handles crawl lifecycle: initiate -> poll for completion -> retrieve results
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from urllib.parse import urlparse

from .dataforseo_client import DataForSEOClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SiteCrawler:
    """
    Manages website crawling operations using DataForSEO
    Handles the complete crawl lifecycle with status polling
    """

    def __init__(self):
        """Initialize the site crawler with DataForSEO client"""
        self.client = DataForSEOClient()
        self.poll_interval = 10  # seconds - faster polling to catch tasks before expiry
        self.max_poll_time = 600  # 10 minutes max wait
        logger.info("Site crawler initialized")

    def _validate_url(self, url: str) -> str:
        """
        Validate and normalize URL

        Args:
            url: Website URL to validate

        Returns:
            Normalized URL

        Raises:
            ValueError: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        # Parse URL to validate
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError("Invalid URL: no domain found")

            # Normalize URL
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            logger.info(f"Normalized URL: {normalized}")
            return normalized

        except Exception as e:
            raise ValueError(f"Invalid URL format: {str(e)}")

    async def crawl_site(
        self,
        url: str,
        max_pages: int = 100
    ) -> Dict[str, Any]:
        """
        Crawl a website and return comprehensive SEO data

        This is the main method that orchestrates the entire crawl process:
        1. Validate URL
        2. Initiate crawl
        3. Poll for completion
        4. Retrieve and parse results

        Args:
            url: Website URL to crawl
            max_pages: Maximum number of pages to crawl (default 100)

        Returns:
            Parsed crawl results with SEO metrics

        Raises:
            ValueError: If URL is invalid
            Exception: If crawl fails
        """
        start_time = datetime.now()

        try:
            # Validate URL
            validated_url = self._validate_url(url)
            logger.info(f"Starting crawl for {validated_url} (max {max_pages} pages)")

            # Step 1: Initiate crawl
            task_response = await self.client.task_post(validated_url, max_pages)

            if not task_response.get("tasks") or len(task_response["tasks"]) == 0:
                raise Exception("Failed to create crawl task")

            task_data = task_response["tasks"][0]
            task_id = task_data.get("id")

            if not task_id:
                raise Exception("No task ID returned from API")

            if task_data.get("status_code") != 20100:
                status_msg = task_data.get("status_message", "Unknown error")
                raise Exception(f"Task creation failed: {status_msg}")

            logger.info(f"Crawl task created with ID: {task_id}")

            # Step 2: Poll for completion
            status = await self._poll_for_completion(task_id)

            if status != "complete":
                raise Exception(f"Crawl did not complete successfully: {status}")

            # Step 3: Retrieve results
            # Note: /pages/ endpoint may 404 if crawl completed with 0 pages
            # In that case, get data from /summary/ instead
            try:
                results = await self.client.task_get(task_id)
                logger.info("Retrieved crawl data from /pages/ endpoint")
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg:
                    logger.warning(f"/pages/ endpoint returned 404, using /summary/ data instead")
                    # Get summary data instead
                    results = await self.client.task_status(task_id)
                    logger.info("Retrieved crawl data from /summary/ endpoint (0 pages crawled)")
                else:
                    raise

            # Step 4: Parse results
            parsed_results = await self._parse_results(results)

            # Add metadata
            duration = (datetime.now() - start_time).total_seconds()
            parsed_results["metadata"] = {
                "task_id": task_id,
                "target_url": validated_url,
                "max_pages": max_pages,
                "crawl_duration_seconds": duration,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Crawl completed in {duration:.1f} seconds")

            return parsed_results

        except Exception as e:
            logger.error(f"Crawl failed: {str(e)}")
            raise

    async def get_crawl_status(self, task_id: str) -> str:
        """
        Get the current status of a crawl task

        Args:
            task_id: DataForSEO task ID

        Returns:
            Status string: "crawling", "processing", "complete", "failed"

        Raises:
            Exception: If status check fails
        """
        try:
            # Use task_status() method which uses /summary/ endpoint
            # This works during crawling, unlike /pages/ which only works when done
            try:
                result = await self.client.task_status(task_id)

                if result.get("tasks") and len(result["tasks"]) > 0:
                    task = result["tasks"][0]

                    # Check if task has results
                    if task.get("result") and len(task["result"]) > 0:
                        crawl_result = task["result"][0]
                        progress = crawl_result.get("crawl_progress", "unknown")

                        # Get crawl status (contains actual page counts)
                        crawl_status = crawl_result.get("crawl_status", {})
                        pages_done = crawl_status.get("pages_crawled", 0)
                        pages_queued = crawl_status.get("pages_in_queue", 0)

                        if progress == "finished":
                            logger.info(f"Crawl finished! Pages crawled: {pages_done}")
                            return "complete"
                        elif progress in ["in_progress", "in_queue"]:
                            logger.info(f"Crawling: {pages_done} done, {pages_queued} in queue")
                            return "crawling"
                        else:
                            # Has results but unknown progress - consider complete
                            logger.info(f"Unknown progress '{progress}', treating as complete")
                            return "complete"

                    # Task exists but no results yet
                    logger.info("Task has no results yet")
                    return "crawling"

            except Exception as direct_error:
                error_msg = str(direct_error)

                # Check for in-progress status markers
                if "TASK_IN_QUEUE" in error_msg or "TASK_IN_PROGRESS" in error_msg:
                    logger.info("Task is still queued/processing")
                    return "crawling"

                # 404 means task not ready yet (common during initial crawl setup)
                if "404" in error_msg:
                    logger.info("Task not ready yet (404) - still setting up crawl")
                    return "crawling"

                # Other error - actual failure
                logger.error(f"Error checking task status: {direct_error}")
                return "failed"

            return "crawling"

        except Exception as e:
            logger.error(f"Failed to get crawl status: {str(e)}")
            return "failed"

    async def _poll_for_completion(self, task_id: str) -> str:
        """
        Poll DataForSEO API until task is complete

        Args:
            task_id: Task ID to poll

        Returns:
            Status: "complete" or "failed"

        Raises:
            Exception: If polling times out
        """
        start_time = datetime.now()
        poll_count = 0

        logger.info(f"Polling for task {task_id} completion (max {self.max_poll_time}s)")

        while True:
            elapsed = (datetime.now() - start_time).total_seconds()

            # Check timeout
            if elapsed > self.max_poll_time:
                raise Exception(f"Crawl timeout after {elapsed:.1f} seconds")

            poll_count += 1
            logger.info(f"Poll #{poll_count} - checking task status...")

            # Check if task is ready
            status = await self.get_crawl_status(task_id)

            if status == "complete":
                logger.info(f"Task completed after {elapsed:.1f}s ({poll_count} polls)")
                return "complete"

            if status == "failed":
                return "failed"

            # Wait before next poll
            logger.info(f"Task still crawling, waiting {self.poll_interval}s...")
            await asyncio.sleep(self.poll_interval)

    async def _parse_results(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse DataForSEO crawl results into structured SEO data

        Args:
            raw_data: Raw API response from task_get

        Returns:
            Parsed and structured SEO data

        Example structure:
            {
                "summary": {
                    "pages_crawled": 50,
                    "pages_with_issues": 15
                },
                "pages": [...],
                "technical_seo": {...},
                "onpage_seo": {...},
                "structure": {...}
            }
        """
        try:
            if not raw_data.get("tasks") or len(raw_data["tasks"]) == 0:
                raise Exception("No task data in response")

            task_data = raw_data["tasks"][0]

            if not task_data.get("result") or len(task_data["result"]) == 0:
                raise Exception("No results in task data")

            result = task_data["result"][0]

            # Extract summary info - handle both /summary/ and /pages/ endpoints
            # /pages/ has pages_crawled at top level
            # /summary/ has it in crawl_status object
            crawl_status = result.get("crawl_status", {})
            pages_crawled = crawl_status.get("pages_crawled", result.get("pages_crawled", 0))
            pages_in_queue = crawl_status.get("pages_in_queue", result.get("pages_in_queue", 0))
            crawl_progress = result.get("crawl_progress", "unknown")

            logger.info(f"Parsing results for {pages_crawled} pages")

            # Get page items (only available from /pages/ endpoint)
            items = result.get("items", [])

            # Parse page data
            pages = []
            technical_issues = []
            onpage_issues = []
            structure_issues = []

            for item in items:
                page_data = self._parse_page(item)
                pages.append(page_data)

                # Collect issues
                if page_data.get("issues"):
                    for issue in page_data["issues"]:
                        if issue["category"] == "technical":
                            technical_issues.append(issue)
                        elif issue["category"] == "onpage":
                            onpage_issues.append(issue)
                        elif issue["category"] == "structure":
                            structure_issues.append(issue)

            # Build structured result
            parsed = {
                "summary": {
                    "pages_crawled": pages_crawled,
                    "pages_in_queue": pages_in_queue,
                    "crawl_progress": crawl_progress,
                    "pages_with_issues": sum(1 for p in pages if p.get("issues")),
                    "total_issues": len(technical_issues) + len(onpage_issues) + len(structure_issues)
                },
                "pages": pages,
                "issues": {
                    "technical": technical_issues,
                    "onpage": onpage_issues,
                    "structure": structure_issues
                },
                "raw_result": result  # Keep raw data for debugging
            }

            return parsed

        except Exception as e:
            logger.error(f"Failed to parse results: {str(e)}")
            raise

    def _parse_page(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse individual page data from crawl results

        Args:
            item: Page item from DataForSEO results

        Returns:
            Structured page data
        """
        page_data = {
            "url": item.get("url", ""),
            "status_code": item.get("status_code"),
            "page_timing": item.get("page_timing", {}),
            "meta": {
                "title": item.get("meta", {}).get("title", ""),
                "description": item.get("meta", {}).get("description", ""),
                "h1": item.get("meta", {}).get("htags", {}).get("h1", []),
                "canonical": item.get("meta", {}).get("canonical", "")
            },
            "page_metrics": {
                "size": item.get("size", 0),
                "encoded_size": item.get("encoded_size", 0),
                "load_time_ms": item.get("page_timing", {}).get("time_to_interactive", 0),
                "dom_complete": item.get("page_timing", {}).get("dom_complete", 0)
            },
            "checks": item.get("checks", {}),
            "content_encoding": item.get("content_encoding", ""),
            "media_type": item.get("media_type", ""),
            "is_https": item.get("url", "").startswith("https://"),
            "resource_issues": item.get("resource_errors", {}),
            "issues": []
        }

        # Detect issues for this page
        self._detect_page_issues(page_data, item)

        return page_data

    def _detect_page_issues(self, page_data: Dict[str, Any], raw_item: Dict[str, Any]) -> None:
        """
        Detect SEO issues on a page and add to page_data["issues"]

        Args:
            page_data: Structured page data
            raw_item: Raw page item from API
        """
        issues = []

        # Technical issues
        if not page_data["is_https"]:
            issues.append({
                "category": "technical",
                "severity": "critical",
                "issue": "Page not using HTTPS",
                "url": page_data["url"]
            })

        if page_data["page_metrics"]["load_time_ms"] > 5000:
            issues.append({
                "category": "technical",
                "severity": "warning",
                "issue": f"Slow page load time ({page_data['page_metrics']['load_time_ms']}ms)",
                "url": page_data["url"]
            })

        # On-page issues
        if not page_data["meta"]["title"]:
            issues.append({
                "category": "onpage",
                "severity": "critical",
                "issue": "Missing title tag",
                "url": page_data["url"]
            })

        if not page_data["meta"]["description"]:
            issues.append({
                "category": "onpage",
                "severity": "warning",
                "issue": "Missing meta description",
                "url": page_data["url"]
            })

        if not page_data["meta"]["h1"] or len(page_data["meta"]["h1"]) == 0:
            issues.append({
                "category": "onpage",
                "severity": "warning",
                "issue": "Missing H1 tag",
                "url": page_data["url"]
            })

        page_data["issues"] = issues


# Test function
async def test_crawler():
    """Test the site crawler"""
    crawler = SiteCrawler()

    # Test with a small crawl
    print("Starting test crawl...")
    try:
        results = await crawler.crawl_site("example.com", max_pages=5)
        print(f"\nCrawl completed!")
        print(f"Pages crawled: {results['summary']['pages_crawled']}")
        print(f"Issues found: {results['summary']['total_issues']}")
        print(f"Duration: {results['metadata']['crawl_duration_seconds']:.1f}s")

    except Exception as e:
        print(f"Crawl failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_crawler())
