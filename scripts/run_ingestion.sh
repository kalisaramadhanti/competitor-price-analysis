#!/bin/sh

set -e

echo "=== Starting synthetic fixture ingestion ==="

# Historical month-end fixtures
for file in synthetic_mock_store/historical/*.html; do
    filename=$(basename "$file" .html)
    date=$(echo "$filename" | cut -c1-10)
    platform=$(echo "$filename" | cut -c12-)

    echo "Ingesting $file ($platform, $date)"

    python -m crawler.main \
        --source "$file" \
        --platform "$platform" \
        --base-url "https://synthetic.example" \
        --storage postgres \
        --crawled-at "${date}T12:00:00+07:00"
done

# Current/latest synthetic fixtures
echo "Ingesting latest Blibli fixture"

python -m crawler.main \
    --source synthetic_mock_store/analytics/index.html \
    --platform blibli \
    --base-url "https://synthetic.example" \
    --storage postgres \
    --crawled-at "2026-09-30T12:00:00+07:00"

echo "Ingesting latest Tokopedia fixture"

python -m crawler.main \
    --source synthetic_mock_store/analytics_tokopedia/index.html \
    --platform tokopedia \
    --base-url "https://synthetic.example" \
    --storage postgres \
    --crawled-at "2026-09-30T12:00:00+07:00"

echo "=== Synthetic fixture ingestion complete ==="