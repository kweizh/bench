
import sys
import httpx
try:
    from my_sdk import MySdk
except ImportError:
    print("my_sdk not found")
    sys.exit(1)

class MockTransport(httpx.BaseTransport):
    def __init__(self):
        self.request = None

    def handle_request(self, request):
        self.request = request
        return httpx.Response(200, json={"message": "ok"})

transport = MockTransport()
client = httpx.Client(transport=transport)
sdk = MySdk(client=client)

method_called = False
for attr in dir(sdk):
    if not attr.startswith("_"):
        obj = getattr(sdk, attr)
        if hasattr(obj, "get_hello"):
            obj.get_hello()
            method_called = True
            break
        if attr == "get_hello":
            obj()
            method_called = True
            break

if not method_called:
    req = client.build_request("GET", "https://api.example.com/hello")
    if hasattr(sdk, "sdk_configuration") and hasattr(sdk.sdk_configuration, "hooks"):
        try:
            from my_sdk.hooks.types import BeforeRequestContext
            context = BeforeRequestContext(hook_ctx_name="dummy", operation_id="dummy", security_source=None)
            req = sdk.sdk_configuration.hooks.before_request(context, req)
        except Exception as e:
            print(f"Error calling hook directly: {e}")
    else:
        print("Could not find hooks in SDK configuration")
        sys.exit(1)
    transport.request = req

if not transport.request:
    print("No request made")
    sys.exit(1)

if transport.request.headers.get("X-Organization-Id") != "org_12345":
    print(f"Header missing or wrong: {transport.request.headers}")
    sys.exit(1)

print("SUCCESS")
