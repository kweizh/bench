const { KnockMgmt } = require('@knocklabs/mgmt')

const serviceToken = process.env.KNOCK_SERVICE_TOKEN
const runId = process.env.ZEALT_RUN_ID

if (!serviceToken) {
  console.error('KNOCK_SERVICE_TOKEN is required')
  process.exit(1)
}

if (!runId) {
  console.error('ZEALT_RUN_ID is required')
  process.exit(1)
}

const knock = new KnockMgmt(serviceToken)

async function triggerWorkflow() {
  const workflowKey = `popover-demo-${runId}`
  const userId = `popover-user-${runId}`
  const environment = 'development'

  console.log(`Triggering workflow: ${workflowKey}`)
  console.log(`User ID: ${userId}`)
  console.log(`Environment: ${environment}`)

  try {
    // Trigger the workflow
    console.log('Triggering workflow...')
    const result = await knock.workflows.run(workflowKey, {
      environment: environment,
      recipients: [userId],
      data: {
        body: `hello from popover ${runId}`,
      },
    })
    console.log('Workflow triggered successfully')
    console.log('Result:', JSON.stringify(result, null, 2))

    console.log(`\nWorkflow "${workflowKey}" has been triggered with data:`)
    console.log(`  recipients: ["${userId}"]`)
    console.log(`  data: { body: "hello from popover ${runId}" }`)
  } catch (error) {
    console.error('Error triggering workflow:', error.response?.data || error.message)
    if (error.error?.errors) {
      console.error('Validation errors:', JSON.stringify(error.error.errors, null, 2))
    }
    throw error
  }
}

triggerWorkflow()
  .then(() => {
    console.log('Workflow trigger completed successfully')
    process.exit(0)
  })
  .catch((error) => {
    console.error('Workflow trigger failed:', error)
    process.exit(1)
  })