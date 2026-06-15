FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip && \
    pip3 install --break-system-packages pytest-json-ctrf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install mikefarah/yq (Go binary) used by the verifier to parse workflow.yaml
RUN curl -fsSL -o /usr/local/bin/yq \
        https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 && \
    chmod +x /usr/local/bin/yq

# Install the real Speakeasy CLI from the official release archive.
# The plan.md was updated to use this direct-download approach to avoid GitHub
# API rate limits triggered by the cli-install.sh script during Docker builds.
# This installs the same official binary the install script would fetch.
ARG SPEAKEASY_VERSION=1.765.1
RUN wget -q https://github.com/speakeasy-api/speakeasy/releases/download/v${SPEAKEASY_VERSION}/speakeasy_linux_amd64.zip -O /tmp/speakeasy.zip && \
    unzip -q /tmp/speakeasy.zip -d /tmp/speakeasy && \
    mv /tmp/speakeasy/speakeasy /usr/local/bin/speakeasy && \
    chmod +x /usr/local/bin/speakeasy && \
    rm -rf /tmp/speakeasy /tmp/speakeasy.zip

RUN mkdir -p /home/user && chmod 0755 /home/user

# Seed the project directory with a minimal but valid OpenAPI 3 (petstore-like) spec.
# Do NOT create .speakeasy/workflow.yaml — the agent must author it.
RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    cat > openapi.yaml <<'EOF'
openapi: 3.0.3
info:
  title: Petstore API
  version: 1.0.0
  description: A minimal petstore API used as the source for SDK generation.
servers:
  - url: https://api.example.com
paths:
  /pets:
    get:
      operationId: listPets
      summary: List all pets
      responses:
        '200':
          description: A list of pets.
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Pet'
    post:
      operationId: createPet
      summary: Create a pet
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NewPet'
      responses:
        '201':
          description: The created pet.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Pet'
  /pets/{petId}:
    get:
      operationId: getPetById
      summary: Get a pet by ID
      parameters:
        - name: petId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: A single pet.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Pet'
components:
  schemas:
    Pet:
      type: object
      required: [id, name]
      properties:
        id:
          type: string
        name:
          type: string
        tag:
          type: string
    NewPet:
      type: object
      required: [name]
      properties:
        name:
          type: string
        tag:
          type: string
EOF

WORKDIR /home/user/project

LABEL Author="generate-harbor-tasks"
LABEL Description="Speakeasy CLI environment for authoring a basic .speakeasy/workflow.yaml from a seeded OpenAPI 3 spec."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip
#   - always required pip3 packages: pytest-json-ctrf
#   - real Speakeasy CLI installed via https://go.speakeasy.com/cli-install.sh (symlinked to /usr/local/bin/speakeasy)
#   - mikefarah/yq for YAML parsing in the verifier
#   - /home/user/project: project root with a seeded openapi.yaml (OpenAPI 3 petstore spec)
#   - .speakeasy/workflow.yaml is intentionally NOT pre-created
