FROM ubuntu:24.04

# Pin the Speakeasy CLI version installed via the official install script.
# The install script calls the GitHub API to discover the latest release; we
# patch that single line to use a pinned tag so the build is deterministic and
# does not depend on anonymous GitHub API rate limits.
ENV SPEAKEASY_VERSION=1.765.1

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep \
        unzip jq sudo && \
    pip3 install --break-system-packages pytest-json-ctrf && \
    ARCH="$(dpkg --print-architecture)" && \
    case "${ARCH}" in \
        amd64) YQ_BIN="yq_linux_amd64" ;; \
        arm64) YQ_BIN="yq_linux_arm64" ;; \
        *) echo "Unsupported architecture: ${ARCH}" >&2; exit 1 ;; \
    esac && \
    curl -fsSL "https://github.com/mikefarah/yq/releases/download/v4.44.3/${YQ_BIN}" \
        -o /usr/local/bin/yq && \
    chmod +x /usr/local/bin/yq && \
    curl -fsSL https://go.speakeasy.com/cli-install.sh -o /tmp/cli-install.sh && \
    sed -i 's|latest_tag=\$(get_latest_release "\$REPO_NAME")|latest_tag="v${VERSION}"|' /tmp/cli-install.sh && \
    VERSION="${SPEAKEASY_VERSION}" sh /tmp/cli-install.sh && \
    if [ ! -x /usr/local/bin/speakeasy ] && [ -x /root/.speakeasy/bin/speakeasy ]; then \
        ln -sf /root/.speakeasy/bin/speakeasy /usr/local/bin/speakeasy; \
    fi && \
    rm -f /tmp/cli-install.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/project && \
    cat >/home/user/project/gen.yaml <<'EOF'
configVersion: 2.0.0
generation:
  sdkClassName: speakeasybar
  maintainOpenAPIOrder: true
  usageSnippets:
    optionalPropertyRendering: withExample
  useClassNamesForArrayFields: true
  fixes:
    nameResolutionDec2023: true
    parameterOrderingFeb2024: true
    requestResponseComponentNamesFeb2024: true
    securityFeb2025: true
  auth:
    oAuth2ClientCredentialsEnabled: false
    oAuth2PasswordEnabled: false
typescript:
  version: 0.1.0
  author: speakeasy-eval
  packageName: "@speakeasy-eval/sdk"
  clientServerStatusCodesAsErrors: true
  enumFormat: enum
  flattenGlobalSecurity: true
  imports:
    option: openapi
    paths:
      callbacks: sdk/models/callbacks
      errors: sdk/models/errors
      operations: sdk/models/operations
      shared: sdk/models/shared
      webhooks: sdk/models/webhooks
  inputModelSuffix: input
  maxMethodParams: 5
  methodArguments: require-security-and-request
  moduleFormat: commonjs
  outputModelSuffix: output
  responseFormat: envelope
  templateVersion: v1
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Speakeasy task environment with a seeded TypeScript SDK project at /home/user/project where gen.yaml has OAuth2 client credentials disabled."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - additional apt packages: unzip, jq, sudo (used by the speakeasy install script)
#   - always required pip3 packages: pytest-json-ctrf
#   - speakeasy CLI installed via the official install script (https://go.speakeasy.com/cli-install.sh),
#     pinned to v${SPEAKEASY_VERSION} so the GitHub API release-lookup line is bypassed
#   - yq (mikefarah/yq) installed to /usr/local/bin/yq for YAML verification
#   - /home/user/project: seeded Speakeasy project directory
#   - /home/user/project/gen.yaml: initial gen.yaml with oAuth2ClientCredentialsEnabled set to false and a TypeScript target
