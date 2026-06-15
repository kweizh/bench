import type { AppProps } from "next/app";
import { useRouter } from "next/router";
import { LiveblocksProvider, RoomProvider } from "@liveblocks/react";
import { LiveList } from "@liveblocks/client";
import "../liveblocks.config";

const RUN_ID = process.env.NEXT_PUBLIC_ZEALT_RUN_ID || "local";
const ROOM_ID = `whiteboard-${RUN_ID}`;

// Color palette keyed by the ?user=<n> query param.
const USER_COLORS: Record<string, string> = {
  "1": "#DC2626", // red
  "2": "#2563EB", // blue
};
const DEFAULT_COLOR = "#059669"; // green

function getColor(userParam: string | string[] | undefined): string {
  if (typeof userParam === "string" && USER_COLORS[userParam]) {
    return USER_COLORS[userParam];
  }
  return DEFAULT_COLOR;
}

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const color = getColor(router.query.user);
  const publicKey = process.env.NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY || "";

  return (
    <LiveblocksProvider publicApiKey={publicKey}>
      <RoomProvider
        id={ROOM_ID}
        initialPresence={{ selectedShapeId: null, color }}
        initialStorage={{ shapes: new LiveList([]) }}
      >
        <Component {...pageProps} />
      </RoomProvider>
    </LiveblocksProvider>
  );
}
