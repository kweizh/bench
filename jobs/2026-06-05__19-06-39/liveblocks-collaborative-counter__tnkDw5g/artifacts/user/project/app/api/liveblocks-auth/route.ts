import { Liveblocks } from "@liveblocks/node";
import { NextResponse } from "next/server";

const secret = process.env.LIVEBLOCKS_SECRET_KEY;

export async function POST(request: Request) {
  if (!secret) {
    return NextResponse.json(
      { error: "Missing LIVEBLOCKS_SECRET_KEY" },
      { status: 500 }
    );
  }

  let body: { room?: string } = {};
  try {
    body = await request.json();
  } catch {
    body = {};
  }
  const room = typeof body?.room === "string" ? body.room : "default-room";

  const liveblocks = new Liveblocks({ secret });
  const session = liveblocks.prepareSession(
    `user-${Math.random().toString(36).slice(2, 10)}`,
    { userInfo: { name: "anonymous" } }
  );
  session.allow(room, session.FULL_ACCESS);

  const { status, body: tokenBody } = await session.authorize();
  return new NextResponse(tokenBody, {
    status,
    headers: { "content-type": "application/json" }
  });
}
