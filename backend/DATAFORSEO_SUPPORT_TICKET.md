# DataForSEO Support Ticket

**Subject:** On-Page API - All task_get requests returning 404 for completed tasks

---

## Account Information
- **Account Email:** chris@contentmarketerinc.com
- **API Being Used:** On-Page API (Standard Method)
- **Issue Date:** October 6, 2025

---

## Problem Description

I am experiencing a critical issue where all `task_get` requests return 404 errors, even for tasks that appear in the `tasks_ready` endpoint. This prevents me from retrieving any crawl results from completed tasks.

---

## Detailed Symptoms

### 1. Tasks Create Successfully
- POST requests to `v3/on_page/task_post` return status code 20100 (Task Created)
- Task IDs are provided in the response
- Account is charged correctly ($0.00625 per task)
- Example successful task creation:
  ```json
  {
    "status_code": 20000,
    "status_message": "Ok.",
    "tasks": [{
      "id": "10061336-1060-0216-0000-78b0378c950e",
      "status_code": 20100,
      "status_message": "Task Created.",
      "cost": 0.00625
    }]
  }
  ```

### 2. Tasks Appear in tasks_ready
- GET requests to `v3/on_page/tasks_ready` show 1 ready task consistently
- Example response shows task IDs like: `10061336-1060-0217-0000-242637f87aca`

### 3. All task_get Requests Return 404
- GET requests to `v3/on_page/task_get/{task_id}` **always** return 404
- This happens for:
  - The original task ID from `task_post`
  - Task IDs listed in `tasks_ready`
  - Tasks created hours or days ago

- Example error response:
  ```json
  {
    "version": "0.1.20250922",
    "status_code": 40400,
    "status_message": "Not Found.",
    "time": "0 sec.",
    "cost": 0,
    "tasks_count": 0,
    "tasks_error": 0,
    "tasks": null
  }
  ```

### 4. Task IDs Appear to Change
- Observed that task IDs change between creation and completion
- Example:
  - Created: `10060547-1060-0216-0000-f909b1ce4908`
  - In tasks_ready: `10060547-1060-0217-0000-8240cb6d893a`
  - Note the change from `-0216-` to `-0217-` in the middle segment

---

## Steps to Reproduce

1. **Create a task:**
   ```bash
   POST https://api.dataforseo.com/v3/on_page/task_post
   Body: [{
     "target": "https://example.com",
     "max_crawl_pages": 5
   }]
   ```
   Result: Task created successfully with ID `10061336-1060-0216-0000-78b0378c950e`

2. **Wait for task completion and check ready list:**
   ```bash
   GET https://api.dataforseo.com/v3/on_page/tasks_ready
   ```
   Result: Shows 1 ready task with ID `10061336-1060-0217-0000-242637f87aca`

3. **Attempt to retrieve task results:**
   ```bash
   GET https://api.dataforseo.com/v3/on_page/task_get/10061336-1060-0217-0000-242637f87aca
   ```
   Result: 404 Not Found

4. **Also tried with original task ID:**
   ```bash
   GET https://api.dataforseo.com/v3/on_page/task_get/10061336-1060-0216-0000-78b0378c950e
   ```
   Result: 404 Not Found

---

## Testing Performed

I have extensively tested this issue over multiple hours with the following results:

### Test 1: Immediate Retrieval
- Created task and immediately tried `task_get`
- Result: 404 error

### Test 2: Polling with tasks_ready
- Created task, polled `tasks_ready` every 15 seconds for 5 minutes
- Tasks appear in `tasks_ready` list
- Every task ID from `tasks_ready` returns 404 when retrieved
- Result: All retrieval attempts failed with 404

### Test 3: Multiple Test Websites
- Tested with multiple targets: example.com, prismspecialtiesdmv.com
- Result: Same 404 error for all

### Test 4: Different Time Intervals
- Tried retrieving tasks immediately after creation
- Tried retrieving after 1 minute, 5 minutes, 30 minutes, 1 hour
- Result: Always 404

### Summary of Tests
- **Total tasks created:** 15+
- **Tasks that appeared in tasks_ready:** All
- **Tasks successfully retrieved:** 0
- **Success rate:** 0%

---

## Questions for Support

1. **Is there an account configuration issue preventing task result retrieval?**
   - Are there specific subscription tiers or permissions required?
   - Do I need to enable a setting for result storage?

2. **Why are task IDs changing between creation and completion?**
   - Is this normal behavior?
   - Should I be using a different ID for retrieval?

3. **Why do tasks in `tasks_ready` return 404?**
   - According to documentation, tasks in `tasks_ready` should be retrievable
   - Are these tasks failing during execution?

4. **Is there an alternative workflow I should be using?**
   - Should I be using postback/pingback instead?
   - Is there a different endpoint for Standard method result retrieval?

5. **Are there any known issues with On-Page API task retention?**
   - Current API version: 0.1.20250922
   - Are there any service disruptions or bugs affecting my account?

---

## Implementation Details

- **Authentication:** Using Basic Auth with login/password encoded in Base64
- **Request Format:** All requests follow documentation exactly
- **HTTP Method:** POST for task_post, GET for tasks_ready and task_get
- **Base URL:** https://api.dataforseo.com/v3
- **Content-Type:** application/json
- **Authorization Header:** Properly formatted as `Basic {base64_credentials}`

---

## Expected Behavior

According to the DataForSEO documentation:

1. POST to `task_post` should create a task and return task ID
2. Task should process (2-5 minutes for small crawls)
3. Task ID should appear in `tasks_ready` when complete
4. GET to `task_get/{task_id}` should return crawl results
5. Results should be available for 30 days (Standard method)

**Current behavior:** Steps 1-3 work correctly, but step 4 always fails with 404.

---

## Impact

This issue is **blocking all development** on my SEO audit tool. I cannot:
- Retrieve any crawl results
- Test my implementation
- Deliver value to end users
- Proceed with project development

---

## Request for Assistance

Please investigate this issue urgently and provide:

1. **Root cause analysis** - Why are all task_get requests failing?
2. **Account verification** - Is my account properly configured for Standard method?
3. **Workaround** - If there's a known issue, is there an alternative approach?
4. **Timeline** - When can I expect this to be resolved?

I am available for any additional debugging, testing, or information you may need.

---

## Additional Information

- **Current account balance:** ~$49 remaining (sufficient funds)
- **Rate limiting:** Well under API limits (testing at low volume)
- **Network:** Requests from WSL2 environment, standard internet connection
- **No errors in:** task_post, tasks_ready endpoints - only task_get fails

Thank you for your prompt attention to this critical issue.

Best regards,
Chris
chris@contentmarketerinc.com
