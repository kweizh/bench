import { Liveblocks } from "@liveblocks/node";

const liveblocks = new Liveblocks({
  secret: process.env.LIVEBLOCKS_SECRET_KEY as string,
});

export async function POST(request: Request) {
  const runId = process.env.ZEALT_RUN_ID || "local";
  const roomId = `cursor-follow-${runId}`;

  // Generate a random user identifier for each connection.
  const userId = `user-${Math.random().toString(36).slice(2, 10)}`;

  const session = liveblocks.prepareSession(userId, {
    userInfo: {
      name: userId,
      color: `hsl(${Math.floor(Math.random() * 360)}, 70%, 55%)`,
    },
  });

  // Allow full access to the per-run room.
  session.allow(roomId, session.FULL_ACCESS);

  const { status, body } = await session.authorize();
  return new Response(body, { status, headers: { "Content-Type": "application/json" } });
}
