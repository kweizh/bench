const { KnockMgmt } = require("@knocklabs/mgmt");
console.log("Keys:", Object.keys(new KnockMgmt({ bearerToken: "test" }).workflows));
