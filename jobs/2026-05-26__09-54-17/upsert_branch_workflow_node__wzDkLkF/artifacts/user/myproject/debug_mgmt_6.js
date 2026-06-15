const { KnockMgmt } = require("@knocklabs/mgmt");
const mgmtClient = new KnockMgmt({ bearerToken: "test" });
console.log("Commits Proto Keys:", Object.getOwnPropertyNames(Object.getPrototypeOf(mgmtClient.commits)));
console.log("Workflows Proto Keys:", Object.getOwnPropertyNames(Object.getPrototypeOf(mgmtClient.workflows)));
