# Failed Task IDs - Quick Reference

**Account:** chris@contentmarketerinc.com
**Date:** October 6, 2025
**Issue:** All task_get requests returning 404

---

## Summary

- **Total tasks created:** 15+
- **Tasks successfully retrieved:** 0 (0% success rate)
- **Pattern:** Task IDs change between creation and ready state
- **Common issue:** All tasks in `tasks_ready` return 404 on retrieval

---

## Example Task Failures

### Test 1: example.com (5 pages)
```
Created Task ID:    10060545-1060-0216-0000-fd8b9a344705
Ready Task ID:      10060545-1060-0217-0000-fd8b9a344705
Status:             Both IDs return 404
Note:               ID segment changed from -0216- to -0217-
```

### Test 2: example.com (5 pages)
```
Created Task ID:    10060547-1060-0216-0000-f909b1ce4908
Ready Task ID:      10060547-1060-0217-0000-8240cb6d893a
Status:             Both IDs return 404
Note:               Complete UUID changed in ready list
```

### Test 3: example.com (5 pages)
```
Created Task ID:    10061336-1060-0216-0000-78b0378c950e
Ready Task IDs:     Multiple different IDs observed:
                    - 10061336-1060-0217-0000-242637f87aca
                    - 10061336-1060-0217-0000-4f7e57d347ee
                    - 10061336-1060-0217-0000-352b637624be
                    - 10061336-1060-0217-0000-f7159da2a907
                    - 10061337-1060-0217-0000-e4d6cc88d776
                    - 10061337-1060-0217-0000-7955acbbc9dd
                    - 10061337-1060-0217-0000-380f51dae427
                    - 10061338-1060-0217-0000-8a322609e7d7
Status:             ALL return 404
```

### Test 4: prismspecialtiesdmv.com (50 pages)
```
Created Task ID:    audit_20251005_223652_139774879559552 (internal tracking)
DataForSEO Task ID: Unknown (never successfully retrieved)
Status:             Audit stuck at 10% progress, unable to retrieve results
```

---

## Observed Patterns

### 1. Task ID Transformation
- **Created IDs:** Format `XXXXXXXX-1060-0216-0000-YYYYYYYYYYYY`
- **Ready IDs:** Format `XXXXXXXX-1060-0217-0000-ZZZZZZZZZZZZ`
- **Pattern:** Middle segment changes from `-0216-` to `-0217-`
- **Pattern:** Last segment (UUID) completely changes

### 2. tasks_ready Behavior
- Always shows "1 ready task"
- Task IDs in ready list are different from created IDs
- Every ready task ID returns 404 when retrieved
- New task IDs appear in ready list with each poll

### 3. Consistent Failures
- No task has ever been successfully retrieved
- 404 errors occur regardless of:
  - Time elapsed (tested 0 seconds to 1+ hours)
  - Target website (example.com, prismspecialtiesdmv.com)
  - Task size (5 pages, 50 pages)
  - Using created ID vs ready ID

---

## API Call Examples

### Successful Task Creation
```bash
POST https://api.dataforseo.com/v3/on_page/task_post

Request:
[{
  "target": "https://example.com",
  "max_crawl_pages": 5,
  "load_resources": false,
  "enable_javascript": true,
  "enable_browser_rendering": false,
  "store_raw_html": false
}]

Response:
{
  "version": "0.1.20250922",
  "status_code": 20000,
  "status_message": "Ok.",
  "time": "0.0525 sec.",
  "cost": 0.00625,
  "tasks_count": 1,
  "tasks_error": 0,
  "tasks": [{
    "id": "10060547-1060-0216-0000-f909b1ce4908",
    "status_code": 20100,
    "status_message": "Task Created.",
    "time": "0.0037 sec.",
    "cost": 0.00625,
    "result_count": 0
  }]
}
```

### Tasks Ready Check
```bash
GET https://api.dataforseo.com/v3/on_page/tasks_ready

Response:
{
  "version": "0.1.20250922",
  "status_code": 20000,
  "status_message": "Ok.",
  "cost": 0,
  "tasks_count": 1,
  "tasks": [{
    "id": "10060547-1060-0217-0000-8240cb6d893a",
    "status_message": "Ok."
  }]
}
```

### Failed Task Retrieval (Created ID)
```bash
GET https://api.dataforseo.com/v3/on_page/task_get/10060547-1060-0216-0000-f909b1ce4908

Response:
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

### Failed Task Retrieval (Ready ID)
```bash
GET https://api.dataforseo.com/v3/on_page/task_get/10060547-1060-0217-0000-8240cb6d893a

Response:
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

---

## Account Status

- **Balance:** ~$49 available
- **Total spent on testing:** ~$0.10 (15+ tasks × $0.00625)
- **Rate limiting:** Well under limits (< 10 requests/minute)
- **Authentication:** Verified working (task creation succeeds)
- **Endpoints tested:**
  - ✅ `/v3/on_page/task_post` - Works perfectly
  - ✅ `/v3/on_page/tasks_ready` - Works, shows tasks
  - ❌ `/v3/on_page/task_get/{id}` - Always returns 404

---

## What We've Ruled Out

1. ❌ **Authentication issues** - task_post works fine with same credentials
2. ❌ **Insufficient funds** - account has $49 balance
3. ❌ **Rate limiting** - testing at very low volume
4. ❌ **Network issues** - other endpoints work correctly
5. ❌ **Invalid URL format** - following documentation exactly
6. ❌ **Timing issues** - tested from immediate to 1+ hour delays
7. ❌ **Task failures** - tasks appear in tasks_ready, indicating completion
8. ❌ **Implementation errors** - using official DataForSEO workflow

---

## Key Questions

1. **Why do task IDs change?** Is `-0216-` to `-0217-` transformation expected?
2. **Why do ready tasks return 404?** tasks_ready should only list retrievable tasks
3. **Is there an account limitation?** Does our subscription allow result retrieval?
4. **Are tasks being deleted?** Why are completed tasks immediately unavailable?
5. **Is this a known issue?** Is there a current service disruption?

---

## Technical Environment

- **Client:** Custom Python async client using aiohttp
- **Python Version:** 3.x
- **OS:** WSL2 (Windows Subsystem for Linux)
- **Network:** Standard internet connection
- **Authentication:** Base64-encoded Basic Auth
- **Request Format:** JSON (UTF-8)
- **API Version:** v3
- **API Response Version:** 0.1.20250922

---

**This reference document contains actual task IDs and API responses from testing for DataForSEO support team investigation.**
