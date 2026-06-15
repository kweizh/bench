"use client";

import { ReactNode, useMemo } from "react";
import { RoomProvider } from "../liveblocks.config";
import { LiveObject } from "@liveblocks/client";
import { useSearchParams } from "next/navigation";
import { LiveblocksProvider } from "@liveblocks/react";

export function Room({ children }: { children: ReactNode }) {
  const searchParams = useSearchParams();
  const name = searchParams.get("name") || "Anonymous";

  const roomId = useMemo(() => {
    const runId = process.env.NEXT_PUBLIC_ZEALT_RUN_ID || "local";
    return `harbor-typing-form-${runId}`;
  }, []);

  return (
    <LiveblocksProvider authEndpoint={`/api/liveblocks-auth?name=${encodeURIComponent(name)}`}>
      <RoomProvider
        id={roomId}
        initialPresence={{ typing: null, info: { name } }}
        initialStorage={{
          form: new LiveObject({ name: "", email: "", bio: "" }),
        }}
      >
        {children}
      </RoomProvider>
    </LiveblocksProvider>
  );
}
