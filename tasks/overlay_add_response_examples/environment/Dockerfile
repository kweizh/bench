FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash unzip jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download latest speakeasy release directly to avoid sudo requirement in cli-install.sh
RUN LATEST_TAG=$(curl -fsSL https://api.github.com/repos/speakeasy-api/speakeasy/releases/latest | jq -r .tag_name) && \
    VERSION=${LATEST_TAG#v} && \
    curl -fsSL "https://github.com/speakeasy-api/speakeasy/releases/download/${LATEST_TAG}/speakeasy_linux_amd64.zip" -o speakeasy.zip && \
    unzip speakeasy.zip && \
    mv speakeasy /usr/local/bin/ && \
    chmod +x /usr/local/bin/speakeasy && \
    rm speakeasy.zip

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Speakeasy environment with an initial openapi.yaml for overlay testing."

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    cat >openapi.yaml <<'EOF'
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /ping:
    get:
      operationId: ping
      responses:
        '200':
          description: OK
EOF

# Container contents:
#   - speakeasy CLI installed
#   - /home/user/project  — project directory
#   - openapi.yaml with /ping endpoint

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]