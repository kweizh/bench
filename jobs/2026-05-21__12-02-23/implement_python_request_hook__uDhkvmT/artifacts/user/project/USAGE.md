<!-- Start SDK Example Usage [usage] -->
```python
# Synchronous Example
from my_sdk import MySDK


with MySDK() as ms_client:

    res = ms_client.get_hello()

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.

```python
# Asynchronous Example
import asyncio
from my_sdk import MySDK

async def main():

    async with MySDK() as ms_client:

        res = await ms_client.get_hello_async()

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->