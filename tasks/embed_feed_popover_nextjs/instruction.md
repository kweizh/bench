# Embed Knock NotificationFeedPopover in a Next.js App

## Background
Knock provides a pre-built React in-app feed UI (the `NotificationFeedPopover`) that connects to a Knock in-app feed channel and renders messages produced by Knock workflows in real time. In this task, you will build a small Next.js application that embeds Knock's pre-built popover UI and wire it to an in-app feed workflow that you provision in Knock.

## Requirements
- Read `run-id` from the `ZEALT_RUN_ID` environment variable and use it to scope all run-specific resources.
- Provision a Knock in-app workflow in the `development` environment with key `popover-demo-${run-id}` using the Management API (or CLI) authenticated by `KNOCK_SERVICE_TOKEN`. The workflow must:
  - Contain a single in-app feed step that targets the in-app feed channel with channel key `in-app`.
  - Render the trigger payload field `data.body` as the notification body using a Liquid expression (e.g., `{{ data.body }}`).
  - Be **active** in the `development` environment so it can be triggered with the environment API key.
- Build a Next.js application (App Router) at `/home/user/myproject` that:
  - Uses `@knocklabs/react` to render Knock's pre-built popover UI on the root route `/`.
  - Wires the UI to the in-app feed channel using `NEXT_PUBLIC_KNOCK_PUBLIC_API_KEY` and `NEXT_PUBLIC_KNOCK_FEED_CHANNEL_ID` (which mirror `KNOCK_PUBLIC_API_TOKEN` and `KNOCK_INAPP_FEED_CHANNEL_ID`).
  - Identifies the current user with id `popover-user-${run-id}` so the embedded feed loads messages addressed to that recipient.
  - Renders a `NotificationIconButton` and a `NotificationFeedPopover` together; the popover must open when the icon button is clicked and close when its `onClose` callback fires.
  - Imports the Knock stylesheet (`@knocklabs/react/dist/index.css`) so the popover renders with default styling.

## Implementation Hints
- Use the Knock Management API SDK (`@knocklabs/mgmt`) or the Knock CLI to upsert and activate the workflow. Remember that upserts target the `development` environment and that the trigger API requires the workflow to be active in that environment.
- The popover requires a `buttonRef` pointing at the `NotificationIconButton`, plus `isVisible` / `onClose` state that you manage in a client component.
- Wrap the Knock UI in both `KnockProvider` (with the public API key and user) and `KnockFeedProvider` (with the feed channel id).
- The Next.js page that renders Knock components must be a client component (`"use client"`).
- Run the app on port `3000` and start it with `npm start` after producing a production build (`npm run build`).

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Start command: `npm start`
- Port: `3000`
- The Next.js app must build successfully with `npm run build` before being started.
- Workflow provisioned in Knock:
  - Key: `popover-demo-${run-id}` where `run-id` is read from `ZEALT_RUN_ID`.
  - Active in the `development` environment.
  - Contains an in-app feed step bound to channel key `in-app` whose template renders `data.body`.
- Web app routes:
  - `GET /`: returns HTTP 200 and serves an HTML page whose rendered DOM contains:
    - A notification icon button element with CSS class `rnf-notification-icon-button` (the default class emitted by Knock's `NotificationIconButton`).
    - A reference to the Knock React stylesheet (the CSS class names produced by `@knocklabs/react` such as `rnf-*` must appear in the page).
  - Clicking the notification icon button must reveal a popover element with CSS class `rnf-notification-feed-popover` (the default class emitted by Knock's `NotificationFeedPopover`).
  - After Knock workflow `popover-demo-${run-id}` is triggered with `recipients: ["popover-user-${run-id}"]` and `data: {"body": "hello from popover ${run-id}"}`, the popover content must display the text `hello from popover ${run-id}` once it is opened.

