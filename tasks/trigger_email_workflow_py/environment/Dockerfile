FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        requests \
        knockapi \
        google-api-python-client \
        google-auth \
        google-auth-oauthlib && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/knock_task

LABEL Author="generate-harbor-tasks"
LABEL Description="Knock Python SDK task environment for upserting and triggering a Knock email workflow."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Knock Python SDK: knockapi
#   - HTTP client for Management API calls: requests
#   - Gmail verification dependencies: google-api-python-client, google-auth, google-auth-oauthlib
#   - /home/user/knock_task: working directory for the executor's script and log output
