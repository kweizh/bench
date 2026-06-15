import type { AppProps } from "next/app";
import { useRouter } from "next/router";
import { LiveblocksProvider, RoomProvider, useMyPresence } from "@liveblocks/react";
import { LiveList } from "@liveblocks/client";
import { useEffect } from "react";
import "../liveblocks.config";

const RUN_ID = process.env.NEXT_PUBLIC_ZEALT_RUN_ID || "local";
const ROOM_ID = `whiteboard-${RUN_ID}`;

function getUserColor(userParam: string | string[] | undefined): string {
  const n = Array.isArray(userParam) ? userParam[0] : userParam;
  if (n === "1") return "#DC2626";
  if (n === "2") return "#2563EB";
  return "#059669";
}

function PresenceColorSync() {
  const router = useRouter();
  const [, updateMyPresence] = useMyPresence();

  useEffect(() => {
    if (router.isReady) {
      const color = getUserColor(router.query.user);
      updateMyPresence({ color });
    }
  }, [router.isReady, router.query.user, updateMyPresence]);

  return null;
}

export default function App({ Component, pageProps }: AppProps) {
  const publicKey = process.env.NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY || "";

  return (
    <LiveblocksProvider publicApiKey={publicKey}>
      <RoomProvider
        id={ROOM_ID}
        initialPresence={{ selectedShapeId: null, color: "#059669" }}
        initialStorage={{ shapes: new LiveList([]) }}
      >
        <PresenceColorSync />
        <Component {...pageProps} />
      </RoomProvider>
    </LiveblocksProvider>
  );
}