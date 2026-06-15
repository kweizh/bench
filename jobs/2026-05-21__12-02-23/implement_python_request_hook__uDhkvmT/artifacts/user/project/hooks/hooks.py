import httpx
from .._hooks.types import BeforeRequestContext, BeforeRequestHook

class MyHook(BeforeRequestHook):
    def before_request(self, hook_ctx: BeforeRequestContext, request: httpx.Request) -> httpx.Request:
        request.headers["X-Organization-Id"] = "org_12345"
        return request
