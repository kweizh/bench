FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip && \
    pip3 install --break-system-packages pytest-json-ctrf PyYAML && \
    wget -q https://github.com/speakeasy-api/speakeasy/releases/download/v1.765.1/speakeasy_linux_amd64.zip -O /tmp/speakeasy.zip && \
    unzip -q /tmp/speakeasy.zip -d /tmp/speakeasy-extract && \
    mv /tmp/speakeasy-extract/speakeasy /usr/local/bin/speakeasy && \
    chmod +x /usr/local/bin/speakeasy && \
    rm -rf /tmp/speakeasy.zip /tmp/speakeasy-extract && \
    wget -q https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq && \
    chmod +x /usr/local/bin/yq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/project && \
    cat >/home/user/project/spec_a.yaml <<'EOF'
openapi: 3.0.3
info:
  title: Users API
  version: 1.0.0
  description: A minimal Users API used for testing the Speakeasy merge command.
servers:
  - url: https://api.example.com/users-svc
paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
      responses:
        '200':
          description: A list of users.
          content:
            application/json:
              schema:
                type: array
                items:
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
        name:
          type: string
        email:
          type: string
          format: email
EOF

RUN cat >/home/user/project/spec_b.yaml <<'EOF'
openapi: 3.0.3
info:
  title: Products API
  version: 1.0.0
  description: A minimal Products API used for testing the Speakeasy merge command.
servers:
  - url: https://api.example.com/products-svc
paths:
  /products:
    get:
      operationId: listProducts
      summary: List all products
      responses:
        '200':
          description: A list of products.
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Product'
components:
  schemas:
    Product:
      type: object
      required:
        - id
        - name
      properties:
        id:
          type: string
        name:
          type: string
        price:
          type: number
          format: float
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Speakeasy CLI v1.765.1 environment with two seeded OpenAPI 3.0 specs in /home/user/project."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip
#   - always required pip3 packages: pytest-json-ctrf, PyYAML (for parsing merged spec in tests)
#   - speakeasy CLI v1.765.1 installed from official GitHub release into /usr/local/bin/speakeasy
#   - yq installed for inspecting YAML if needed
#   - /home/user/project/spec_a.yaml: minimal OpenAPI 3.0 spec containing GET /users
#   - /home/user/project/spec_b.yaml: minimal OpenAPI 3.0 spec containing GET /products
