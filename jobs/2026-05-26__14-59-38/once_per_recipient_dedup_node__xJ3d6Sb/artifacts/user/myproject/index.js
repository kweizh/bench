const { KnockMgmt } = require('@knocklabs/mgmt');
const { Knock: KnockNode } = require('@knocklabs/node');
const fs = require('fs');
const path = require('path');

const runId = process.env.ZEALT_RUN_ID;
const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
const apiToken = process.env.KNOCK_API_TOKEN;
const gmailUser = process.env.GMAIL_USER_NAME;
const mailtrapDomain = process.env.MAILTRAP_DOMAIN;

if (!runId || !serviceToken || !apiToken || !gmailUser || !mailtrapDomain) {
  console.error("Missing required environment variables");
  process.exit(1);
}

const knockMgmt = new KnockMgmt({ serviceToken });
const knockNode = new KnockNode({ apiKey: apiToken });

const workflowKey = `dedup-test-${runId}`;

async function main() {
  console.log(`Upserting workflow ${workflowKey}...`);
  // 1. Upsert workflow
  const upsertRes = await knockMgmt.workflows.upsert(workflowKey, {
    environment: 'development',
    workflow: {
      name: `Dedup Test ${runId}`,
      trigger_frequency: 'once_per_recipient',
      steps: [
        {
          type: 'channel',
          ref: 'email_step',
          channel_key: 'mailtrap',
          channel_overrides: {
            from_address: `dedup-${runId}@${mailtrapDomain}`
          },
          template: {
            subject: `dedup-test-${runId}`,
            html_body: `<p>Hello {{ recipient.name }}</p>`,
            settings: {
              layout_key: null
            }
          }
        }
      ]
    }
  });

  console.log('Workflow upserted. Committing...');
  await knockMgmt.commits.commitAll({ environment: 'development' });

  console.log('Workflow committed. Activating...');

  // 2. Activate workflow
  await knockMgmt.workflows.activate(workflowKey, {
    environment: 'development'
  });

  console.log('Workflow activated. Triggering first time...');

  // 3. Trigger workflow twice
  const recipient = {
    id: `dedup-recipient-${runId}`,
    email: `${gmailUser}+receiver-${runId}@gmail.com`,
    name: `Recipient ${runId}`
  };

  const firstTrigger = await knockNode.workflows.trigger(workflowKey, {
    recipients: [recipient],
    data: {}
  });

  console.log('First trigger complete. Triggering second time...');

  const secondTrigger = await knockNode.workflows.trigger(workflowKey, {
    recipients: [recipient],
    data: {}
  });

  console.log('Second trigger complete. Writing logs...');

  const logFile = path.join(__dirname, 'output.log');
  const logLines = [
    `First trigger workflow_run_id: ${firstTrigger?.workflow_run_id || 'null'}`,
    `Second trigger workflow_run_id: ${secondTrigger?.workflow_run_id || 'null'}`
  ];

  fs.writeFileSync(logFile, logLines.join('\n') + '\n');
  console.log('Done.');
}

main().catch(err => {
  console.error('Error occurred:', err.response?.data || err);
  process.exit(1);
});
