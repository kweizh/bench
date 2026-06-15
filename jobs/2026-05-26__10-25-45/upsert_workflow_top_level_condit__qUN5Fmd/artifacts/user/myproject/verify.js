const { KnockMgmt } = require('@knocklabs/mgmt');
async function verify() {
  const mgmt = new KnockMgmt({ serviceToken: process.env.KNOCK_SERVICE_TOKEN });
  const runId = process.env.ZEALT_RUN_ID;
  const wf = await mgmt.workflows.retrieve(`top-level-conditions-${runId}`, { environment: 'development' });
  console.log("active:", wf.active);
  console.log("conditions:", JSON.stringify(wf.conditions, null, 2));
  console.log("steps:", JSON.stringify(wf.steps, null, 2));
}
verify().catch(console.error);
