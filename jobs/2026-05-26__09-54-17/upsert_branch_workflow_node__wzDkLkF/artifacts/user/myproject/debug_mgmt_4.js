const { KnockMgmt } = require("@knocklabs/mgmt");
const mgmtClient = new KnockMgmt({ bearerToken: "test" });
console.log("Mgmt Prototypes:", Object.keys(Object.getPrototypeOf(mgmtClient)));
console.log("Commits Prototypes:", Object.keys(Object.getPrototypeOf(mgmtClient.commits)));
