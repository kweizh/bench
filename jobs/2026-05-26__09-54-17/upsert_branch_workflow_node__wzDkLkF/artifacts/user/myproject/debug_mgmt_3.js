const { KnockMgmt } = require("@knocklabs/mgmt");
const mgmtClient = new KnockMgmt({ bearerToken: "test" });
console.log("Commits Keys:", Object.keys(mgmtClient.commits));
