#!/bin/bash
# Start Graphiti Memory Layer (Docker + containers)
# Called by macOS Launch Agent at login

LOG="/tmp/graphiti_startup.log"
echo "$(date): Starting Graphiti memory layer..." >> "$LOG"

# Wait for Docker daemon to be ready (max 120s)
MAX_WAIT=120
WAITED=0
while ! /usr/local/bin/docker info &>/dev/null 2>&1; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "$(date): Docker not ready after ${MAX_WAIT}s, starting Docker Desktop..." >> "$LOG"
        open -a Docker
        sleep 30
        break
    fi
    sleep 5
    WAITED=$((WAITED + 5))
done

# Check again
if ! /usr/local/bin/docker info &>/dev/null 2>&1; then
    echo "$(date): Docker still not ready, aborting" >> "$LOG"
    exit 1
fi

echo "$(date): Docker ready, starting containers..." >> "$LOG"

/usr/local/bin/docker compose \
    --env-file /Users/mathieulandry-girouard/graphiti/mcp_server/.env \
    -f /Users/mathieulandry-girouard/graphiti/mcp_server/docker/docker-compose.yml \
    up -d >> "$LOG" 2>&1

# Wait for health check
sleep 15
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
echo "$(date): Health check: $HEALTH" >> "$LOG"
