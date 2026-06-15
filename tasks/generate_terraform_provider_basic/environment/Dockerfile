FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash golang-go unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then ARCH="arm64"; fi && \
    wget -qO speakeasy.zip "https://github.com/speakeasy-api/speakeasy/releases/download/v1.762.0/speakeasy_linux_${ARCH}.zip" && \
    unzip speakeasy.zip -d /usr/local/bin && \
    rm speakeasy.zip && \
    chmod +x /usr/local/bin/speakeasy

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Speakeasy Terraform provider generation environment with Go and OpenAPI spec."

RUN mkdir -p /home/user/myproject && \
    cd /home/user/myproject && \
    cat >openapi.yaml <<'EOF'
openapi: 3.1.0
info:
  title: Petstore API
  version: 1.0.0
servers:
  - url: http://api.petstore.com/v1
paths:
  /pet:
    post:
      summary: Add a new pet to the store
      operationId: addPet
      requestBody:
        description: Pet object that needs to be added to the store
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Pet'
      responses:
        '200':
          description: Successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Pet'
  /pet/{petId}:
    get:
      summary: Find pet by ID
      operationId: getPetById
      parameters:
        - name: petId
          in: path
          description: ID of pet to return
          required: true
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Pet'
components:
  schemas:
    Pet:
      type: object
      required:
        - name
        - photoUrls
      properties:
        id:
          type: integer
          format: int64
        name:
          type: string
          example: doggie
        photoUrls:
          type: array
          items:
            type: string
EOF

# Container contents:
#   - speakeasy installed.
#   - golang-go installed.
#   - /home/user/myproject  — project path
#   - openapi.yaml with Petstore API

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
