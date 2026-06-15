const fs = require("fs");
const path = require("path");
const KnockMgmt = require("@knocklabs/mgmt");

const runId = process.env.ZEALT_RUN_ID;
const serviceToken = process.env.KNOCK_SERVICE_TOKEN;

if (!runId) {
  throw new Error("ZEALT_RUN_ID environment variable is required.");
}

if (!serviceToken) {
  throw new Error("KNOCK_SERVICE_TOKEN environment variable is required.");
}

const workflowKey = `order-confirmation-${runId}`;
const workflowName = `Order Confirmation ${runId}`;
const logPath = path.join(__dirname, "output.log");

const client = new KnockMgmt({
  serviceToken,
});

const workflow = {
  name: workflowName,
  trigger_data_json_schema: {
    type: "object",
    required: ["order_id", "total_amount", "customer_email"],
    properties: {
      order_id: { type: "string" },
      total_amount: { type: "number" },
      customer_email: { type: "string", format: "email" },
    },
  },
  steps: [
    {
      name: "In-app order confirmation",
      ref: "in_app_order_confirmation",
      type: "channel",
      channel_key: "in-app",
      template: {
        markdown_body:
          "Order {{ data.order_id }} confirmed with total {{ data.total_amount }}.",
        action_url: "https://example.com/orders/{{ data.order_id }}",
      },
    },
  ],
};

const writeLogLine = (line) => {
  fs.appendFileSync(logPath, `${line}\n`);
};

const main = async () => {
  fs.writeFileSync(logPath, "");

  await client.workflows.upsert(workflowKey, {
    environment: "development",
    workflow,
    commit: true,
    commit_message: `Upsert order confirmation workflow ${runId}`,
  });

  const activation = await client.workflows.activate(workflowKey, {
    environment: "development",
    status: true,
  });

  writeLogLine(`Workflow Key: ${workflowKey}`);
  writeLogLine(`Workflow Active: ${activation.workflow.active}`);
};

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
