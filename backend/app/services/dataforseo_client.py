"""
DataForSEO API Client
Handles authentication, API requests, rate limiting, and error handling
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
import aiohttp
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataForSEOClient:
    """
    Async client for DataForSEO On-Page API
    Handles authentication, rate limiting, retries, and error handling
    """

    def __init__(self):
        """Initialize the DataForSEO client with credentials from environment"""
        self.login = os.getenv("DATAFORSEO_LOGIN")
        self.password = os.getenv("DATAFORSEO_PASSWORD")
        self.base_url = os.getenv("DATAFORSEO_API_URL", "https://api.dataforseo.com/v3")

        if not self.login or not self.password:
            raise ValueError("DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD must be set in .env")

        # Create auth header
        self.auth_header = self._create_auth_header()

        # Configuration
        self.max_retries = 3
        self.timeout = 30
        self.retry_delay = 2  # seconds

        logger.info("DataForSEO client initialized")

    def _create_auth_header(self) -> str:
        """
        Create Basic Auth header for DataForSEO API
        Returns: Authorization header value
        """
        credentials = f"{self.login}:{self.password}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {b64_credentials}"

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make an async HTTP request to DataForSEO API with retries

        Args:
            method: HTTP method (GET or POST)
            endpoint: API endpoint path
            data: Request payload for POST requests
            retry_count: Current retry attempt number

        Returns:
            API response as dict

        Raises:
            Exception: After max retries or on unrecoverable errors
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=self.timeout)

                if method.upper() == "POST":
                    async with session.post(
                        url,
                        json=data,
                        headers=headers,
                        timeout=timeout
                    ) as response:
                        return await self._handle_response(response, method, endpoint, data, retry_count)

                elif method.upper() == "GET":
                    async with session.get(
                        url,
                        headers=headers,
                        timeout=timeout
                    ) as response:
                        return await self._handle_response(response, method, endpoint, data, retry_count)

                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {endpoint}")
            if retry_count < self.max_retries:
                return await self._retry_request(method, endpoint, data, retry_count)
            raise Exception(f"Request timeout after {self.max_retries} retries")

        except aiohttp.ClientError as e:
            logger.error(f"Client error for {endpoint}: {str(e)}")
            if retry_count < self.max_retries:
                return await self._retry_request(method, endpoint, data, retry_count)
            raise Exception(f"Client error after {self.max_retries} retries: {str(e)}")

    async def _handle_response(
        self,
        response: aiohttp.ClientResponse,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]],
        retry_count: int
    ) -> Dict[str, Any]:
        """
        Handle API response and check for errors

        Args:
            response: aiohttp response object
            method: HTTP method used
            endpoint: API endpoint
            data: Request data
            retry_count: Current retry count

        Returns:
            Parsed JSON response

        Raises:
            Exception: On error responses
        """
        # Handle rate limiting (429)
        if response.status == 429:
            logger.warning(f"Rate limited on {endpoint}, retry {retry_count + 1}/{self.max_retries}")
            if retry_count < self.max_retries:
                await asyncio.sleep(self.retry_delay * (retry_count + 1))  # Exponential backoff
                return await self._retry_request(method, endpoint, data, retry_count)
            raise Exception("Rate limit exceeded after max retries")

        # Handle authentication errors
        if response.status == 401:
            raise Exception("Authentication failed - check DataForSEO credentials")

        # Handle other client errors
        if response.status >= 400 and response.status < 500:
            error_text = await response.text()
            raise Exception(f"Client error {response.status}: {error_text}")

        # Handle server errors with retry
        if response.status >= 500:
            logger.error(f"Server error {response.status} for {endpoint}")
            if retry_count < self.max_retries:
                return await self._retry_request(method, endpoint, data, retry_count)
            raise Exception(f"Server error {response.status} after {self.max_retries} retries")

        # Success - parse JSON
        if response.status == 200:
            try:
                result = await response.json()

                # Check DataForSEO status code in response
                if result.get("status_code") and result["status_code"] >= 40000:
                    logger.error(f"DataForSEO API error: {result.get('status_message')}")
                    raise Exception(f"DataForSEO error: {result.get('status_message')}")

                logger.info(f"Request to {endpoint} successful, cost: ${result.get('cost', 0)}")
                return result

            except Exception as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                raise Exception(f"Invalid JSON response: {str(e)}")

        raise Exception(f"Unexpected status code: {response.status}")

    async def _retry_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]],
        retry_count: int
    ) -> Dict[str, Any]:
        """
        Retry a failed request with exponential backoff

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            retry_count: Current retry count

        Returns:
            API response
        """
        retry_count += 1
        delay = self.retry_delay * retry_count
        logger.info(f"Retrying request to {endpoint} after {delay}s (attempt {retry_count}/{self.max_retries})")
        await asyncio.sleep(delay)
        return await self._make_request(method, endpoint, data, retry_count)

    # ===== On-Page API Methods =====

    async def task_post(self, target_url: str, max_crawl_pages: int = 100) -> Dict[str, Any]:
        """
        Initiate a website crawl task

        Args:
            target_url: Website URL to crawl
            max_crawl_pages: Maximum number of pages to crawl (default 100)

        Returns:
            API response with task_id

        Example response:
            {
                "status_code": 20000,
                "tasks": [{
                    "id": "task_id_here",
                    "status_code": 20100
                }]
            }
        """
        endpoint = "on_page/task_post"

        payload = [{
            "target": target_url,
            "max_crawl_pages": max_crawl_pages,
            "load_resources": False,
            "enable_javascript": True,
            "enable_browser_rendering": False,
            "store_raw_html": False
        }]

        logger.info(f"Initiating crawl for {target_url} (max {max_crawl_pages} pages)")

        try:
            result = await self._make_request("POST", endpoint, payload)

            # Extract task ID from response
            if result.get("tasks") and len(result["tasks"]) > 0:
                task_id = result["tasks"][0].get("id")
                logger.info(f"Crawl task created: {task_id}")
                return result
            else:
                raise Exception("No task ID returned from API")

        except Exception as e:
            logger.error(f"Failed to initiate crawl: {str(e)}")
            raise

    async def tasks_ready(self) -> Dict[str, Any]:
        """
        Check which tasks are ready for retrieval

        IMPORTANT: Task IDs are in the 'result' array, NOT 'tasks' array!
        The top-level 'id' is the API request ID, not a task ID.

        Returns:
            API response with ready tasks in 'result' array

        Example response structure:
            {
                "id": "08071727-1535-0217-0000-1958f65eebb9",  # API request ID (ignore)
                "status_code": 20000,
                "result_count": 106,
                "result": [                                     # Task IDs are HERE
                    {
                        "id": "08041601-1535-0216-0000-fc052fccbb0f",  # Actual task ID
                        "target": "dataforseo.com",
                        "date_posted": "2020-08-04 13:01:21 +00:00",
                        "tag": ""
                    }
                ]
            }

        Usage:
            response = await client.tasks_ready()
            for task in response.get("result", []):  # Use 'result', not 'tasks'
                task_id = task["id"]
        """
        endpoint = "on_page/tasks_ready"

        try:
            result = await self._make_request("GET", endpoint)

            # Task IDs are in 'result' array, not 'tasks'
            ready_count = len(result.get("result", []))
            logger.info(f"Found {ready_count} ready tasks in 'result' array")

            return result

        except Exception as e:
            logger.error(f"Failed to check ready tasks: {str(e)}")
            raise

    async def task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check crawl status using summary endpoint (non-blocking)

        IMPORTANT: Use this for polling status during crawl.
        The /summary/ endpoint is available while crawling and returns status.

        Args:
            task_id: Task ID from task_post

        Returns:
            Status response with crawl_progress

        Example response:
            {
                "status_code": 20000,
                "tasks": [{
                    "id": "task_id",
                    "status_code": 20000,
                    "result": [{
                        "crawl_progress": "in_progress" | "finished",
                        "pages_crawled": 5,
                        "pages_in_queue": 10
                    }]
                }]
            }
        """
        endpoint = f"on_page/summary/{task_id}"
        logger.info(f"Checking crawl status for task {task_id} via summary endpoint")

        try:
            result = await self._make_request("GET", endpoint)

            # Validate response structure
            if not result.get("tasks") or len(result["tasks"]) == 0:
                raise Exception("No task data returned")

            task_data = result["tasks"][0]
            status_code = task_data.get("status_code")
            status_msg = task_data.get("status_message", "")

            # Handle in-progress states
            if status_code == 40100 or "Task In Queue" in status_msg:
                raise Exception("TASK_IN_QUEUE")
            elif status_code == 40300 or "Task In Progress" in status_msg:
                raise Exception("TASK_IN_PROGRESS")
            elif status_code != 20000:
                raise Exception(f"Task error: {status_msg}")

            return result

        except Exception as e:
            logger.error(f"Failed to check task status: {str(e)}")
            raise

    async def task_get(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve COMPLETE results with page data for a finished crawl

        IMPORTANT: Only use this AFTER crawl_progress is "finished".
        The /pages/ endpoint only works when crawl is complete.

        Args:
            task_id: Task ID from task_post

        Returns:
            Complete crawl results with page data

        Example response:
            {
                "status_code": 20000,
                "tasks": [{
                    "id": "task_id",
                    "status_code": 20000,
                    "result": [{
                        "crawl_progress": "finished",
                        "pages_crawled": 50,
                        "items": [...]  # Actual page data
                    }]
                }]
            }
        """
        # CRITICAL: Use POST /pages/ endpoint with task ID in body
        # NOT GET /pages/{task_id} - that returns 404
        endpoint = "on_page/pages"

        # Request payload with task ID
        payload = [{"id": task_id}]

        logger.info(f"Retrieving page data for task {task_id} via pages endpoint (POST)")

        try:
            result = await self._make_request("POST", endpoint, payload)

            # Validate response structure
            if not result.get("tasks") or len(result["tasks"]) == 0:
                raise Exception("No task data returned")

            task_data = result["tasks"][0]

            # Check task status
            status_code = task_data.get("status_code")
            status_msg = task_data.get("status_message", "")

            # Status codes:
            # 20000 = OK (task completed successfully)
            # 40100 = Task In Queue (still processing - not an error!)
            # 40300 = Task In Progress (still processing - not an error!)
            if status_code == 40100 or "Task In Queue" in status_msg:
                raise Exception("TASK_IN_QUEUE")  # Special marker for in-progress tasks
            elif status_code == 40300 or "Task In Progress" in status_msg:
                raise Exception("TASK_IN_PROGRESS")  # Special marker for in-progress tasks
            elif status_code != 20000:
                raise Exception(f"Task failed: {status_msg}")

            # Check if task has results
            if not task_data.get("result"):
                raise Exception("No results available for task")

            pages_crawled = task_data["result"][0].get("pages_crawled", 0)
            logger.info(f"Retrieved results for {pages_crawled} crawled pages")

            return result

        except Exception as e:
            logger.error(f"Failed to retrieve task results: {str(e)}")
            raise


# Test function (for development)
async def test_client():
    """Test the DataForSEO client"""
    client = DataForSEOClient()

    # Test task_post
    result = await client.task_post("https://example.com", max_crawl_pages=10)
    print(f"Task posted: {result}")

    # Test tasks_ready
    ready = await client.tasks_ready()
    print(f"Ready tasks: {ready}")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_client())
