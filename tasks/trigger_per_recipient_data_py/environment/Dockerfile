FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        knockapi \
        requests \
        google-api-python-client \
        google-auth \
        google-auth-oauthlib \
        google-auth-httplib2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject && chmod 0755 /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Knock per-recipient email trigger task environment with the knockapi Python SDK and Gmail verification dependencies."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - knockapi: Knock Python SDK used by the task (workflows.trigger)
#   - requests: used by the task and verifier for Knock Management API calls
#   - google-api-python-client + google-auth*: used by the verifier to query Gmail
#   - /home/user/myproject: working directory for the task script and output.log
