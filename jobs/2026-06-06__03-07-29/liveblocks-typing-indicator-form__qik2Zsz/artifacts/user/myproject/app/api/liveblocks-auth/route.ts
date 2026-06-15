import { Liveblocks } from "@liveblocks/node";

const liveblocks = new Liveblocks({
  secret: process.env.LIVEBLOCKS_SECRET_KEY!,
});

export async function POST(request: Request) {
  const body = await request.json();
  const room = body.room;

  // Create a unique user ID for this session
  const userId = "user-" + Math.random().toString(36).substr(2, 9);

  // Prepare a session with user info
  const session = liveblocks.prepareSession(userId, {
    userInfo: { name: "Anonymous" },
  });

  // Allow full access to the requested room
  session.allow(room, session.FULL_ACCESS);

  // Authorize and return
  const { status, body: responseBody } = await session.authorize();

  return new Response(responseBody, { status });
}