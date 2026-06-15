FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        requests \
        google-api-python-client \
        google-auth \
        google-auth-oauthlib && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Pre-create the project directory and pre-install the Knock Node SDKs so the
# executor can `require` them directly without needing network access during
# the task.
RUN mkdir -p /home/user/myproject && \
    cd /home/user/myproject && \
    npm init -y >/dev/null && \
    npm install --no-audit --no-fund \
        @knocklabs/mgmt@latest \
        @knocklabs/node@latest

LABEL Author="generate-harbor-tasks"
LABEL Description="Knock once_per_recipient deduplication task: Node.js + Python + pre-installed @knocklabs/mgmt and @knocklabs/node."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - additional pip3 packages for verification: requests, google-api-python-client, google-auth, google-auth-oauthlib
#   - Node.js v24 toolchain (node + npm) for running the Knock SDKs
#   - /home/user/myproject: project directory with package.json and pre-installed
#         @knocklabs/mgmt (Management API SDK) and @knocklabs/node (API SDK).
