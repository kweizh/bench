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
RUN mkdir -p /home/user/cancel_task

LABEL Author="generate-harbor-tasks"
LABEL Description="Knock cancel-workflow-run task: Node.js v24 environment with an empty /home/user/cancel_task project directory."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (for installing @knocklabs/mgmt and @knocklabs/node at task time)
#   - pip3 packages required by tests: requests (Knock Management & public APIs),
#       google-api-python-client / google-auth / google-auth-oauthlib (Gmail inbox check)
#   - /home/user/cancel_task: empty project directory where the agent builds the Node.js project
