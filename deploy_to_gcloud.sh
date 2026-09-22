#!/bin/bash
# T&TG Trade Corporation — Google Cloud Deploy Script
# Run this once from your local machine after gcloud CLI is installed

set -e

PROJECT_ID="tomgrouptrade"   # Replace with actual Project ID from console
REGION="us-central1"
SERVICE_NAME="tntg-corp"

echo "=== T&TG Google Cloud Deploy ==="
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com

# Build and deploy
echo "Building and deploying to Cloud Run..."
gcloud builds submit --config cloudbuild.yaml

echo ""
echo "=== Deploy Complete ==="
echo "Your app is live at:"
gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"
