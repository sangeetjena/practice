from __future__ import annotations

import re
from typing import Annotated, Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Name = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{1,11}$")]
Positive = Annotated[int, Field(strict=True, ge=1)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Network(StrictModel):
    subnet_cidr: str
    enable_nat: bool = False

    @field_validator("subnet_cidr")
    @classmethod
    def cidr(cls, value):
        import ipaddress

        network = ipaddress.ip_network(value, strict=True)
        if network.version != 4 or not network.is_private:
            raise ValueError("Use a private IPv4 subnet")
        return value


class Access(StrictModel):
    developer_groups: list[str] = []
    operator_groups: list[str] = []
    viewer_groups: list[str] = []
    deployment_service_account: str

    @field_validator("developer_groups", "operator_groups", "viewer_groups")
    @classmethod
    def groups(cls, values):
        if any(not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value) for value in values):
            raise ValueError("Groups must be email addresses without a group: prefix")
        return values

    @field_validator("deployment_service_account")
    @classmethod
    def service_account(cls, value):
        if not re.fullmatch(r"[a-z0-9-]+@[a-z0-9-]+\.iam\.gserviceaccount\.com", value):
            raise ValueError("Expected a deployment service-account email")
        return value


class Dataflow(StrictModel):
    machine_type: str = "n2-standard-2"
    initial_workers: Positive = 1
    max_workers: Positive = 3
    disk_size_gb: Annotated[int, Field(ge=30)] = 50

    @model_validator(mode="after")
    def worker_limits(self):
        if self.initial_workers > self.max_workers:
            raise ValueError("initial_workers cannot exceed max_workers")
        return self


class Dataproc(StrictModel):
    # A supported LTS runtime. Upgrade deliberately with an integration smoke test.
    runtime_version: str = "2.2"
    executor_instances: Annotated[int, Field(ge=2)] = 2
    max_executors: Annotated[int, Field(ge=2)] = 4
    executor_cores: Literal[4, 8, 16] = 4
    ttl: Annotated[str, Field(pattern=r"^[1-9][0-9]*s$")] = "7200s"

    @model_validator(mode="after")
    def executor_limits(self):
        if self.executor_instances > self.max_executors:
            raise ValueError("executor_instances cannot exceed max_executors")
        return self


class Bigtable(StrictModel):
    enabled: bool = False
    zone: str
    min_nodes: Positive = 1
    max_nodes: Positive = 3
    cpu_target: Annotated[int, Field(ge=10, le=80)] = 60
    table: str = "customer_metrics"
    column_family: str = "metrics"

    @model_validator(mode="after")
    def node_limits(self):
        if self.min_nodes > self.max_nodes:
            raise ValueError("min_nodes cannot exceed max_nodes")
        return self


class Secret(StrictModel):
    secret_id: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_-]{1,255}$")]
    version: Annotated[str, Field(pattern=r"^[1-9][0-9]*$")]
    readers: list[Literal["dataflow", "dataproc"]]


class Schedule(StrictModel):
    enabled: bool = False
    cron: str = "0 2 * * *"
    timezone: str = "UTC"

    @field_validator("cron")
    @classmethod
    def cron_fields(cls, value):
        if len(value.split()) != 5:
            raise ValueError("Expected a five-field Cloud Scheduler cron expression")
        return value

    @field_validator("timezone")
    @classmethod
    def timezone_exists(cls, value):
        ZoneInfo(value)
        return value


class Job(StrictModel):
    engine: Literal["dataflow", "dataproc"]
    use_case: Literal["clean_orders", "daily_sales", "partner_extract", "bigtable_metrics"]
    input_prefix: str = "orders/"
    output_prefix: str = "results/"
    secret: str | None = None
    api_url: str | None = None
    timeout_seconds: Annotated[int, Field(ge=600, le=86400)] = 14400
    schedule: Schedule = Schedule()

    @field_validator("input_prefix", "output_prefix")
    @classmethod
    def relative_prefix(cls, value):
        if not re.fullmatch(r"[a-zA-Z0-9_/-]+/", value) or ".." in value or value.startswith("/"):
            raise ValueError("Use a relative bucket prefix ending in /; no traversal or URI")
        return value

    @model_validator(mode="after")
    def supported_example(self):
        allowed = {
            "dataflow": {"clean_orders", "partner_extract", "bigtable_metrics"},
            "dataproc": {"daily_sales", "partner_extract"},
        }
        if self.use_case not in allowed[self.engine]:
            raise ValueError("This use case is not implemented for the selected engine")
        if self.use_case == "partner_extract":
            if not self.secret or not self.api_url or not self.api_url.startswith("https://"):
                raise ValueError("partner_extract requires a secret reference and an HTTPS api_url")
        elif self.secret or self.api_url:
            raise ValueError("Only partner_extract accepts secret and api_url settings")
        return self


