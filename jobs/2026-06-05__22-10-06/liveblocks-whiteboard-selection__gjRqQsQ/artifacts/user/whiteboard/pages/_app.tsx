import type { AppProps } from "next/app";
import { LiveblocksProvider, RoomProvider } from "@liveblocks/react";
import { LiveList } from "@liveblocks/client";
import { useRouter } from "next/router";
import "../liveblocks.config";

const RUN_ID = process.env.NEXT_PUBLIC_ZEALT_RUN_ID || "local";
const ROOM_ID = `whiteboard-${RUN_ID}`;

const COLORS = ["#059669", "#DC2626", "#2563EB"];

export default function App({ Component, pageProps }: AppProps) {
  const publicKey = process.env.NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY || "";
  const { query } = useRouter();

  const userIndex = query.user ? parseInt(query.user as string) : 0;
  // n=1 -> #DC2626 (index 1)
  // n=2 -> #2563EB (index 2)
  // default -> #059669 (index 0)
  const color = userIndex === 1 ? COLORS[1] : userIndex === 2 ? COLORS[2] : COLORS[0];

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
