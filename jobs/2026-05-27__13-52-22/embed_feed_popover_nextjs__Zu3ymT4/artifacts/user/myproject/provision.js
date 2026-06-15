const { KnockMgmt } = require("@knocklabs/mgmt");

async function main() {
  const runId = process.env.ZEALT_RUN_ID;
  const knock = new KnockMgmt({ apiKey: process.env.KNOCK_SERVICE_TOKEN });
  const workflowKey = `popover-demo-${runId}`;

  try {
    console.log("Upserting workflow...");
    await knock.workflows.upsert(workflowKey, {
      environment: "development",
      workflow: {
        name: `Popover Demo ${runId}`,
        steps: [
          {
            ref: "in-app-step",
            type: "channel",
            channel_key: "in-app",
            template: {
              markdown_body: "{{ data.body }}",
              action_url: "https://example.com"
            }
          }
        ]
      }
    });
    console.log("Workflow upserted.");

    console.log("Activating workflow...");
    await knock.workflows.activate(workflowKey, {
      environment: "development",
      status: true
    });
    console.log("Workflow activated.");
  } catch (error) {
    if (error.error && error.error.errors) {
      console.error("Errors:", JSON.stringify(error.error.errors, null, 2));
    } else {
      console.error("Error:", error);
    }
  }
}

main();