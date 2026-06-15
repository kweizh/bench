const fs = require("fs");
const path = require("path");
const Knock = require("@knocklabs/node");

const runId = process.env.ZEALT_RUN_ID;
const apiKey = process.env.KNOCK_API_TOKEN;

if (!runId) {
  throw new Error("ZEALT_RUN_ID environment variable is required.");
}

if (!apiKey) {
  throw new Error("KNOCK_API_TOKEN environment variable is required.");
}

const workflowKey = `order-confirmation-${runId}`;
const logPath = path.join(__dirname, "output.log");
const recipient = `recipient-${runId}`;

const client = new Knock({
  apiKey,
});

const writeLogLine = (line) => {
  fs.appendFileSync(logPath, `${line}\n`);
};

const main = async () => {
  const validPayload = {
    order_id: `order-${runId}`,
    total_amount: 125.5,
    customer_email: `customer-${runId}@example.com`,
  };

  const validResponse = await client.workflows.trigger(workflowKey, {
    recipients: [recipient],
    data: validPayload,
  });

  writeLogLine(`Valid Trigger Workflow Run ID: ${validResponse.workflow_run_id}`);

  try {
    await client.workflows.trigger(workflowKey, {
      recipients: [recipient],
      data: {
        order_id: `order-${runId}`,
        total_amount: "125.5",
        customer_email: `customer-${runId}@example.com`,
      },
    });
  } catch (error) {
    const status = error && error.status ? error.status : "unknown";
    const message = error && error.message ? error.message : String(error);
    writeLogLine(`Invalid Trigger Status: ${status}`);
    writeLogLine(`Invalid Trigger Message: ${message}`);
    return;
  }

  throw new Error("Invalid trigger did not fail as expected.");
};

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
