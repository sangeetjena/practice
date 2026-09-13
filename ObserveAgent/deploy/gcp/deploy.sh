#!/usr/bin/env bash
# Deploy reviewed images/configuration to your project; never embeds secret values.
# Example environment and prerequisites: docs/GOOGLE_CLOUD.md.
set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
: "${REGION:?Set REGION}"
: "${IMAGE:?Set IMAGE to the pushed Dockerfile.cloud image}"
: "${CLOUD_SQL_CONNECTION:?Set project:region:instance}"
: "${DATABASE_SECRET:?Existing Secret Manager name containing DATABASE_URL}"
: "${AUTH_SECRET:?Existing Secret Manager name containing OBSERVE_AUTH_KEYS JSON}"
: "${TENANTS_SECRET:?Existing Secret Manager name containing OBSERVE_TENANTS JSON}"
: "${CHROMA_HOST:?Set a reachable private Chroma server hostname}"

gcloud services enable run.googleapis.com pubsub.googleapis.com cloudscheduler.googleapis.com \
  sqladmin.googleapis.com secretmanager.googleapis.com --project "$PROJECT_ID"

ensure_account() {
  local account="$1"
  gcloud iam service-accounts describe "$account@$PROJECT_ID.iam.gserviceaccount.com" \
    --project "$PROJECT_ID" >/dev/null 2>&1 || \
    gcloud iam service-accounts create "$account" --project "$PROJECT_ID"
}
for account in observe-api observe-worker observe-push observe-scheduler; do
  ensure_account "$account"
done
api_sa="observe-api@$PROJECT_ID.iam.gserviceaccount.com"
worker_sa="observe-worker@$PROJECT_ID.iam.gserviceaccount.com"
push_sa="observe-push@$PROJECT_ID.iam.gserviceaccount.com"
scheduler_sa="observe-scheduler@$PROJECT_ID.iam.gserviceaccount.com"
for identity in "$api_sa" "$worker_sa"; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member "serviceAccount:$identity" \
    --role roles/cloudsql.client --condition=None >/dev/null
  for secret in "$DATABASE_SECRET" "$TENANTS_SECRET"; do
    gcloud secrets add-iam-policy-binding "$secret" --project "$PROJECT_ID" \
      --member "serviceAccount:$identity" --role roles/secretmanager.secretAccessor >/dev/null
  done
done
gcloud secrets add-iam-policy-binding "$AUTH_SECRET" --project "$PROJECT_ID" \
  --member "serviceAccount:$api_sa" --role roles/secretmanager.secretAccessor >/dev/null

gcloud pubsub topics describe observe-events --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud pubsub topics create observe-events --project "$PROJECT_ID"
gcloud pubsub topics add-iam-policy-binding observe-events --project "$PROJECT_ID" \
  --member "serviceAccount:$worker_sa" --role roles/pubsub.publisher >/dev/null

network_flags=()
if [[ -n "${VPC_CONNECTOR:-}" ]]; then
  network_flags+=(--vpc-connector "$VPC_CONNECTOR" --vpc-egress private-ranges-only)
fi
common_flags=(--project "$PROJECT_ID" --region "$REGION" --image "$IMAGE" \
  --set-cloudsql-instances "$CLOUD_SQL_CONNECTION")
common_secrets="DATABASE_URL=$DATABASE_SECRET:latest,OBSERVE_TENANTS=$TENANTS_SECRET:latest"

# Schema setup runs separately, before accepting traffic. No model or Chroma calls required.
gcloud run jobs deploy observe-migrate "${common_flags[@]}" "${network_flags[@]}" \
  --service-account "$worker_sa" --set-secrets "$common_secrets" \
  --set-env-vars "CHROMA_HOST=$CHROMA_HOST,OBSERVE_AUTH_KEYS=[]" \
  --command python --args=-m,observe_agent.cloud.admin,migrate --task-timeout 600s
gcloud run jobs execute observe-migrate --project "$PROJECT_ID" --region "$REGION" --wait

# Services start in offline/dry-run mode. Enable models after configuring model secrets.
gcloud run deploy observe-api "${common_flags[@]}" "${network_flags[@]}" \
  --service-account "$api_sa" --no-allow-unauthenticated --port 8090 \
  --set-secrets "$common_secrets,OBSERVE_AUTH_KEYS=$AUTH_SECRET:latest" \
  --set-env-vars "APP_ROLE=api,CHROMA_HOST=$CHROMA_HOST" \
  --concurrency 20 --max-instances 5 --memory 1Gi --timeout 60s
gcloud run deploy observe-worker "${common_flags[@]}" "${network_flags[@]}" \
  --service-account "$worker_sa" --no-allow-unauthenticated --port 8090 \
  --set-secrets "$common_secrets" \
  --set-env-vars "APP_ROLE=worker,OBSERVE_AUTH_KEYS=[],CHROMA_HOST=$CHROMA_HOST,PUBSUB_TOPIC=projects/$PROJECT_ID/topics/observe-events,ACTION_MODE=dry_run" \
  --concurrency 1 --max-instances 5 --memory 1Gi --timeout 600s
worker_url=$(gcloud run services describe observe-worker --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)')
gcloud run services update observe-worker --project "$PROJECT_ID" --region "$REGION" \
  --update-env-vars "PUBSUB_AUDIENCE=$worker_url,PUBSUB_SERVICE_ACCOUNT=$push_sa,SCHEDULER_AUDIENCE=$worker_url,SCHEDULER_SERVICE_ACCOUNT=$scheduler_sa"
for identity in "$push_sa" "$scheduler_sa"; do
  gcloud run services add-iam-policy-binding observe-worker --project "$PROJECT_ID" --region "$REGION" \
    --member "serviceAccount:$identity" --role roles/run.invoker >/dev/null
done
project_number=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
gcloud iam service-accounts add-iam-policy-binding "$push_sa" --project "$PROJECT_ID" \
  --member "serviceAccount:service-$project_number@gcp-sa-pubsub.iam.gserviceaccount.com" \
  --role roles/iam.serviceAccountTokenCreator >/dev/null
subscription_verb=create
if gcloud pubsub subscriptions describe observe-worker --project "$PROJECT_ID" >/dev/null 2>&1; then
  subscription_verb=update
fi
subscription_flags=(--project "$PROJECT_ID" --push-endpoint "$worker_url/internal/events" \
  --push-auth-service-account "$push_sa" --push-auth-token-audience "$worker_url" --ack-deadline 600)
if [[ "$subscription_verb" == create ]]; then subscription_flags+=(--topic observe-events); fi
gcloud pubsub subscriptions "$subscription_verb" observe-worker "${subscription_flags[@]}"
scheduler_verb=create
if gcloud scheduler jobs describe observe-outbox --project "$PROJECT_ID" --location "$REGION" >/dev/null 2>&1; then
  scheduler_verb=update
fi
gcloud scheduler jobs "$scheduler_verb" http observe-outbox --project "$PROJECT_ID" --location "$REGION" \
  --schedule '* * * * *' --uri "$worker_url/internal/outbox" --http-method POST \
  --oidc-service-account-email "$scheduler_sa" --oidc-token-audience "$worker_url" --attempt-deadline 320s
gcloud run services describe observe-api --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)'
