const { KnockMgmt } = require("@knocklabs/mgmt");
const mgmtClient = new KnockMgmt({ bearerToken: "test" });
console.log("Commits:", mgmtClient.commits);
console.log("Commits Proto:", Object.getPrototypeOf(mgmtClient.commits));
console.log("Commits Proto Proto:", Object.getPrototypeOf(Object.getPrototypeOf(mgmtClient.commits)));
