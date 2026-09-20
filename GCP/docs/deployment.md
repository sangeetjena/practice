# Build, deploy, and promote

All examples start in `practice/GCP`. Local rendering and tests are free of cloud writes. Terraform apply, publish, promote, and `run --execute` are explicit cloud operations. Use an existing billing-enabled project for each environment.

## 1. Set environment configuration

Replace every `replace-me-*` project ID and deployment service-account email in the environment files. Add real group emails. Confirm region and subnet ranges. Defaults enable only the two storage-based examples; Bigtable, NAT, and API jobs are opt-in. Provision capacity and confirm quotas before scheduling production runs.

Install Python 3.11, Terraform 1.9 or newer (CI pins 1.11.4), Google Cloud CLI, and Docker with Linux container support. Install the Python environment as described in the README. Google provider selections and dependency versions are committed in lock files.

## 2. Bootstrap each project once

An administrator creates the state bucket, deployment service account, and GitHub federation. Ordinary workflow callers cannot bootstrap or edit IAM.

Copy `infrastructure/bootstrap/terraform.tfvars.example` into `build/dev/bootstrap.tfvars` and fill the GitHub repository/owner **numeric IDs**, exact repository name, and release branch. Use separate directories and state for each environment. Obtain numeric IDs from GitHub's repository API or `gh api repos/OWNER/REPO --jq '{repository_id: .id, owner_id: .owner.id}'`.

```powershell
New-Item -ItemType Directory -Force build/dev
Copy-Item infrastructure/bootstrap/terraform.tfvars.example build/dev/bootstrap.tfvars
# Edit build/dev/bootstrap.tfvars before continuing.
gcloud auth application-default login
terraform -chdir=infrastructure/bootstrap init
terraform -chdir=infrastructure/bootstrap plan -state=../../build/dev/bootstrap.tfstate -var-file=../../build/dev/bootstrap.tfvars -out=../../build/dev/bootstrap.tfplan
terraform -chdir=infrastructure/bootstrap apply -state=../../build/dev/bootstrap.tfstate ../../build/dev/bootstrap.tfplan
```

The `-state` option is used only for this local bootstrap backend so dev/preprod/prod do not share a state file. Securely back up the bootstrap state or migrate it to a separately controlled remote backend. Never delete it after creating the resources. The platform state below uses a GCS backend with locking and object versioning.

Set GitHub environment variables in `gcp-dev`, `gcp-preprod`, and `gcp-prod`:

- `GCP_WIF_PROVIDER`: bootstrap's federation provider resource name.
- `GCP_DEPLOYER_SA`: bootstrap's deployment service-account email.
- `GCP_STATE_BUCKET`: `<PROJECT_ID>-terraform-state`.
- `GCP_ARTIFACT_BUCKET`: `<PROJECT_ID>-<name>-<environment>-artifacts`.

Protect the release branch and these environments. Require production reviewers and restrict the deployment branch to the bootstrap trust condition. These are repository settings, not automatically applied by Terraform in this template.

## 3. Provision the foundation

```powershell
gcp-platform render --env dev
$env:TF_DATA_DIR = Join-Path (Get-Location) 'build/dev/tfdata'
terraform -chdir=infrastructure/environments init -backend-config="bucket=YOUR_DEV_PROJECT-terraform-state" -backend-config="prefix=platform/dev"
terraform -chdir=infrastructure/environments plan -var-file=../../build/dev/platform.tfvars.json -out=../../build/dev/infra.tfplan
# Review the plan before applying it.
terraform -chdir=infrastructure/environments apply ../../build/dev/infra.tfplan
terraform -chdir=infrastructure/environments output -json | Set-Content -Encoding utf8 build/dev/outputs.json
```

Use a different `TF_DATA_DIR`, bucket, prefix, and output directory for each environment. Never run prod against a dev backend. The root configuration is reusable; the state and identities are not shared.

With no release manifest, workflows reject execution and configured Scheduler jobs remain paused. This allows registries, buckets and identities to exist before artifact publication. Provision input data and secret versions before enabling the corresponding workload.

## 4. Build once and publish in dev

```powershell
gcp-platform publish --env dev --outputs build/dev/outputs.json --version git-a1b2c3d
```

