FROM ubuntu:24.04

# Install base apt packages, the Speakeasy CLI (pinned GitHub release),
# yq, and required pip packages.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip && \
    pip3 install --break-system-packages pytest-json-ctrf && \
    ARCH="$(uname -m)" && \
    case "$ARCH" in \
        x86_64|amd64) SPEAKEASY_ARCH="linux_amd64"; YQ_ARCH="linux_amd64" ;; \
        aarch64|arm64) SPEAKEASY_ARCH="linux_arm64"; YQ_ARCH="linux_arm64" ;; \
        *) echo "Unsupported architecture: $ARCH" >&2 && exit 1 ;; \
    esac && \
    curl -fsSL -o /tmp/speakeasy.zip \
        "https://github.com/speakeasy-api/speakeasy/releases/download/v1.765.1/speakeasy_${SPEAKEASY_ARCH}.zip" && \
    mkdir -p /tmp/speakeasy_unzip && \
    unzip -q /tmp/speakeasy.zip -d /tmp/speakeasy_unzip && \
    install -m 0755 /tmp/speakeasy_unzip/speakeasy /usr/local/bin/speakeasy && \
    rm -rf /tmp/speakeasy.zip /tmp/speakeasy_unzip && \
    curl -fsSL -o /usr/local/bin/yq \
        "https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_${YQ_ARCH}" && \
    chmod +x /usr/local/bin/yq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create the user home directory expected by Harbor tasks.
RUN mkdir -p /home/user && chmod 0755 /home/user

# Seed the project directory with a valid OpenAPI 3 spec that contains
# both an internal endpoint (the overlay target) and a public endpoint
# (which must remain untouched).
RUN mkdir -p /home/user/project && \
    cat > /home/user/project/openapi.yaml <<'EOF'
openapi: 3.0.3
info:
  title: Speakeasy Bar Mixed API
  version: 1.0.0
  description: |
    Sample API exposing both internal and public endpoints. Used to demonstrate
    OpenAPI Overlays that hide internal endpoints from generated SDKs.
servers:
  - url: https://api.example.com
paths:
  /internal/health:
    get:
      operationId: getInternalHealth
      summary: Internal health probe
      description: Used by internal monitoring; should be excluded from public SDKs.
      tags:
        - internal
      responses:
        '200':
          description: Service is healthy.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthStatus'
  /public/items:
    get:
      operationId: listItems
      summary: List public items
      description: Returns a list of items visible to public API consumers.
      tags:
        - public
      responses:
        '200':
          description: A list of items.
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Item'
components:
  schemas:
    HealthStatus:
      type: object
      required:
        - status
      properties:
        status:
          type: string
          enum: [ok, degraded, down]
    Item:
      type: object
      required:
        - id
        - name
      properties:
        id:
          type: string
        name:
          type: string
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Speakeasy CLI environment seeded with an OpenAPI spec containing internal and public endpoints for overlay tasks."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip
#   - always required pip3 packages: pytest-json-ctrf
#   - Speakeasy CLI v1.765.1 installed from the official GitHub release to /usr/local/bin/speakeasy
#   - yq v4.44.3 installed to /usr/local/bin/yq for YAML assertions
#   - /home/user/project/openapi.yaml: seeded OpenAPI 3 spec with /internal/health (GET) and /public/items (GET)
