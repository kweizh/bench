# MySDK

## Overview

### Available Operations

* [get_hello](#get_hello)

## get_hello

### Example Usage

<!-- UsageSnippet language="python" operationID="getHello" method="get" path="/hello" -->
```python
from my_sdk import MySDK


with MySDK() as ms_client:

    res = ms_client.get_hello()

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.GetHelloResponseBody](../../models/gethelloresponsebody.md)**

### Errors

| Error Type               | Status Code              | Content Type             |
| ------------------------ | ------------------------ | ------------------------ |
| errors.MySDKDefaultError | 4XX, 5XX                 | \*/\*                    |