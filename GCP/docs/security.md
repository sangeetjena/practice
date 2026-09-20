# Identities, access, and secrets

## Who can change or run things?

Infrastructure changes are made by the dedicated deployment service account through protected CI. Humans propose changes in Git. Configure branch protection, required checks, CODEOWNERS, protected GitHub environments, reviewer groups, and allowed deployment branches in GitHub; a GCP IAM policy cannot enforce repository review rules.

`viewer_groups` receive project-level job/workflow/log viewing roles. `developer_groups` receive those viewing roles and can invoke workflows in **dev only**. `operator_groups` can invoke workflows in the environment's project where they are listed. Workflows Invoker is granted at project scope: use dedicated environment projects, and do not place unrelated privileged workflows there. These groups do not receive project Editor or Owner. If operators need to inspect source/output data, add reviewed bucket-level grants rather than expanding these job-management roles.

The current runtime identities are per engine and environment: `<name>-<env>-dataflow` and `<name>-<env>-dataproc`. Their permissions are shared by jobs on that engine. For mutually untrusted workloads, extend the identity map to one account per job and bind separate buckets/secrets. The template does not claim per-job isolation with a shared engine account.

The workflow identity can create/read/cancel jobs using a custom launcher role and can attach only the two runtime service accounts. The scheduler identity can invoke workflows in the dedicated environment project. Runtime accounts get worker roles and scoped access to the platform's data/staging/artifact resources. Secret access is granted on individual configured secrets.

Google-managed Dataflow and Dataproc service agents remain distinct from worker identities. Terraform materializes the service agents and grants their corresponding service-agent roles; do not use those identities as human or workload accounts.

## CI authentication

Bootstrap configures GitHub OIDC Workload Identity Federation. Its trust condition checks the immutable numeric repository and owner IDs, the release branch, and the exact `repo:OWNER/REPO:environment:gcp-ENV` subject. This avoids trusting arbitrary repositories with similarly named owners or accepting an unprotected branch's token.

CI uses short-lived credentials through `google-github-actions/auth`. No service-account JSON keys are generated. Local operators can use Application Default Credentials with their user identity or approved impersonation. Grant impersonation separately and narrowly if your organization permits it; the template does not give every developer token-creation rights.

Bootstrap is an administrator operation. The infrastructure deployer has IAM, networking, storage, and service administration permissions because it provisions these controls. Although it is not granted Secret Accessor, a privileged IAM administrator can grant additional access; it is part of the trusted administrative boundary. Restrict its workflow and federation configuration accordingly. Splitting foundation IAM into a separate administrator-managed repository is a further hardening option.

## How secrets reach Dataflow

1. Terraform creates `partner-api-key` and a secret-level `roles/secretmanager.secretAccessor` grant for the Dataflow worker identity.
2. An authorized secret operator adds a version. Example: `gcloud secrets versions add partner-api-key --project PROJECT --data-file=/secure/location/key.txt`. The file must remain outside this repository and be handled under your team's secret-management procedure.
3. YAML specifies the numeric version, such as `'3'`.
4. Terraform places `projects/PROJECT/secrets/partner-api-key/versions/3` in the job parameters.
5. `FetchPartner.setup()` calls `read_secret()` on a Dataflow worker. Google client libraries use Application Default Credentials backed by that worker's attached service account.
6. The API key stays in worker memory and is supplied as an HTTPS header. The constructor only contains the secret reference, so the payload is not serialized into Beam's launch graph.

## How secrets reach Dataproc

The same reference is passed in the PySpark argument list. `fetch_partition()` obtains the secret inside each executor partition using the configured Dataproc runtime identity. The driver does not fetch and broadcast a plaintext token. Secret values are never placed in Spark configuration, command-line parameters, workflow environment variables, image layers, or Terraform state.

The helper pins numeric versions for repeatable releases. Rotation means adding a new version, changing the YAML reference, applying configuration, and validating a new run. A running worker caches the retrieved value for its setup/partition lifetime; rotation does not magically replace memory in an already-running task.

## Example boundaries

API endpoints are deployment configuration, not ad hoc arguments. Redirects are disabled to prevent an API key being forwarded to another host. Responses are capped at 10 MB per day in the sample. Failures do not include response bodies or credential headers in the exception text. Provider pagination, timeouts, rate limits and retry semantics must be adapted for a real integration.

Secret Manager IAM grants access to secret versions; pinning a version is an application reproducibility control, not a per-version IAM boundary. Also do not put credentials in the configured URL itself.

## References

- [Secret Manager best practices](https://docs.cloud.google.com/secret-manager/docs/best-practices)
- [Workload Identity Federation for deployment pipelines](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
- [Dataflow security and permissions](https://docs.cloud.google.com/dataflow/docs/concepts/security-and-permissions)
