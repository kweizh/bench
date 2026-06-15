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

async function validateWorkflow() {
  const workflowKey = `popover-demo-${runId}`

  console.log(`Validating workflow: ${workflowKey}`)

  try {
    const workflowData = {
      workflow: {
        name: `Popover Demo ${runId}`,
        description: 'Demo workflow for Knock popover integration',
        steps: [
          {
            key: 'in-app-step',
            ref: 'in-app-step',
            type: 'channel',
            channel_key: 'in-app',
            template: {
              subject: 'New Notification',
              markdown_body: '{{ data.body }}',
              action_url: 'https://example.com',
            },
          },
        ],
      },
    }

    console.log('Workflow data:', JSON.stringify(workflowData, null, 2))

    // Validate the workflow
    console.log('Validating workflow...')
    const result = await knock.workflows.validate(workflowKey, {
      environment: 'development',
      ...workflowData,
    })
    console.log('Workflow validation result:', JSON.stringify(result, null, 2))
  } catch (error) {
    console.error('Error validating workflow:', error.response?.data || error.message)
    if (error.error?.errors) {
      console.error('Validation errors:', JSON.stringify(error.error.errors, null, 2))
    }
    throw error
  }
}

validateWorkflow()
  .then(() => {
    console.log('Workflow validation completed successfully')
    process.exit(0)
  })
  .catch((error) => {
    console.error('Workflow validation failed:', error)
    process.exit(1)
  })