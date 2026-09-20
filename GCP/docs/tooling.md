# Build and orchestration choices

There is no universal industry build tool for data engineering. Choose each tool for the problem it solves and the languages the team maintains.

**Terraform** owns cloud infrastructure and IAM, with separate state per environment, reviewed plans and pinned Google providers. It is not the recurring data-job scheduler.

**Python packaging plus pinned dependency lock files** serves the Beam/PySpark implementation and CLI. Docker supplies preinstalled dependencies to cloud workers, avoiding runtime downloads over the public internet. Image digests identify actual executable artifacts during promotion.

**GitHub Actions** fits this repository's existing CI layout. It validates pull requests and uses Workload Identity Federation for protected deployments. Cloud Build is also a reasonable GCP-native build executor when a team prefers it; introducing two competing CI implementations in the starter would add maintenance without improving this workflow.

**Maven** builds the Java Flink extension. Flink documents Maven project setup, and its dependency scopes and shade plugin fit packaging one job JAR without bundling the runtime itself. The POM aligns Flink libraries, runs stateful operator tests, and produces the JAR copied into the image. Python workloads still use Python tooling, and Terraform still manages infrastructure.

**Gradle** is another good JVM option, particularly when the team already standardizes on it or needs more custom build logic. It is not necessary to introduce a second Java build system alongside Maven for this single job.

**Bazel** offers explicit build graphs, caching, and reproducibility features for large multi-language repositories. Its adoption cost is difficult to justify for this small Python-first platform; reconsider it when repository scale and build performance make that tradeoff worthwhile.

**Make** can provide aliases, but it does not replace Terraform, a dependency resolver, or CI. A Python CLI works on this user's Windows workspace and on Linux CI without requiring Make. Optional Make targets can wrap the CLI later.

## Which companies use Maven or Bazel?

Concrete public examples, rather than an unsupported popularity ranking:

- **AWS:** its Java SDK v2 contribution guide uses Maven for building and testing. [AWS SDK contributor guide](https://github.com/aws/aws-sdk-java-v2/blob/master/CONTRIBUTING.md)
- **Microsoft:** the Azure SDK for Java engineering guide uses Maven. [Azure SDK engineering guide](https://github.com/Azure/azure-sdk-for-java/wiki/Getting-Started-Guidance)
- **Uber:** its engineering team documents adopting Bazel for the Go monorepo. [Uber engineering](https://www.uber.com/us/en/blog/go-monorepo-bazel/)
- **Stripe:** its engineering blog documents Bazel for build and test pipelines. [Stripe engineering](https://stripe.com/blog/fast-secure-builds-choose-two)

These examples concern particular products or build platforms, not exclusive company-wide policies. Maven fits this Java job's ecosystem and limited build graph. Bazel would become more attractive with a much larger multi-language monorepo, shared remote caching/execution, and engineers available to maintain its rules. Publishing to Maven Central does not itself prove that a project builds with Maven; Gradle and Bazel projects can consume/publish Maven artifacts too.

[Flink's Maven guide](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/dev/configuration/maven/) and [Bazel's user directory](https://bazel.build/community/users) provide further context.

**Cloud Scheduler + Workflows** is the implemented orchestration choice. It provides scheduled triggers and a serverless execution state machine without operating an Airflow environment. Workflows is responsible for launch, polling, timeout handling, and failure propagation.

**Cloud Composer (managed Airflow)** becomes a stronger choice for large interdependent DAGs, many sensors, sophisticated catch-up/backfill controls, shared Airflow operators, and teams already operating Airflow. This starter deliberately documents the limits of its simple daily window policy. Do not recreate all of Airflow's scheduling semantics inside a growing custom workflow framework.

## Dependency maintenance

The container SDK/runtime versions are deliberately explicit. Update `pyproject.toml` and the corresponding Docker base image together. Resolve locks for all target platforms and constrain the smaller dependency sets to the Beam resolution:

```text
uv pip compile pyproject.toml --python-version 3.11 --extra beam --extra cloud --universal -o requirements/beam.lock
uv pip compile pyproject.toml --python-version 3.11 --extra cloud --universal --constraint requirements/beam.lock -o requirements/cloud.lock
uv pip compile pyproject.toml --python-version 3.11 --extra dev --extra cloud --universal --constraint requirements/beam.lock -o requirements/dev.lock
```

Commit lock changes with validation evidence. Resolve and test target runtime compatibility, especially Beam/Protobuf/gRPC combinations. OS base image packages are not frozen by Python locks; production artifacts should also receive your registry's vulnerability scanning and base-image upgrade process. Promotion reuses tested image digests and does not rebuild them.
