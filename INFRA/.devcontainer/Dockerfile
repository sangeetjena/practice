FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG TARGETARCH
ARG KIND_VERSION=v0.27.0
ARG KUBECTL_VERSION=v1.32.2
ARG HELM_VERSION=v3.17.3
ARG TERRAFORM_VERSION=1.11.4

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        jq \
        make \
        python3 \
        python3-pip \
        python3-venv \
        unzip \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    case "$TARGETARCH" in \
      amd64|arm64) ARCH="$TARGETARCH" ;; \
      *) echo "Unsupported architecture: $TARGETARCH" >&2; exit 1 ;; \
    esac; \
    curl -fsSL "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-${ARCH}" \
      -o /usr/local/bin/kind; \
    chmod 0755 /usr/local/bin/kind; \
    curl -fsSLo /tmp/kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${ARCH}/kubectl"; \
    curl -fsSLo /tmp/kubectl.sha256 "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${ARCH}/kubectl.sha256"; \
    echo "$(cat /tmp/kubectl.sha256)  /tmp/kubectl" | sha256sum --check --status; \
    install -o root -g root -m 0755 /tmp/kubectl /usr/local/bin/kubectl; \
    curl -fsSLo /tmp/helm.tar.gz "https://get.helm.sh/helm-${HELM_VERSION}-linux-${ARCH}.tar.gz"; \
    curl -fsSLo /tmp/helm.tar.gz.sha256sum "https://get.helm.sh/helm-${HELM_VERSION}-linux-${ARCH}.tar.gz.sha256sum"; \
    echo "$(awk '{print $1}' /tmp/helm.tar.gz.sha256sum)  /tmp/helm.tar.gz" \
      | sha256sum --check --status; \
    tar -xzf /tmp/helm.tar.gz -C /tmp; \
    install -o root -g root -m 0755 "/tmp/linux-${ARCH}/helm" /usr/local/bin/helm; \
    curl -fsSLo /tmp/terraform.zip "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_${ARCH}.zip"; \
    curl -fsSLo /tmp/terraform_SHA256SUMS "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_SHA256SUMS"; \
    TERRAFORM_SHA="$(awk -v file="terraform_${TERRAFORM_VERSION}_linux_${ARCH}.zip" '$2 == file {print $1}' /tmp/terraform_SHA256SUMS)"; \
    test -n "$TERRAFORM_SHA"; \
    echo "$TERRAFORM_SHA  /tmp/terraform.zip" | sha256sum --check --status; \
    unzip -q /tmp/terraform.zip -d /usr/local/bin; \
    rm -rf /tmp/kubectl /tmp/kubectl.sha256 /tmp/helm.tar.gz /tmp/helm.tar.gz.sha256sum \
      /tmp/linux-${ARCH} /tmp/terraform.zip /tmp/terraform_SHA256SUMS

USER vscode
RUN python3 --version \
    && kind version \
    && kubectl version --client \
    && helm version --short \
    && terraform version