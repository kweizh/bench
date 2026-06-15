import { Liveblocks } from "@liveblocks/node";
import { NextRequest, NextResponse } from "next/server";

const secret = process.env.LIVEBLOCKS_SECRET_KEY;

export async function POST(req: NextRequest) {
  if (!secret) {
    return NextResponse.json({ error: "Missing LIVEBLOCKS_SECRET_KEY" }, { status: 500 });
  }

  const liveblocks = new Liveblocks({ secret });

  // Accept the user id either from the request body, query, or referer.
  let userId: string | undefined;
  try {
    const body = (await req.json().catch(() => ({}))) as { userId?: string; user?: string };
    userId = body.userId || body.user;
  } catch {
    // ignore
  }
  if (!userId) {
    const url = new URL(req.url);
    userId = url.searchParams.get("user") || undefined;
  }
  if (!userId) {
    const referer = req.headers.get("referer");
    if (referer) {
      try {
        const u = new URL(referer).searchParams.get("user");
        if (u) userId = u;
      } catch {
        // ignore
      }
    }
  }
  if (!userId) userId = "anonymous";

  const runId = process.env.ZEALT_RUN_ID || "local-dev";
  const roomId = `liveblocks-drawing-${runId}`;

  const session = liveblocks.prepareSession(userId, {
    userInfo: { name: userId },
  });
  session.allow(roomId, session.FULL_ACCESS);

  const { status, body } = await session.authorize();
  return new NextResponse(body, { status });
}
