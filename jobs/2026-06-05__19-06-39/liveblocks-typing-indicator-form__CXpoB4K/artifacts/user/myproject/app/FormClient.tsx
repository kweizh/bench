"use client";

import React, { Suspense } from "react";
import { LiveblocksProvider, RoomProvider, ClientSideSuspense } from "@liveblocks/react";
import { LiveObject } from "@liveblocks/client";
import { useSearchParams } from "next/navigation";
import FormContent from "./FormContent";

function FormClientInner({ roomId }: { roomId: string }) {
  const searchParams = useSearchParams();
  const name = searchParams.get("name") || "Anonymous";

  return (
    <LiveblocksProvider authEndpoint={`/api/liveblocks-auth?name=${encodeURIComponent(name)}`}>
      <RoomProvider
        id={roomId}
        initialPresence={{
          typing: null,
          info: { name },
          user: { name },
        }}
        initialStorage={{
          form: new LiveObject({
            name: "",
            email: "",
            bio: "",
          }),
        }}
      >
        <ClientSideSuspense fallback={<div>Loading room...</div>}>
          <FormContent />
        </ClientSideSuspense>
      </RoomProvider>
    </LiveblocksProvider>
  );
}

export default function FormClient({ roomId }: { roomId: string }) {
  return (
    <Suspense fallback={<div>Loading search params...</div>}>
      <FormClientInner roomId={roomId} />
    </Suspense>
  );
}
