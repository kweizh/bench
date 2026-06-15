FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash unzip zip sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Speakeasy CLI
RUN curl -fsSL https://go.speakeasy.com/cli-install.sh | sh

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Speakeasy CLI target generation task environment"

RUN mkdir -p /home/user/myproject && \
    cd /home/user/myproject && \
    cat > openapi.yaml <<'EOF'
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

WORKDIR /home/user/myproject

# Container contents:
#   - speakeasy cli installed
#   - /home/user/myproject - project directory with openapi.yaml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
