FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest python3-venv bash unzip sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://go.speakeasy.com/cli-install.sh | sh

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Speakeasy environment with a sample openapi.yaml for Python SDK generation"

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    cat >openapi.yaml <<'EOF'
openapi: 3.0.3
info:
  title: Example API
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /hello:
    get:
      operationId: getHello
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
EOF

# Container contents:
#   - speakeasy CLI installed
#   - /home/user/project - working directory
#   - /home/user/project/openapi.yaml - sample OpenAPI spec

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]