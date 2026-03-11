# Design Decisions (ADR log)

## ADR-001: Online data source for EDA and training
- Date: 2026-03-02
- Decision: Use **BigQuery** as the primary online data source for EDA and training.
- Reason:
  - Supports SQL EDA directly on cloud-hosted data
  - Matches OLAP concepts taught in the course
  - Satisfies professor requirement to work with online data
- Consequences:
  - Need ingestion step (load CSV into BigQuery)
  - Training scripts should query BigQuery instead of reading local files

## ADR-002: Raw file storage
- Date: 2026-02-28
- Decision: Use **GCS** for raw dataset storage and future artifacts.
- Reason:
  - Standard MLOps pattern: raw files and artifacts in object storage
  - Works well for model files and metrics outputs later
- Consequences:
  - Maintain bucket path documentation
  - Ensure data is not committed to Git

## ADR-003: Repo workflow
- Date: 2026-02-09
- Decision: Use GitFlow with branches `main`, `develop`, and `feature/*`.
- Reason:
  - Required by lab and course process
  - Supports traceable milestone PRs
- Consequences:
  - PR required for milestone submission (`develop` $\to$ `main`)

## ADR-004: CI/CD tooling
- Date: 2026-02-09
- Decision: Use Ruff + pre-commit + pytest + GitHub Actions.
- Reason:
  - Matches lab instruction
  - Provides consistent formatting, linting and automated checks
- Consequences:
  - Contributors must install pre-commit locally
