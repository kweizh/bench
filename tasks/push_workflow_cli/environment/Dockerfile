FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nodejs && \
    npm install -g @knocklabs/cli@1.1.2 && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/knock-project && chmod 0755 /home/user/knock-project

LABEL Author="generate-harbor-tasks"
LABEL Description="Knock CLI task environment with Node.js v24, @knocklabs/cli, and an empty Knock project directory."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (required by @knocklabs/cli)
#   - @knocklabs/cli installed globally so the `knock` binary is available
#   - python3 `requests` for HTTP verification against the Knock Management API
#   - /home/user/knock-project: empty project directory the executor will initialize
