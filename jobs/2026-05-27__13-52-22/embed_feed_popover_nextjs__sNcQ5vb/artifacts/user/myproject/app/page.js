"use client";

import { useState, useRef } from "react";
import {
  KnockProvider,
  KnockFeedProvider,
  NotificationIconButton,
  NotificationFeedPopover,
} from "@knocklabs/react";

// Import the Knock stylesheet
import "@knocklabs/react/dist/index.css";

const KnockPopover = ({ apiKey, feedChannelId, userId }) => {
  const [isVisible, setIsVisible] = useState(false);
  const buttonRef = useRef(null);

  return (
    <KnockProvider apiKey={apiKey} userId={userId}>
      <KnockFeedProvider feedChannelId={feedChannelId}>
        <>
          <NotificationIconButton
            ref={buttonRef}
            onClick={(e) => setIsVisible(!isVisible)}
          />
          <NotificationFeedPopover
            buttonRef={buttonRef}
            isVisible={isVisible}
            onClose={() => setIsVisible(false)}
          />
        </>
      </KnockFeedProvider>
    </KnockProvider>
  );
};

export default function Home() {
  const apiKey = process.env.NEXT_PUBLIC_KNOCK_PUBLIC_API_KEY;
  const feedChannelId = process.env.NEXT_PUBLIC_KNOCK_FEED_CHANNEL_ID;
  const runId = process.env.NEXT_PUBLIC_ZEALT_RUN_ID;
  const userId = `popover-user-${runId}`;

  return (
    <main style={{ padding: "2rem" }}>
      <h1>Knock Popover Demo</h1>
      <KnockPopover
        apiKey={apiKey}
        feedChannelId={feedChannelId}
        userId={userId}
      />
    </main>
  );
}
