const { Knock } = require('@knocklabs/node');
const knock = new Knock('dummy-key');
console.log(Object.keys(knock.workflows));