Publication builds three Linux images: Beam launcher, Beam worker, and Spark. It pushes them to the Terraform-created immutable-tag repository, resolves their digests, packages shared Python code deterministically, uploads the Spark driver/archive, and creates a Flex Template JSON specification. It writes `build/releases/git-a1b2c3d/dev-release.json` and uploads a copy to the release prefix in Cloud Storage.

Use a unique version associated with the reviewed commit. Reusing a version fails because image tags are immutable and object uploads use `ifGenerationMatch=0`. If a partial publish fails, diagnose it and use a new version rather than overwriting a release. `publish` requires Docker and artifact write permissions; it does not launch jobs.

## 5. Deploy the release

```powershell
gcp-platform render --env dev --release build/releases/git-a1b2c3d/dev-release.json
terraform -chdir=infrastructure/environments plan -var-file=../../build/dev/platform.tfvars.json -out=../../build/dev/release.tfplan
terraform -chdir=infrastructure/environments apply ../../build/dev/release.tfplan
terraform -chdir=infrastructure/environments output -json | Set-Content -Encoding utf8 build/dev/outputs.json
```

Workflows now references the published image digests and artifact URIs. Run the fixture smoke test from [the jobs guide](../jobs/README.md), inspect output, and verify IAM/secret/network behavior in your actual project.

For later **configuration-only changes**, render with the currently deployed manifest. Rendering without `--release` deliberately returns the platform to the unpublished/paused state; it is not the normal update path. The CI `infra` operation refuses to reset an existing platform this way.

## 6. Promote to preprod and prod

Provision the target foundation and export its outputs first. An authorized promotion identity needs read access to the source release objects/images and publish access in the target project. Bootstrap intentionally does not grant cross-environment access automatically. Grant source artifact-bucket Object Viewer and source repository Artifact Registry Reader to that promotion identity through your foundation administration process.

```powershell
gcp-platform promote --env preprod --outputs build/preprod/outputs.json --version git-a1b2c3d --source-release build/releases/git-a1b2c3d/dev-release.json
gcp-platform render --env preprod --release build/releases/git-a1b2c3d/preprod-release.json
```

Promotion copies existing digest-pinned images, the original Spark driver/archive, and the original template metadata. It checks that image digests remain identical. It changes environment-specific artifact addresses, not executable code. Apply the target environment's reviewed plan using its backend. Repeat for prod after preprod validation.

The deployment workflow's `release` operation downloads a manifest **already published into the target environment**. It does not rebuild or implicitly promote artifacts. This makes the promotion trust boundary explicit.

## GitHub Actions

`gcp-checks.yml` runs lint, Python/Beam/Spark tests, schema consistency, Terraform formatting/validation, and mock plans. Pull requests do not receive GCP credentials.

`gcp-deploy.yml` is manually dispatched from the trusted branch:

- `infra`: initial foundation apply, with schedules paused.
- `publish`: build and publish a version in dev, without running jobs.
- `release`: apply an already-published environment release.

Deployment runs are serialized by environment. They authenticate through federation, run local validation, save a Terraform plan, and apply that saved plan. GitHub environment reviewers approve the deployment run before credentials are issued. The saved plan is uploaded for audit. For organizations requiring a separate **human approval of the exact plan**, use the manual plan/apply sequence above or split CI into protected plan and apply jobs with the plan artifact passed between them; the starter's single deployment job does not claim that additional gate.

## Rollback and upgrades

Redeploy a previous release manifest to affect subsequent runs. Already-running jobs continue using their original configuration. IAM/resource changes require their own reviewed Terraform plan; reverting an image does not revert data or undo schema changes.

Bigtable writes use stable customer/day cells; concurrent different releases writing the same keys can conflict. Avoid overlapping backfills against those keys. GCS batch outputs are isolated by run ID; downstream consumers must deliberately select a successful run instead of globbing every historical run and double-counting it.

Refresh dependencies deliberately with `uv pip compile`, review container vulnerability scan results, upgrade the Beam SDK and worker base image together, and run preprod smoke tests. Update launcher/base image pins as part of that process. No cloud deployment has been attempted by creating this repository.
