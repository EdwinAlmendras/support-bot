#!/bin/bash

# Stop containers
echo "🛑 Stopping bot..."
docker compose down

# Remove database
if [ -f "data/bot.db" ]; then
    echo "🗑️ Deleting database..."
    sudo rm -f data/bot.db
fi

# Rebuild and start
echo "🚀 Rebuilding and starting..."
# Ensure we build to include latest code changes
docker compose up -d --build

echo "✅ Done! Logs:"
docker compose logs -f bot