class Flink(StrictModel):
    enabled: bool = False
    namespace: Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{1,30}$")] = "flink"
    authorized_cidrs: list[str] = []
    pod_cidr: str = "10.60.0.0/16"
    service_cidr: str = "10.70.0.0/20"
    master_cidr: str = "172.16.0.0/28"
    node_machine_type: str = "e2-standard-4"
    min_nodes: Positive = 1
    max_nodes: Positive = 3
    parallelism: Positive = 2
    task_slots: Positive = 2
    jobmanager_cpu: Positive = 1
    taskmanager_cpu: Positive = 2
    jobmanager_replicas: Positive = 1
    rocksdb_local_disk_gb: Positive = 20
    jobmanager_memory: str = "2048m"
    taskmanager_memory: str = "4096m"
    join_horizon_seconds: Positive = 86400
    allowed_lateness_seconds: Annotated[int, Field(ge=0)] = 3600
    out_of_orderness_seconds: Annotated[int, Field(ge=0)] = 30
    idle_timeout_seconds: Positive = 120
    max_retention_seconds: Positive = 259200
    window_seconds: Positive = 300
    checkpoint_interval_seconds: Positive = 60
    checkpoint_timeout_seconds: Positive = 600
    file_discovery_seconds: Positive = 10
    batch_schedule: Schedule = Schedule(enabled=False, cron="0 4 * * *", timezone="UTC")
    batch_timeout_seconds: Annotated[int, Field(ge=600, le=86400)] = 14400

    @model_validator(mode="after")
    def bounds(self):
        import ipaddress

        if self.min_nodes > self.max_nodes:
            raise ValueError("Flink min_nodes cannot exceed max_nodes")
        if self.max_retention_seconds < self.join_horizon_seconds + self.allowed_lateness_seconds:
            raise ValueError("Flink retention must cover join horizon plus allowed lateness")
        ranges = [
            ipaddress.ip_network(value, strict=True)
            for value in [self.pod_cidr, self.service_cidr, self.master_cidr]
        ]
        if any(network.version != 4 or not network.is_private for network in ranges):
            raise ValueError("GKE ranges must be private IPv4")
        if ranges[2].prefixlen != 28:
            raise ValueError("GKE master_cidr must be /28")
        if any(left.overlaps(right) for index, left in enumerate(ranges) for right in ranges[index + 1 :]):
            raise ValueError("GKE address ranges cannot overlap")
        for value in self.authorized_cidrs:
            if ipaddress.ip_network(value).prefixlen == 0:
                raise ValueError("Do not expose the GKE control plane to all addresses")
        if self.enabled and not self.authorized_cidrs:
            raise ValueError("Flink requires authorized_cidrs for the operator/deployment runner")
        return self


class PlatformConfig(StrictModel):
    environment: Literal["dev", "preprod", "prod"]
    project_id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")]
    region: Annotated[str, Field(pattern=r"^[a-z]+-[a-z]+[0-9]+$")]
    name: Name = "data"
    network: Network
    access: Access
    dataflow: Dataflow = Dataflow()
    dataproc: Dataproc = Dataproc()
    bigtable: Bigtable
    secrets: dict[str, Secret] = {}
    jobs: dict[Name, Job]
    flink: Flink = Flink()

    @model_validator(mode="after")
    def references(self):
        if self.flink.enabled:
            import ipaddress

            if not self.network.enable_nat:
                raise ValueError("GKE private nodes require NAT for the public operator images")
            subnet = ipaddress.ip_network(self.network.subnet_cidr)
            if any(
                subnet.overlaps(ipaddress.ip_network(cidr))
                for cidr in (self.flink.pod_cidr, self.flink.service_cidr, self.flink.master_cidr)
            ):
                raise ValueError("GKE ranges overlap the worker subnet")
        ids = [secret.secret_id for secret in self.secrets.values()]
        if len(ids) != len(set(ids)):
            raise ValueError("Secret IDs must be unique")
        if not self.jobs:
            raise ValueError("Define at least one job")
        for name, job in self.jobs.items():
            if job.secret:
                secret = self.secrets.get(job.secret)
                if secret is None or job.engine not in secret.readers:
                    raise ValueError(f"{name}: secret must exist and grant access to {job.engine}")
                if not self.network.enable_nat:
                    raise ValueError(f"{name}: external API examples require network.enable_nat")
            if job.use_case == "bigtable_metrics" and not self.bigtable.enabled:
                raise ValueError(f"{name}: enable Bigtable before enabling this example")
        return self
