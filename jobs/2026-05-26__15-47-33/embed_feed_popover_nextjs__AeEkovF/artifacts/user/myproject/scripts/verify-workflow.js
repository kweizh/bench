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

async function verifyWorkflow() {
  const workflowKey = `popover-demo-${runId}`
  const environment = 'development'

  console.log(`Verifying workflow: ${workflowKey}`)
  console.log(`Environment: ${environment}`)

  try {
    // Retrieve the workflow
    console.log('Retrieving workflow...')
    const workflow = await knock.workflows.retrieve(workflowKey, {
      environment: environment,
    })
    console.log('Workflow retrieved successfully')
    console.log('Workflow details:', JSON.stringify(workflow, null, 2))

    // Verify key requirements
    console.log('\n=== Verification Results ===')
    console.log(`✅ Workflow Key: ${workflow.key}`)
    console.log(`✅ Workflow Name: ${workflow.name}`)
    console.log(`✅ Active: ${workflow.active}`)
    console.log(`✅ Environment: ${environment}`)
    console.log(`✅ Number of Steps: ${workflow.steps.length}`)

    if (workflow.steps.length > 0) {
      const step = workflow.steps[0]
      console.log(`✅ Step Type: ${step.type}`)
      console.log(`✅ Step Channel Key: ${step.channel_key}`)
      console.log(`✅ Step Template Body: ${step.template.markdown_body}`)
    }
  } catch (error) {
    console.error('Error verifying workflow:', error.response?.data || error.message)
    if (error.error?.errors) {
      console.error('Validation errors:', JSON.stringify(error.error.errors, null, 2))
    }
    throw error
  }
}

verifyWorkflow()
  .then(() => {
    console.log('\nWorkflow verification completed successfully')
    process.exit(0)
  })
  .catch((error) => {
    console.error('Workflow verification failed:', error)
    process.exit(1)
  })