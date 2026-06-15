const { KnockMgmt } = require('@knocklabs/mgmt');
const mgmt = new KnockMgmt('dummy');
console.log(mgmt.workflows.upsert.toString());
console.log(mgmt.workflows.activate.toString());
