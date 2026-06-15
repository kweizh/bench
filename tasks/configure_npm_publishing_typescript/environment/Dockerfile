FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip && \
    pip3 install --break-system-packages pytest-json-ctrf && \
    wget -qO /tmp/speakeasy.zip https://github.com/speakeasy-api/speakeasy/releases/download/v1.765.1/speakeasy_linux_amd64.zip && \
    unzip -q /tmp/speakeasy.zip -d /tmp/speakeasy && \
    install -m 0755 /tmp/speakeasy/speakeasy /usr/local/bin/speakeasy && \
    rm -rf /tmp/speakeasy /tmp/speakeasy.zip && \
    wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64 && \
    chmod +x /usr/local/bin/yq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/project

# Seed a project with a gen.yaml that has a typescript target using the
# default packageName ("openapi"). The agent must update this file to set
# packageName to "@example/my-sdk" and author to "Example Team".
RUN cat >/home/user/project/gen.yaml <<'EOF'
configVersion: 2.0.0
generation:
  sdkClassName: mySdk
  maintainOpenAPIOrder: true
  usageSnippets:
    optionalPropertyRendering: withExample
  useClassNamesForArrayFields: true
  fixes:
    nameResolutionDec2023: true
    parameterOrderingFeb2024: true
    requestResponseComponentNamesFeb2024: true
    securityFeb2025: true
typescript:
  version: 0.0.1
  packageName: openapi
  author: Speakeasy
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Speakeasy TypeScript SDK project with default gen.yaml awaiting npm publishing configuration."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip
#   - always required pip3 packages: pytest-json-ctrf
#   - speakeasy CLI installed via official install script (symlinked to /usr/local/bin/speakeasy if needed)
#   - yq (mikefarah) installed at /usr/local/bin/yq for YAML inspection and editing
#   - /home/user/project: Speakeasy SDK project directory
#   - /home/user/project/gen.yaml: initial Speakeasy gen.yaml with default TypeScript packageName ("openapi")
