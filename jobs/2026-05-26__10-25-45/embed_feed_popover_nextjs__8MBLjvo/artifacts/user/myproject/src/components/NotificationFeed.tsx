"use client";

import { useRef, useState } from "react";
import {
  KnockProvider,
  KnockFeedProvider,
  NotificationIconButton,
  NotificationFeedPopover,
} from "@knocklabs/react";
import "@knocklabs/react/dist/index.css";

const KNOCK_PUBLIC_API_KEY = process.env.NEXT_PUBLIC_KNOCK_PUBLIC_API_KEY!;
const KNOCK_FEED_CHANNEL_ID = process.env.NEXT_PUBLIC_KNOCK_FEED_CHANNEL_ID!;
const USER_ID = "popover-user-zr-8mbljvo";

export default function NotificationFeed() {
  const [isVisible, setIsVisible] = useState(false);
  const notifButtonRef = useRef<HTMLButtonElement>(null);

  return (
    <KnockProvider apiKey={KNOCK_PUBLIC_API_KEY} userId={USER_ID}>
      <KnockFeedProvider feedId={KNOCK_FEED_CHANNEL_ID}>
        <div style={{ position: "relative", display: "inline-block" }}>
          <NotificationIconButton
            ref={notifButtonRef}
            onClick={() => setIsVisible((prev) => !prev)}
          />
          <NotificationFeedPopover
            buttonRef={notifButtonRef}
            isVisible={isVisible}
            onClose={() => setIsVisible(false)}
          />
        </div>
      </KnockFeedProvider>
    </KnockProvider>
  );
}
