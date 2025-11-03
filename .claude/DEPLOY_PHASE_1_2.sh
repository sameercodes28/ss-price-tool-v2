#!/bin/bash
# Deployment Script: Phase 1 & 2 (v2.5.0)
# Critical fixes + Error code system
# Run from project root: /Users/sameerm4/Desktop/SS-2

set -e  # Exit on error

echo "🚀 Deploying Phase 1 & 2 to Production"
echo "========================================"
echo ""

# Check we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "error_codes.py" ]; then
    echo "❌ Error: Run from project root (must contain main.py and error_codes.py)"
    exit 1
fi

# Check git status
echo "1️⃣ Checking git status..."
git status --short
echo ""

# Confirm deployment
read -p "Deploy Phase 1 & 2 to production? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Deploy to Google Cloud Functions
echo ""
echo "2️⃣ Deploying to Google Cloud Functions..."
echo "   Region: europe-west2"
echo "   Runtime: python311"
echo ""

gcloud functions deploy sofa-price-calculator-v2 \
  --region europe-west2 \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point http_entry_point \
  --timeout 540s \
  --memory 512MB

echo ""
echo "✅ Deployment complete!"
echo ""

# Test deployed version
echo "3️⃣ Testing deployed version..."
echo ""

API_URL="https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2"

# Test 1: Valid query
echo "   Test 1: Valid query (should return price)"
RESPONSE=$(curl -s -X POST "$API_URL/getPrice" \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}')

if echo "$RESPONSE" | grep -q "price"; then
    echo "   ✅ Valid queries working"
else
    echo "   ❌ Valid query failed!"
    echo "   Response: $RESPONSE"
fi
echo ""

# Test 2: Error code (missing query)
echo "   Test 2: Error codes (missing query)"
RESPONSE=$(curl -s -X POST "$API_URL/getPrice" \
  -H "Content-Type: application/json" \
  -d '{}')

if echo "$RESPONSE" | grep -q "error_code"; then
    ERROR_CODE=$(echo "$RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('error_code', 'NONE'))")
    echo "   ✅ Error codes working (got: $ERROR_CODE)"
else
    echo "   ⚠️  Error codes not in response yet (may need a few minutes)"
fi
echo ""

# Test 3: Chat endpoint
echo "   Test 3: Chat endpoint"
RESPONSE=$(curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "How much is midhurst?"}], "session_id": "deploy-test"}')

if echo "$RESPONSE" | grep -q "response"; then
    echo "   ✅ Chat endpoint working"
else
    echo "   ❌ Chat endpoint failed!"
fi
echo ""

# Check logs
echo "4️⃣ Recent logs:"
gcloud functions logs read sofa-price-calculator-v2 --region europe-west2 --limit 10
echo ""

echo "=========================================="
echo "✅ Deployment Complete!"
echo ""
echo "Next steps:"
echo "  1. Test frontend at index.html"
echo "  2. Monitor telemetry.html for errors"
echo "  3. Check debug.html for API calls"
echo "  4. Watch logs for [Cache] and error codes"
echo ""
echo "Rollback if needed:"
echo "  git checkout 945f196  # v2.4.0"
echo "  gcloud functions deploy..."
echo ""
