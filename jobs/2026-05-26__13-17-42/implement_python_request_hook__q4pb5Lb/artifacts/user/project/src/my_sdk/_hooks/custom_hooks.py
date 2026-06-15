"""Custom hook implementations for the MySDK."""

import httpx
from typing import Union

from .types import BeforeRequestContext, BeforeRequestHook


class OrganizationIdHook(BeforeRequestHook):
    """A BeforeRequestHook that injects the X-Organization-Id header into every request."""

    def before_request(
        self, hook_ctx: BeforeRequestContext, request: httpx.Request
    ) -> Union[httpx.Request, Exception]:
        headers = dict(request.headers)
        headers["X-Organization-Id"] = "org_12345"
        new_request = httpx.Request(
            method=request.method,
            url=request.url,
            headers=headers,
            content=request.content,
            extensions=request.extensions,
        )
        return new_request
