"use client";

import React, { useMemo } from "react";
import { LiveList } from "@liveblocks/client";
import { RoomProvider } from "@/lib/liveblocks";
import { CanvasScaffold } from "@/components/CanvasScaffold";

function getRoomId(): string {
  const runId =
    typeof process !== "undefined" &&
    process.env &&
    process.env.NEXT_PUBLIC_ZEALT_RUN_ID
      ? process.env.NEXT_PUBLIC_ZEALT_RUN_ID
      : "local-dev";
  return `liveblocks-drawing-${runId}`;
}

function getUserId(): string {
  if (typeof window === "undefined") return "anonymous";
  const params = new URLSearchParams(window.location.search);
  const u = params.get("user");
  return u && u.length > 0 ? u : "anonymous";
}

export default function Page() {
  // Read userId once at component creation time (client only).
  // Using a lazy initialiser so it runs on first render on the client.
  const [userId] = React.useState<string>(() => getUserId());

  const roomId = useMemo(() => getRoomId(), []);

  return (
    <RoomProvider
      id={roomId}
      initialPresence={{ cursor: null }}
      initialStorage={{ strokes: new LiveList([]) }}
    >
      <CanvasScaffold userId={userId} />
    </RoomProvider>
  );
}
