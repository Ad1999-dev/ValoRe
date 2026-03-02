# Cloud setup

## Google Cloud Project
- Project ID: valore-mlsd-project
- Region: europe-west1

## Billing
- Educational credits: $50 linked to the project

## IAM access
Team members are added through Google Cloud IAM: Owner.

## Local authentication (required for Python SDK)
Commands used:
- `gcloud init`
- `gcloud config set project valore-mlsd-project`
- `gcloud auth application-default login`

If quota mismatch happens:
- `gcloud auth application-default set-quota-project valore-mlsd-project`

## Enabled APIs
- BigQuery API: `bigquery.googleapis.com`
- (Optional) Cloud Storage API: `storage.googleapis.com`