#!/bin/bash
# Automatic Audit Script with Retry Logic
# Usage: ./auto_audit.sh <website_url> [max_pages]

URL="${1:-prismspecialtiesdmv.com}"
MAX_PAGES="${2:-50}"
MAX_WAIT=600  # 10 minutes max wait
POLL_INTERVAL=30

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         SERP-Master Automatic Audit Script                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Website: $URL"
echo "Max Pages: $MAX_PAGES"
echo "Max Wait: ${MAX_WAIT}s"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Server not running. Starting server..."
    cd ~/serp-master/backend
    source venv/bin/activate
    nohup python -m app.main > /tmp/serp_api.log 2>&1 &
    SERVER_PID=$!
    echo "   Server started with PID: $SERVER_PID"
    echo "   Waiting for server to be ready..."
    sleep 5

    # Verify server started
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "❌ Server failed to start. Check logs:"
        echo "   tail -50 /tmp/serp_api.log"
        exit 1
    fi
    echo "✅ Server is ready"
    echo ""
fi

# Start audit
echo "🚀 Starting audit..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/audit/start \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$URL\", \"max_pages\": $MAX_PAGES}")

TASK_ID=$(echo $RESPONSE | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TASK_ID" ]; then
    echo "❌ Failed to start audit"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Audit started"
echo "   Task ID: $TASK_ID"
echo ""

# Monitor progress
echo "📊 Monitoring progress..."
echo "═══════════════════════════════════════════════════════════"

START_TIME=$(date +%s)
POLL_COUNT=0

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))

    # Check timeout
    if [ $ELAPSED -gt $MAX_WAIT ]; then
        echo ""
        echo "⏱️  Timeout reached (${MAX_WAIT}s)"
        echo ""
        echo "🔍 Checking server logs for issues..."
        tail -30 /tmp/serp_api.log
        exit 1
    fi

    # Poll status
    POLL_COUNT=$((POLL_COUNT + 1))
    STATUS_RESPONSE=$(curl -s http://localhost:8000/api/audit/status/$TASK_ID)

    STATUS=$(echo $STATUS_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    PROGRESS=$(echo $STATUS_RESPONSE | grep -o '"progress":[0-9]*' | cut -d':' -f2)

    TIMESTAMP=$(date +%H:%M:%S)
    echo "[$TIMESTAMP] Poll #$POLL_COUNT - Status: $STATUS, Progress: ${PROGRESS}%"

    # Check if complete
    if [ "$STATUS" = "complete" ]; then
        echo ""
        echo "✅ Audit COMPLETE!"
        echo "   Time taken: ${ELAPSED}s"
        echo "   Total polls: $POLL_COUNT"
        echo ""

        # Get results
        echo "📥 Fetching results..."
        RESULTS=$(curl -s http://localhost:8000/api/audit/results/$TASK_ID)

        # Save results to file
        RESULTS_FILE="audit_results_$(date +%Y%m%d_%H%M%S).json"
        echo "$RESULTS" > "$RESULTS_FILE"
        echo "   Results saved to: $RESULTS_FILE"
        echo ""

        # Parse and display summary
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║                    AUDIT SUMMARY                           ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        echo ""

        # Extract score using Python
        python3 << EOF
import json
import sys

try:
    with open('$RESULTS_FILE', 'r') as f:
        data = json.load(f)

    score = data.get('score', {})
    issues = data.get('issues', {})
    metadata = data.get('metadata', {})

    print(f"🎯 SEO Score: {score.get('total_score', 'N/A')}/{score.get('max_score', 30)} ({score.get('percentage', 0):.1f}%)")
    print(f"   Grade: {score.get('grade', 'N/A')}")
    print("")

    print("📊 Score Breakdown:")
    print(f"   Technical SEO:  {score.get('technical_seo', {}).get('score', 0)}/10")
    print(f"   On-Page SEO:    {score.get('onpage_seo', {}).get('score', 0)}/10")
    print(f"   Site Structure: {score.get('structure_seo', {}).get('score', 0)}/10")
    print("")

    summary = issues.get('summary', {})
    print("🔍 Issues Found:")
    print(f"   Critical: {summary.get('critical_count', 0)}")
    print(f"   Warnings: {summary.get('warning_count', 0)}")
    print(f"   Info:     {summary.get('info_count', 0)}")
    print(f"   Quick Wins: {summary.get('quick_win_count', 0)}")
    print("")

    print("📈 Crawl Statistics:")
    print(f"   Pages Crawled: {metadata.get('pages_crawled', 'N/A')}")
    print(f"   Duration: {metadata.get('crawl_duration_seconds', 'N/A')}s")
    print("")

    # Show top 3 quick wins
    quick_wins = issues.get('quick_wins', [])
    if quick_wins:
        print("⚡ Top 3 Quick Wins:")
        print("")
        for i, issue in enumerate(quick_wins[:3], 1):
            print(f"   {i}. {issue.get('issue', 'N/A')}")
            print(f"      Impact: +{issue.get('impact', 0)} points | Effort: {issue.get('effort', 'N/A')}")
            print(f"      Affected: {issue.get('pages_affected', 'N/A')}")
            rec = issue.get('recommendation', '')
            print(f"      Fix: {rec[:70]}..." if len(rec) > 70 else f"      Fix: {rec}")
            print("")

except Exception as e:
    print(f"Error parsing results: {e}")
    print("")
    print("Raw results available in: $RESULTS_FILE")
EOF

        echo "═══════════════════════════════════════════════════════════"
        echo ""
        echo "📄 Full results: $RESULTS_FILE"
        echo "🌐 API Docs: http://localhost:8000/docs"
        echo ""
        exit 0
    fi

    # Check if failed
    if [ "$STATUS" = "failed" ]; then
        echo ""
        echo "❌ Audit FAILED"
        MESSAGE=$(echo $STATUS_RESPONSE | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
        echo "   Error: $MESSAGE"
        echo ""
        echo "🔍 Server logs:"
        tail -30 /tmp/serp_api.log
        exit 1
    fi

    # Wait before next poll
    sleep $POLL_INTERVAL
done
