import { Liveblocks } from "@liveblocks/node";
import { NextRequest, NextResponse } from "next/server";

const liveblocks = new Liveblocks({
  secret: process.env.LIVEBLOCKS_SECRET_KEY!,
});

export async function POST(request: NextRequest) {
  // Get the display name from the request body (sent by the client)
  let displayName = "Anonymous";
  try {
    const body = await request.json();
    if (body?.displayName) {
      displayName = body.displayName;
    }
  } catch {
    // ignore parse errors
  }

  // Create a session for the user
  const session = liveblocks.prepareSession(`user-${Math.random().toString(36).slice(2)}`, {
    userInfo: {
      name: displayName,
    },
  });

  // Derive room id from environment variable
  const runId = process.env.ZEALT_RUN_ID;
  const roomId = runId ? `harbor-typing-form-${runId}` : "harbor-typing-form-local";

  // Grant full access to the room
  session.allow(roomId, session.FULL_ACCESS);

  const { status, body } = await session.authorize();
  return new NextResponse(body, { status });
}
