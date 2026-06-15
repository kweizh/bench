const { KnockMgmt } = require("@knocklabs/mgmt");
const fs = require("fs");

async function run() {
  const runId = process.env.ZEALT_RUN_ID;
  const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
  const workflowKey = `order-confirmation-${runId}`;
  const workflowName = `Order Confirmation ${runId}`;
  const logFile = "/home/user/knock_task/output.log";

  const knockMgmt = new KnockMgmt({ bearerToken: serviceToken });

  const workflowData = {
    name: workflowName,
    trigger_data_json_schema: {
      type: "object",
      properties: {
        order_id: { type: "string" },
        total_amount: { type: "number" },
        customer_email: { type: "string", format: "email" },
      },
      required: ["order_id", "total_amount", "customer_email"],
    },
    steps: [
      {
        type: "channel",
        channel_key: "in-app",
        ref: "in-app-step",
        template: {
          markdown_body: "Order {{ data.order_id }} for {{ data.total_amount }} has been confirmed.",
          action_url: "https://example.com",
        },
      },
    ],
  };

  try {
    console.log(`Upserting workflow: ${workflowKey}`);
    await knockMgmt.workflows.upsert(workflowKey, {
      environment: "development",
      workflow: workflowData,
    }).catch(e => {
        if (e.error && e.error.errors) {
            console.error("Validation Errors:", JSON.stringify(e.error.errors, null, 2));
        }
        throw e;
    });

    console.log(`Activating workflow: ${workflowKey}`);
    await knockMgmt.workflows.activate(workflowKey, {
      environment: "development",
    }).catch(e => {
        if (e.error && e.error.errors) {
            console.error("Activation Errors:", JSON.stringify(e.error.errors, null, 2));
        }
        throw e;
    });

    fs.appendFileSync(logFile, `Workflow Key: ${workflowKey}\n`);
    fs.appendFileSync(logFile, `Workflow Active: true\n`);
    
    console.log("Upsert and activation complete.");
  } catch (error) {
    console.error("Error in upsert_workflow.js:", error);
    process.exit(1);
  }
}

run();
