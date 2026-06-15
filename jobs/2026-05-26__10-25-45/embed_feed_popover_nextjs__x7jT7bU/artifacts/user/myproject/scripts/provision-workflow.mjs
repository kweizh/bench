import KnockMgmt from "@knocklabs/mgmt";

const runId = process.env.ZEALT_RUN_ID;
const serviceToken = process.env.KNOCK_SERVICE_TOKEN;

if (!runId) {
  console.error("ZEALT_RUN_ID is required to provision the workflow.");
  process.exit(1);
}

if (!serviceToken) {
  console.error("KNOCK_SERVICE_TOKEN is required to provision the workflow.");
  process.exit(1);
}

const workflowKey = `popover-demo-${runId}`;

const knock = new KnockMgmt({ serviceToken });

await knock.workflows.upsert(workflowKey, {
  environment: "development",
  workflow: {
    name: `Popover demo ${runId}`,
    steps: [
      {
        ref: "in_app_feed",
        name: "In-app feed",
        type: "channel",
        channel_key: "in-app",
        channel_type: "in_app_feed",
        template: {
          markdown_body: "{{ data.body }}",
          action_url: "https://example.com",
        },
      },
    ],
  },
});

await knock.workflows.activate(workflowKey, {
  environment: "development",
  status: true,
});

console.log(`Provisioned and activated workflow ${workflowKey}.`);
