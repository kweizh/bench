import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/sdk"

def test_typescript_compilation():
    """Verify that the project compiles without TypeScript errors."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"

def test_correlation_ts_exists_and_implements_interface():
    """Verify that correlation.ts exists and implements AfterErrorHook."""
    hook_file = os.path.join(PROJECT_DIR, "src", "hooks", "custom", "correlation.ts")
    assert os.path.isfile(hook_file), f"Custom hook file {hook_file} does not exist."
    
    with open(hook_file, "r") as f:
        content = f.read()
    
    assert "implements AfterErrorHook" in content or "AfterErrorHook" in content, \
        "Expected CorrelationHook to implement AfterErrorHook."
    assert "CorrelationHook" in content, "Expected CorrelationHook class to be defined."

def test_registration_ts_registers_hook():
    """Verify that registration.ts registers the new hook."""
    registration_file = os.path.join(PROJECT_DIR, "src", "hooks", "registration.ts")
    
    with open(registration_file, "r") as f:
        content = f.read()
    
    assert "registerAfterErrorHook" in content, \
        "Expected hooks.registerAfterErrorHook to be called in registration.ts."
    assert "CorrelationHook" in content, \
        "Expected CorrelationHook to be imported and used in registration.ts."

def test_hook_runtime_behavior():
    """Verify the runtime behavior of the hook by running a test script."""
    test_script_path = os.path.join(PROJECT_DIR, "test_runner.ts")
    
    test_script_content = """
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
"""
    
    with open(test_script_path, "w") as f:
        f.write(test_script_content)
        
    # Compile the test script
    compile_result = subprocess.run(
        ["npx", "tsc", "test_runner.ts", "--target", "ES2022", "--module", "NodeNext", "--moduleResolution", "NodeNext"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert compile_result.returncode == 0, f"Failed to compile test script:\n{compile_result.stdout}\n{compile_result.stderr}"
    
    # Run the test script
    run_result = subprocess.run(
        ["node", "test_runner.js"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    assert run_result.returncode == 0, f"Hook runtime test failed:\n{run_result.stdout}\n{run_result.stderr}"
    assert "SUCCESS" in run_result.stdout, f"Hook runtime test did not report SUCCESS:\n{run_result.stdout}"
