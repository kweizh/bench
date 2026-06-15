const KnockMgmt = require("@knocklabs/mgmt").default;
const knockMgmt = new KnockMgmt(process.env.KNOCK_SERVICE_TOKEN);

async function test() {
  try {
    const wf = await knockMgmt.workflows.upsert("test-workflow", {
      environment: "development",
      workflow: {
        name: "Test Workflow",
        trigger_data_json_schema: {
          type: "object",
          properties: {
            channel_preference: { type: "string" }
          },
          required: ["channel_preference"]
        },
        steps: [
          {
            ref: "branch_step",
            type: "branch",
            name: "Branch on channel preference",
            branches: [
              {
                name: "Email Branch",
                terminates: true,
                conditions: {
                  all: [
                    {
                      argument: "email",
                      variable: "data.channel_preference",
                      operator: "equal_to"
                    }
                  ]
                },
                steps: [
                  {
                    ref: "email_step",
                    type: "channel",
                    channel_key: "mailtrap",
                    template: {
                      subject: "Hello {{ recipient.name }}",
                      html_body: "This is an email for {{ recipient.name }}",
                      settings: {}
                    }
                  }
                ]
              },
              {
                name: "Dummy Branch",
                terminates: false,
                conditions: {
                  all: [
                    {
                      argument: "dummy",
                      variable: "data.channel_preference",
                      operator: "equal_to"
                    }
                  ]
                },
                steps: []
              },
              {
                name: "Default Branch",
                terminates: true,
                default: true,
                steps: [
                  {
                    ref: "in_app_step",
                    type: "channel",
                    channel_key: "in-app",
                    template: {
                      markdown_body: "This is an in-app message for {{ recipient.name }}",
                      action_url: "https://example.com"
                    }
                  }
                ]
              }
            ]
          }
        ]
      }
    });
    console.log("Success:", JSON.stringify(wf, null, 2));
  } catch (e) {
    if (e.error) {
      console.error("Error:", JSON.stringify(e.error, null, 2));
    } else {
      console.error("Error:", e);
    }
  }
}

test();
