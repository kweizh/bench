"use client";

import React, { useEffect, useState } from "react";
import { LiveObject } from "@liveblocks/client";
import { RoomProvider } from "../../liveblocks.config";

const ROOM_ID = process.env.NEXT_PUBLIC_ROOM_ID || "harbor-typing-form-local";

export function Room({ children }: { children: React.ReactNode }) {
  const [displayName, setDisplayName] = useState("Anonymous");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const nameParam = params.get("name");
    if (nameParam) {
      setDisplayName(nameParam);
    }
  }, []);

  return (
    <RoomProvider
      id={ROOM_ID}
      initialPresence={{
        typing: null,
        info: { name: displayName },
      }}
      initialStorage={{
        form: new LiveObject({ name: "", email: "", bio: "" }),
      }}
    >
      {children}
    </RoomProvider>
  );
}
