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

async function provisionWorkflow() {
  const workflowKey = `popover-demo-${runId}`
  const environment = 'development'

  console.log(`Provisioning workflow: ${workflowKey} in environment: ${environment}`)

  try {
    // Create or update the workflow using upsert
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

    // Create the workflow using upsert
    console.log('Creating workflow...')
    await knock.workflows.upsert(workflowKey, {
      environment: 'development',
      ...workflowData,
    })
    console.log('Workflow created successfully')

    // Activate the workflow in development environment
    console.log('Activating workflow in development environment...')
    await knock.workflows.activate(workflowKey, {
      environment: 'development',
      status: true,
    })
    console.log('Workflow activated successfully')

    console.log(`\nWorkflow "${workflowKey}" is now active in ${environment} environment`)
  } catch (error) {
    console.error('Error provisioning workflow:', error.response?.data || error.message)
    if (error.error?.errors) {
      console.error('Validation errors:', JSON.stringify(error.error.errors, null, 2))
    }
    throw error
  }
}

provisionWorkflow()
  .then(() => {
    console.log('Workflow provisioning completed successfully')
    process.exit(0)
  })
  .catch((error) => {
    console.error('Workflow provisioning failed:', error)
    process.exit(1)
  })