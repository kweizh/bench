import { Liveblocks } from "@liveblocks/node";
import { NextRequest, NextResponse } from "next/server";

const liveblocks = new Liveblocks({
  secret: process.env.LIVEBLOCKS_SECRET_KEY || "sk_test_placeholder",
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const room = body.room;
    
    // In Liveblocks v2, we can just use identifyUser to create an access token.
    const user = {
      id: Math.random().toString(36).substring(7),
    };
    
    const session = liveblocks.prepareSession(user.id);
    if (room) {
      session.allow(room, session.FULL_ACCESS);
    }
    
    const { status, body: authBody } = await session.authorize();
    return new NextResponse(authBody, { status });
  } catch (error) {
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}
