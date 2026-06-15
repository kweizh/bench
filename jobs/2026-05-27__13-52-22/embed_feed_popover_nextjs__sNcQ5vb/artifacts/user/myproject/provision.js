const { KnockMgmt } = require("@knocklabs/mgmt");

async function provisionWorkflow() {
  const runId = process.env.ZEALT_RUN_ID;
  const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
  const workflowKey = `popover-demo-${runId}`;

  const knock = new KnockMgmt({ apiKey: serviceToken });

  console.log(`Provisioning workflow: ${workflowKey}`);

  try {
    const workflow = await knock.workflows.upsert(workflowKey, {
      workflow: {
          name: `Popover Demo ${runId}`,
          active: true,
          steps: [
            {
              type: "channel",
              channel_key: "in-app",
              ref: "in_app_feed",
              template: {
                markdown_body: "{{ data.body }}",
                action_url: "https://knock.app"
              },
            },
          ],
      }
    });

    console.log(`Workflow ${workflowKey} upserted.`);
    
    try {
        await knock.workflows.activate(workflowKey, {
            environment: "development"
        });
        console.log(`Workflow ${workflowKey} activated in development.`);
    } catch (e) {
        console.log("Activation step failed or not needed:", e.message);
    }

  } catch (error) {
    if (error.error && error.error.errors) {
        console.error("Detailed errors:", JSON.stringify(error.error.errors, null, 2));
    }
    console.error("Error provisioning workflow:", error);
    process.exit(1);
  }
}

provisionWorkflow();
