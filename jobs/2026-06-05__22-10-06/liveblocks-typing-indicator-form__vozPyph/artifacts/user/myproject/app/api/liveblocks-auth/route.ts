import { Liveblocks } from "@liveblocks/node";
import { NextRequest, NextResponse } from "next/server";

const liveblocks = new Liveblocks({
  secret: process.env.LIVEBLOCKS_SECRET_KEY!,
});

export async function POST(request: NextRequest) {
  // Get the display name from searchParams (passed from client if needed)
  // or just use a default for the session.
  // The requirements say: Presence: each user has a typing field ... plus an info (or user) field with a stable display name
  
  const { searchParams } = new URL(request.url);
  const name = searchParams.get("name") || "Anonymous";

  // Start an auth session inside your endpoint
  const session = liveblocks.prepareSession(
    `user-${Math.floor(Math.random() * 10000)}`,
    {
      userInfo: { name },
    }
  );

  // Implement your own security, and give the user access to the room
  const { room } = await request.json();
  session.allow(room, session.FULL_ACCESS);

  // Authorize the user and return the result
  const { status, body } = await session.authorize();
  return new NextResponse(body, { status });
}
