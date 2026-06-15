"use client";

import { LiveblocksProvider, RoomProvider, ClientSideSuspense } from "@liveblocks/react";
import { LiveObject } from "@liveblocks/client";
import { ReactNode } from "react";

export function LiveblocksProviderWrapper({
  roomId,
  children,
}: {
  roomId: string;
  children: ReactNode;
}) {
  return (
    <LiveblocksProvider authEndpoint="/api/liveblocks-auth">
      <RoomProvider
        id={roomId}
        initialStorage={{
          form: new LiveObject({ name: "", email: "", bio: "" }),
        }}
        initialPresence={{ typing: null, info: { name: "Anonymous" } }}
      >
        <ClientSideSuspense fallback={<div>Loading...</div>}>
          {() => <>{children}</>}
        </ClientSideSuspense>
      </RoomProvider>
    </LiveblocksProvider>
  );
}