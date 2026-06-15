const { Knock } = require('@knocklabs/node');
const knock = new Knock({ apiKey: 'dummy-key' });
console.log(knock.workflows.trigger.toString());
