const { KnockMgmt } = require("@knocklabs/mgmt");
const mgmtClient = new KnockMgmt({ bearerToken: "test" });
console.log("Mgmt Keys:", Object.keys(mgmtClient));
