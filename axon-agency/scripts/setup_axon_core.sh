#!/bin/bash
# Script to configure Axon Core integration

AXON_CORE_URL="${1:-https://api-axon88.algorithmicsai.com}"
ENV_FILE="apps/api/.env"

echo "🔗 Configuring Axon Core integration..."
echo "   URL: $AXON_CORE_URL"

# Test connectivity
echo -n "   Testing connectivity... "
if curl -s --connect-timeout 5 "$AXON_CORE_URL/api/health" > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌"
    echo ""
    echo "⚠️  Warning: Cannot reach Axon Core"
    echo "   Make sure cloudflared tunnel is running on Axon 88"
    echo ""
    echo "   To start the tunnel on Axon 88:"
    echo "   $ cloudflared tunnel --url localhost:8080"
    echo ""
fi

# Get token
echo -n "   Fetching access token... "
TOKEN=$(curl -s -X POST "$AXON_CORE_URL/api/token/dev" | jq -r .access_token 2>/dev/null)

if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "✅"
    
    # Update .env file
    echo -n "   Updating $ENV_FILE... "
    sed -i "s|AXON_CORE_API_BASE=.*|AXON_CORE_API_BASE=$AXON_CORE_URL|g" "$ENV_FILE"
    sed -i "s|AXON_CORE_API_TOKEN=.*|AXON_CORE_API_TOKEN=$TOKEN|g" "$ENV_FILE"
    echo "✅"
    
    echo ""
    echo "✅ Axon Core integration configured!"
    echo ""
    echo "Next steps:"
    echo "1. Restart the backend: make restart"
    echo "2. Run integration tests: python scripts/test_integration.py"
    echo ""
else
    echo "❌"
    echo ""
    echo "⚠️  Could not obtain access token"
    echo ""
    echo "Manual configuration:"
    echo "1. Get token manually:"
    echo "   $ curl -X POST $AXON_CORE_URL/api/token/dev"
    echo ""
    echo "2. Add to $ENV_FILE:"
    echo "   AXON_CORE_API_BASE=$AXON_CORE_URL"
    echo "   AXON_CORE_API_TOKEN=<your-token>"
    echo ""
fi
