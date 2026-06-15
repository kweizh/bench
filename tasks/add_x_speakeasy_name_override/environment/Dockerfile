FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip && \
    pip3 install --break-system-packages pytest-json-ctrf pyyaml && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the real Speakeasy CLI v1.765.1 directly from the GitHub release archive.
# We pin the version to make builds deterministic and to avoid hitting GitHub's
# anonymous API rate limit (the official install script otherwise queries the
# GitHub releases API to resolve "latest"). The archive ships a single
# `speakeasy` binary that we drop into /usr/local/bin so it is on PATH.
RUN curl -fsSL -o /tmp/speakeasy.zip \
        https://github.com/speakeasy-api/speakeasy/releases/download/v1.765.1/speakeasy_linux_amd64.zip && \
    unzip -o /tmp/speakeasy.zip -d /tmp/speakeasy && \
    install -m 0755 /tmp/speakeasy/speakeasy /usr/local/bin/speakeasy && \
    rm -rf /tmp/speakeasy /tmp/speakeasy.zip && \
    /usr/local/bin/speakeasy --version

# Install yq (Mike Farah's Go implementation) for YAML inspection in tests and
# by the executor. Pinned for reproducibility.
RUN curl -fsSL -o /usr/local/bin/yq \
        https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64 && \
    chmod 0755 /usr/local/bin/yq && \
    /usr/local/bin/yq --version

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/project

# Seed a real, lint-clean OpenAPI 3.0 specification at
# /home/user/project/openapi.yaml. The spec contains a cryptic operationId
# `pst_user_create` for `POST /users` that the executor must rename to
# `createUser` via the `x-speakeasy-name-override` extension. The spec is
# deliberately valid (no duplicate operationIds, all $refs resolve) so
# `speakeasy lint openapi` exits 0 both before and after the executor's edit.
RUN cat >/home/user/project/openapi.yaml <<'EOF'
openapi: 3.0.3
info:
  title: User Service API
  version: 1.0.0
  description: A small CRUD API for managing users.
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      operationId: lst_users_list
      summary: List users
      tags:
        - users
      responses:
        '200':
          description: A list of users.
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    post:
      operationId: pst_user_create
      summary: Create a user
      tags:
        - users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      responses:
        '201':
          description: The created user.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
  /users/{userId}:
    get:
      operationId: get_user_by_id
      summary: Get a user by id
      tags:
        - users
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: The requested user.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      required:
        - id
        - name
      properties:
        id:
          type: string
          description: Unique identifier for the user.
        name:
          type: string
          description: Display name of the user.
        email:
          type: string
          format: email
          description: Contact email for the user.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Speakeasy CLI v1.765.1 + yq environment with a lint-clean OpenAPI 3.0 spec whose POST /users operation has a cryptic operationId (pst_user_create) for the agent to rename via x-speakeasy-name-override."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: pyyaml (used by initial/final-state tests)
#   - Speakeasy CLI v1.765.1 installed from the official GitHub release zip into /usr/local/bin/speakeasy
#   - yq v4.44.3 (Mike Farah) installed into /usr/local/bin/yq
#   - /home/user/project: working directory for the task
#   - /home/user/project/openapi.yaml: lint-clean OpenAPI 3.0 spec with cryptic operationId pst_user_create on POST /users
