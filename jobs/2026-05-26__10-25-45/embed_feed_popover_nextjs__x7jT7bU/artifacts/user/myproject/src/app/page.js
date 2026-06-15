"use client";

import { useMemo, useRef, useState } from "react";
import {
  KnockFeedProvider,
  KnockProvider,
  NotificationFeedPopover,
  NotificationIconButton,
} from "@knocklabs/react";

export default function Home() {
  const [isVisible, setIsVisible] = useState(false);
  const buttonRef = useRef(null);

  const runId = process.env.NEXT_PUBLIC_ZEALT_RUN_ID;
  const knockPublicKey = process.env.NEXT_PUBLIC_KNOCK_PUBLIC_API_KEY;
  const feedChannelId = process.env.NEXT_PUBLIC_KNOCK_FEED_CHANNEL_ID;

  const userId = useMemo(() => {
    if (!runId) {
      return "popover-user-unknown";
    }

    return `popover-user-${runId}`;
  }, [runId]);

  return (
    <main
      style={{
        display: "flex",
        minHeight: "100vh",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#f8fafc",
        padding: "2rem",
      }}
    >
      <KnockProvider apiKey={knockPublicKey} userId={userId}>
        <KnockFeedProvider feedId={feedChannelId}>
          <div style={{ position: "relative" }}>
            <NotificationIconButton
              ref={buttonRef}
              onClick={() => setIsVisible((current) => !current)}
            />
            <NotificationFeedPopover
              buttonRef={buttonRef}
              isVisible={isVisible}
              onClose={() => setIsVisible(false)}
            />
          </div>
        </KnockFeedProvider>
      </KnockProvider>
    </main>
  );
}
