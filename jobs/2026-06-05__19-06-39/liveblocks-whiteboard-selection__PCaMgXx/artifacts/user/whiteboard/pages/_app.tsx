import type { AppProps } from "next/app";
import { LiveblocksProvider, RoomProvider } from "@liveblocks/react";
import { LiveList } from "@liveblocks/client";
import "../liveblocks.config";

const RUN_ID = process.env.NEXT_PUBLIC_ZEALT_RUN_ID || "local";
const ROOM_ID = `whiteboard-${RUN_ID}`;

export default function App({ Component, pageProps }: AppProps) {
  const publicKey = process.env.NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY || "";
  return (
    <LiveblocksProvider publicApiKey={publicKey}>
      <RoomProvider
        id={ROOM_ID}
        initialPresence={{ selectedShapeId: null }}
        initialStorage={{ shapes: new LiveList([]) }}
      >
        <Component {...pageProps} />
      </RoomProvider>
    </LiveblocksProvider>
  );
}
