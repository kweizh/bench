FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/knock_task && \
    cd /home/user/knock_task && \
    cat >package.json <<'EOF'
{
  "name": "knock-trigger-data-schema-task",
  "version": "1.0.0",
  "private": true,
  "type": "commonjs",
  "dependencies": {
    "@knocklabs/mgmt": "^0.5.0",
    "@knocklabs/node": "^1.0.0"
  }
}
EOF

RUN cd /home/user/knock_task && \
    npm install --no-audit --no-fund

LABEL Author="generate-harbor-tasks"
LABEL Description="Node.js environment with Knock @knocklabs/mgmt and @knocklabs/node SDKs preinstalled in /home/user/knock_task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: requests (used by final state tests to verify via Knock management/API endpoints)
#   - Node.js v24 with npm
#   - /home/user/knock_task: Node project with @knocklabs/mgmt and @knocklabs/node installed for the executor to use
