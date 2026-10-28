#!/usr/bin/env bash
# cleanup_gcr.sh — Delete old Container Registry images, keeping the 3 most recent.
# Run once from your local machine (with gcloud CLI installed and authenticated):
#   bash scripts/cleanup_gcr.sh <YOUR_PROJECT_ID>
#
# Find your project ID: gcloud config get-value project

set -e

PROJECT_ID="${1:-}"
if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: $0 <PROJECT_ID>"
  echo "Find your project ID: gcloud config get-value project"
  exit 1
fi

IMAGE="gcr.io/${PROJECT_ID}/tntg-corp"

echo "==> Listing all images for ${IMAGE} ..."
gcloud container images list-tags "$IMAGE" \
  --sort-by="~timestamp" \
  --format="table(digest,tags,timestamp)"

echo ""
echo "==> Keeping 'latest' + 3 most recent SHA tags. Deleting the rest..."

# Collect digests to delete: everything except 'latest' after the first 3
TO_DELETE=$(
  gcloud container images list-tags "$IMAGE" \
    --filter="-tags:latest" \
    --sort-by="~timestamp" \
    --format="get(digest)" \
    | tail -n +4
)

if [[ -z "$TO_DELETE" ]]; then
  echo "Nothing to delete — you already have 3 or fewer images."
  exit 0
fi

COUNT=$(echo "$TO_DELETE" | wc -l | tr -d ' ')
echo "Deleting ${COUNT} old image(s)..."

echo "$TO_DELETE" | while read -r DIGEST; do
  echo "  Deleting ${IMAGE}@${DIGEST}"
  gcloud container images delete "${IMAGE}@${DIGEST}" \
    --quiet --force-delete-tags
done

echo ""
echo "Done. Remaining images:"
gcloud container images list-tags "$IMAGE" \
  --sort-by="~timestamp" \
  --format="table(digest,tags,timestamp)"
