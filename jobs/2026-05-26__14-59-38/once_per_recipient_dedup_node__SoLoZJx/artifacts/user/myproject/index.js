const { KnockMgmt } = require("@knocklabs/mgmt");
const { Knock } = require("@knocklabs/node");
const fs = require("fs");
const path = require("path");

async function run() {
  const runId = process.env.ZEALT_RUN_ID;
  const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
  const apiToken = process.env.KNOCK_API_TOKEN;
  const gmailUserName = process.env.GMAIL_USER_NAME;
  const mailtrapDomain = process.env.MAILTRAP_DOMAIN;

  if (!runId || !serviceToken || !apiToken || !gmailUserName || !mailtrapDomain) {
    console.error("Missing environment variables");
    process.exit(1);
  }

  const workflowKey = `dedup-test-${runId}`;
  const logFilePath = path.join(__dirname, "output.log");

  // 1. Initialize Management Client
  const mgmtClient = new KnockMgmt({
    bearerToken: serviceToken,
  });

  // 1.5 Delete the recipient to ensure a clean state
  console.log(`Deleting recipient: dedup-recipient-${runId}`);
  const knock = new Knock({ apiKey: apiToken });
  try {
    // We try to delete the user. If it fails, it might be because the user doesn't exist.
    await knock.users.delete(`dedup-recipient-${runId}`);
    console.log("Recipient deleted.");
  } catch (e) {
    console.log("Recipient not found or could not be deleted.");
  }

  console.log(`Upserting workflow: ${workflowKey}`);

  // 2. Upsert Workflow
  try {
    const workflow = await mgmtClient.workflows.upsert(workflowKey, {
      workflow: {
        name: `Dedup Test ${runId}`,
        trigger_frequency: "once_per_recipient",
        steps: [
          {
            type: "channel",
            channel_key: "mailtrap",
            ref: "mailtrap-step",
            template: {
              subject: `Dedup test ${runId}`,
              html_body: "This is a test email for deduplication.",
              settings: {
                from_address: `dedup-${runId}@${mailtrapDomain}`,
              },
            },
          },
        ],
      },
    });

    // 3. Activate Workflow in development environment
    await mgmtClient.workflows.activate(workflowKey, {
      environment: "development",
    });

    console.log("Workflow activated. Committing changes...");

    // 3.5 Commit changes to development environment
    // Use a unique message to avoid potential issues with empty commits
    await mgmtClient.commits.commitAll({
      environment: "development",
      message: `Deploying dedup test ${runId} at ${new Date().toISOString()}`,
    });

    console.log("Changes committed. Waiting for propagation...");
    await new Promise((resolve) => setTimeout(resolve, 5000));

    // 4. Initialize Trigger Client
    const knock = new Knock({ apiKey: apiToken });

    const recipient = {
      id: `dedup-recipient-${runId}`,
      email: `${gmailUserName}+receiver-${runId}@gmail.com`,
      name: `Recipient ${runId}`,
    };

    // 5. Trigger Workflow Twice
    const triggerWorkflow = async (label) => {
      const response = await knock.workflows.trigger(workflowKey, {
        data: {},
        recipients: [recipient],
      });
      
      console.log(`${label} response:`, JSON.stringify(response));

      const workflowRunId = (response && response.workflow_run_id) ? response.workflow_run_id : "null";
      fs.appendFileSync(logFilePath, `${label} workflow_run_id: ${workflowRunId}\n`);
      return workflowRunId;
    };

    console.log("First trigger...");
    await triggerWorkflow("First trigger");

    console.log("Second trigger...");
    await triggerWorkflow("Second trigger");

    console.log("Done.");
  } catch (error) {
    console.error("Full Error:", error);
    process.exit(1);
  }
}

run();
