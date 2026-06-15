"use client";

import { useState, useRef } from "react";
import { KnockProvider, KnockFeedProvider, NotificationIconButton, NotificationFeedPopover } from "@knocklabs/react";
import "@knocklabs/react/dist/index.css";

export default function Home() {
  const [isVisible, setIsVisible] = useState(false);
  const notifButtonRef = useRef(null);
  
  const runId = process.env.NEXT_PUBLIC_ZEALT_RUN_ID;
  const userId = `popover-user-${runId}`;
  
  return (
    <KnockProvider apiKey={process.env.NEXT_PUBLIC_KNOCK_PUBLIC_API_KEY!} userId={userId}>
      <KnockFeedProvider feedId={process.env.NEXT_PUBLIC_KNOCK_FEED_CHANNEL_ID!}>
        <div style={{ padding: "50px", display: "flex", justifyContent: "center" }}>
          <div style={{ position: "relative" }}>
            <NotificationIconButton
              ref={notifButtonRef}
              onClick={() => setIsVisible(!isVisible)}
            />
            <NotificationFeedPopover
              buttonRef={notifButtonRef}
              isVisible={isVisible}
              onClose={() => setIsVisible(false)}
            />
          </div>
        </div>
      </KnockFeedProvider>
    </KnockProvider>
  );
}
