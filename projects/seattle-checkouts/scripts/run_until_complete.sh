#!/bin/bash

echo "🚀 Starting ingestion job..."

until python3 ~/data-portfolio/projects/seattle-checkouts/scripts/ingest.py; do
    echo "❌ Job failed — restarting in 60 seconds..."
    sleep 60
done

echo "✅ Ingestion complete!"