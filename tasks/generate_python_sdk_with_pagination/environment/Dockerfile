FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash unzip sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://go.speakeasy.com/cli-install.sh | sh

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Environment with Speakeasy CLI and an initial OpenAPI specification for pagination generation."

RUN cd /home/user && \
    cat >openapi.yaml <<'EOF'
openapi: 3.1.0
info:
  title: Items API
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /items:
    get:
      summary: Get a list of items
      operationId: getItems
      parameters:
        - name: page
          in: query
          schema:
            type: integer
          required: true
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      type: string
                required:
                  - data
EOF

# Container contents:
#   - Speakeasy CLI installed.
#   - /home/user/openapi.yaml — Initial OpenAPI spec without x-speakeasy-pagination

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
