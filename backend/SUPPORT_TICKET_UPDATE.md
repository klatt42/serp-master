# DataForSEO Support Ticket - UPDATE

**Original Issue:** On-Page API - All task_get requests returning 404 for completed tasks

---

## IMPORTANT UPDATE - Issue Partially Resolved

After extensive testing and reviewing the OpenAPI documentation, we discovered that we were using the **incorrect endpoint** for retrieving On-Page API results.

### What We Fixed

**WRONG Endpoint (was causing 404 errors):**
```
GET https://api.dataforseo.com/v3/on_page/task_get/{task_id}
```

**CORRECT Endpoint (now working):**
```
GET https://api.dataforseo.com/v3/on_page/summary/{task_id}
```

**Result:** The 404 errors are now resolved. We can successfully retrieve results using the `/summary/` endpoint.

---

## NEW ISSUE: Tasks Stuck in "TASK_IN_QUEUE" Status

While the endpoint issue is fixed, we've discovered a new problem with task processing.

### Problem Description

Tasks for certain websites (specifically **prismspecialtiesdmv.com**) remain in "TASK_IN_QUEUE" status indefinitely without ever progressing to processing or completion.

### Test Results

#### ✅ SUCCESS: example.com (5 pages)
```
Task ID: 10061422-1060-0216-0000-72077faf5fdc
Wait time: 180 seconds (3 minutes)
Status: Completed successfully
Crawl progress: "finished"
```

#### ❌ FAILURE: prismspecialtiesdmv.com (10-50 pages)
```
Task IDs tested:
- 10061429-1060-0216-0000-1c856f923b21 (50 pages)
- 10061435-1060-0216-0000-a86c3dbd10e8 (10 pages)

Wait time: 5+ minutes (50+ polls)
Status: TASK_IN_QUEUE (status_code: 40100)
Result: Never progresses beyond queue status
```

### Detailed Polling Log

**Example polling sequence for task 10061435-1060-0216-0000-a86c3dbd10e8:**
```
Poll #1  (10s):  40100 "Task In Queue"
Poll #2  (20s):  40100 "Task In Queue"
Poll #3  (30s):  40100 "Task In Queue"
...
Poll #15 (150s): 40100 "Task In Queue"
Poll #17 (170s): 40100 "Task In Queue"
... continues indefinitely
```

The tasks **never** progress from status_code 40100 to 40300 (In Progress) or 20000 (Complete).

---

## Questions for Support

### 1. Queue Processing Time
**Question:** What is the expected queue time for On-Page API tasks?
- Is 5+ minutes normal for a 10-page crawl?
- Should tasks remain in "TASK_IN_QUEUE" for this long?

### 2. Account Priority
**Question:** Does our account type have lower queue priority?
- Account: chris@contentmarketerinc.com
- Account type: [Please advise - Standard/Free/Trial?]
- Are there different queue priorities for different subscription tiers?

### 3. Task Timeout Behavior
**Question:** Is there a maximum queue time before tasks are dropped?
- The tasks never return an error status
- They just remain in queue indefinitely
- Is this expected behavior?

### 4. Website-Specific Issues
**Question:** Could prismspecialtiesdmv.com be causing crawl failures?
- example.com works fine (3 minutes total)
- prismspecialtiesdmv.com never completes (5+ minutes in queue)
- Does DataForSEO provide any feedback on why a specific URL might be queued longer?

### 5. Status Code Documentation
**Question:** Can you clarify status code 40100 behavior?
- Status code: 40100 "Task In Queue"
- When should a task transition from 40100 → 40300 → 20000?
- Is there a way to check queue position or estimated wait time?

---

## Technical Details

### Request Flow
```
1. POST /v3/on_page/task_post
   Body: {
     "target": "https://prismspecialtiesdmv.com",
     "max_crawl_pages": 10
   }
   Response: {
     "status_code": 20000,
     "tasks": [{
       "id": "10061435-1060-0216-0000-a86c3dbd10e8",
       "status_code": 20100,
       "status_message": "Task Created.",
       "cost": 0.0125
     }]
   }

2. GET /v3/on_page/summary/10061435-1060-0216-0000-a86c3dbd10e8
   (Polled every 10 seconds)

   Response (repeats indefinitely):
   {
     "status_code": 20000,
     "tasks": [{
       "status_code": 40100,
       "status_message": "Task In Queue.",
       "result": null
     }]
   }
```

### Implementation Details
- **Poll interval:** 10 seconds
- **Max wait time:** 600 seconds (10 minutes)
- **Authentication:** Basic Auth (working - task creation succeeds)
- **Cost:** Charged $0.0125-$0.0625 per task (deducted from balance)
- **Balance:** $49 available (sufficient)

---

## What We've Verified

✅ **Endpoint is correct** - Using `/summary/` not `/task_get/`
✅ **Task IDs are correct** - Using original ID from `task_post` response
✅ **Authentication works** - Tasks create successfully (status 20100)
✅ **Funds are available** - $49 balance, tasks cost $0.0125-$0.0625
✅ **Polling logic works** - Successfully retrieves example.com results
✅ **Status handling is correct** - Properly interpreting 40100 as "in queue"

❌ **Tasks never leave queue** - Status remains 40100 indefinitely for prismspecialtiesdmv.com

---

## Request for Investigation

Please investigate why tasks for **prismspecialtiesdmv.com** remain in TASK_IN_QUEUE status indefinitely:

1. **Check task IDs** in your system:
   - `10061429-1060-0216-0000-1c856f923b21` (50 pages)
   - `10061435-1060-0216-0000-a86c3dbd10e8` (10 pages)

2. **Review queue status** - Are these tasks stuck? Failed? Dropped?

3. **Check for errors** - Are there crawler errors not being reported?

4. **Advise on resolution** - Should we:
   - Wait longer (how long is normal)?
   - Use postback/pingback instead?
   - Reduce page count further?
   - Check website's robots.txt or blocking?

---

## Additional Context

- **Working example:** example.com completes in 3 minutes
- **Not working:** prismspecialtiesdmv.com stuck in queue for 5+ minutes
- **Test date:** October 6, 2025
- **API version:** 0.1.20250922
- **Tested:** Multiple page counts (5, 10, 50) - all stuck in queue

---

Thank you for your assistance with this issue. The endpoint correction has resolved the 404 errors, but we need help understanding why certain websites never process from the queue.

Best regards,
Chris
chris@contentmarketerinc.com
