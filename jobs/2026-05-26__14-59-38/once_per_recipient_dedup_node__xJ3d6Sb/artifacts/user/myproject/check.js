const { KnockMgmt } = require('@knocklabs/mgmt');
const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
const knockMgmt = new KnockMgmt({ serviceToken });
const runId = process.env.ZEALT_RUN_ID;
async function main() {
  const workflow = await knockMgmt.workflows.retrieve(`dedup-test-${runId}`, { environment: 'development' });
  console.log(workflow.trigger_frequency);
}
main();
