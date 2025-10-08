#!/bin/bash
# SERP-Master Log Checker
# Shows detailed error logs and diagnostics

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         SERP-Master Log Checker & Diagnostics              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if server is running
echo "🔍 Server Status:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/health)
    echo "   ✅ Server is RUNNING"
    echo "   Response: $HEALTH"
else
    echo "   ❌ Server is NOT running"
    echo "   Start with: cd ~/serp-master/backend && ./start.sh"
fi
echo ""

# Check server logs
echo "═══════════════════════════════════════════════════════════"
echo "📋 Server Logs (last 50 lines):"
echo "═══════════════════════════════════════════════════════════"
if [ -f /tmp/serp_api.log ]; then
    tail -50 /tmp/serp_api.log
else
    echo "   No server log found at /tmp/serp_api.log"
    echo ""
    echo "   Checking for running Python processes..."
    ps aux | grep "python.*app.main" | grep -v grep
fi
echo ""

# Check DataForSEO connection
echo "═══════════════════════════════════════════════════════════"
echo "🔌 DataForSEO Connection Test:"
echo "═══════════════════════════════════════════════════════════"

cd ~/serp-master/backend
source venv/bin/activate

python3 << 'PYEOF'
import asyncio
import os
from app.services.dataforseo_client import DataForSEOClient

async def test_connection():
    try:
        print("   Testing DataForSEO API connection...")
        client = DataForSEOClient()

        # Check ready tasks
        ready = await client.tasks_ready()

        print(f"   ✅ Connection successful")
        print(f"   Ready tasks: {len(ready.get('tasks', []))}")

        # Show recent tasks
        if ready.get('tasks'):
            print("")
            print("   Recent ready tasks:")
            for i, task in enumerate(ready['tasks'][:5], 1):
                print(f"      {i}. Task ID: {task.get('id')}")
                print(f"         Status: {task.get('status_message')}")

    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")

asyncio.run(test_connection())
PYEOF

echo ""

# Check disk space
echo "═══════════════════════════════════════════════════════════"
echo "💾 Disk Space:"
echo "═══════════════════════════════════════════════════════════"
df -h ~ | head -2
echo ""

# Check memory
echo "═══════════════════════════════════════════════════════════"
echo "🧠 Memory Usage:"
echo "═══════════════════════════════════════════════════════════"
free -h | head -2
echo ""

# Show recent audit tasks
echo "═══════════════════════════════════════════════════════════"
echo "📊 Recent Audit Tasks:"
echo "═══════════════════════════════════════════════════════════"
if [ -f ~/serp-master/backend/audit_results_*.json ]; then
    echo "   Saved audit results:"
    ls -lht ~/serp-master/backend/audit_results_*.json 2>/dev/null | head -5
else
    echo "   No saved audit results found"
fi
echo ""

# Show environment variables
echo "═══════════════════════════════════════════════════════════"
echo "⚙️  Environment Configuration:"
echo "═══════════════════════════════════════════════════════════"
cd ~/serp-master/backend
if [ -f .env ]; then
    echo "   DataForSEO Login: $(grep DATAFORSEO_LOGIN .env | cut -d'=' -f2)"
    echo "   DataForSEO URL: $(grep DATAFORSEO_API_URL .env | cut -d'=' -f2)"
    echo "   Environment: $(grep ENVIRONMENT .env | cut -d'=' -f2)"
else
    echo "   ⚠️  No .env file found"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    DIAGNOSTICS COMPLETE                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "💡 Tips:"
echo "   • View live logs: tail -f /tmp/serp_api.log"
echo "   • Test API: curl http://localhost:8000/health"
echo "   • Run audit: ./auto_audit.sh prismspecialtiesdmv.com"
echo ""
