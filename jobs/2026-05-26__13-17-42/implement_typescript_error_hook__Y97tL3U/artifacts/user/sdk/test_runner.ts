
import { CorrelationHook } from "./src/hooks/custom/correlation.js";

async function runTest() {
    const hook = new CorrelationHook();
    
    // Mock Response for 500
    const headers500 = new Headers();
    headers500.set("x-correlation-id", "12345");
    const response500 = new Response(null, { status: 500, headers: headers500 });
    
    let threwError = false;
    try {
        await hook.afterError({ operationID: "test" }, response500, new Error("Original Error"));
    } catch (e: any) {
        threwError = true;
        if (e.message !== "Correlation Error: 12345") {
            console.error("FAILED: Expected error message 'Correlation Error: 12345', got: " + e.message);
            process.exit(1);
        }
    }
    
    if (!threwError) {
        console.error("FAILED: Hook did not throw an error for 500 response with correlation ID.");
        process.exit(1);
    }
    
    // Mock Response for 400
    const headers400 = new Headers();
    headers400.set("x-correlation-id", "67890");
    const response400 = new Response(null, { status: 400, headers: headers400 });
    
    try {
        const result = await hook.afterError({ operationID: "test" }, response400, new Error("Original Error"));
        if (!result || result.response !== response400) {
            console.error("FAILED: Hook did not return original response for 400 status.");
            process.exit(1);
        }
    } catch (e) {
        console.error("FAILED: Hook threw an error for 400 response.");
        process.exit(1);
    }
    
    console.log("SUCCESS");
}

runTest().catch(e => {
    console.error(e);
    process.exit(1);
});
