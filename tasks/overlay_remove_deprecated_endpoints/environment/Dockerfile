FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash unzip sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://go.speakeasy.com/cli-install.sh | sh

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Speakeasy environment with an openapi.yaml containing deprecated endpoints."

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
  /old-endpoint:
    get:
      deprecated: true
      operationId: old
      responses:
        '200':
          description: OK
EOF

# Container contents:
#   - speakeasy CLI installed
#   - /home/user/project  — project directory
#   - openapi.yaml with deprecated /old-endpoint

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
