const { Knock } = require("@knocklabs/node");
const fs = require("fs");

async function run() {
  const runId = process.env.ZEALT_RUN_ID;
  const apiKey = process.env.KNOCK_API_TOKEN;
  const workflowKey = `order-confirmation-${runId}`;
  const logFile = "/home/user/knock_task/output.log";

  const knock = new Knock(apiKey);

  // 1. Trigger with valid payload
  try {
    console.log("Triggering valid payload...");
    const validResponse = await knock.workflows.trigger(workflowKey, {
      recipients: [`recipient-${runId}`],
      data: {
        order_id: "order-123",
        total_amount: 99.99,
        customer_email: "test@example.com",
      },
    });
    fs.appendFileSync(logFile, `Valid Trigger Workflow Run ID: ${validResponse.workflow_run_id}\n`);
    console.log(`Valid trigger successful: ${validResponse.workflow_run_id}`);
  } catch (error) {
    console.error("Error triggering valid payload:", error);
  }

  // 2. Trigger with invalid payload (total_amount as string)
  try {
    console.log("Triggering invalid payload...");
    await knock.workflows.trigger(workflowKey, {
      recipients: [`recipient-${runId}`],
      data: {
        order_id: "order-123",
        total_amount: "99.99", // Should be number
        customer_email: "test@example.com",
      },
    });
    console.log("Invalid trigger unexpectedly succeeded.");
  } catch (error) {
    console.log(`Invalid trigger failed as expected: ${error.status} ${error.message}`);
    fs.appendFileSync(logFile, `Invalid Trigger Status: ${error.status}\n`);
  }
}

run();
