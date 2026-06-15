"use client";

import React, { useMemo, useState } from "react";
import { LiveList } from "@liveblocks/client";
import { RoomProvider } from "@/lib/liveblocks";
import { CanvasScaffold } from "@/components/CanvasScaffold";

function getRoomId(): string {
  const runId =
    typeof process !== "undefined" && process.env && process.env.NEXT_PUBLIC_ZEALT_RUN_ID
      ? process.env.NEXT_PUBLIC_ZEALT_RUN_ID
      : "local-dev";
  return `liveblocks-drawing-${runId}`;
}

export default function Page() {
  // Default user id read on first render from window.location to support ?user=
  const [userId, setUserId] = useState<string>("anonymous");
  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const u = params.get("user");
    if (u && u.length > 0) setUserId(u);
  }, []);

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
