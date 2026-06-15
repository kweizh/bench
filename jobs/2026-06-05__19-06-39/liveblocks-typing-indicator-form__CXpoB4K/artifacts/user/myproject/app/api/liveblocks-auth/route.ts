import { Liveblocks } from "@liveblocks/node";

const liveblocks = new Liveblocks({
  secret: process.env.LIVEBLOCKS_SECRET_KEY!,
});

export async function POST(request: Request) {
  try {
    const { room } = await request.json();
    const { searchParams } = new URL(request.url);
    const name = searchParams.get("name") || "Anonymous";

    // Start an auth session
    const session = liveblocks.prepareSession(
      `user-${Math.random().toString(36).substring(2, 9)}`,
      {
        userInfo: {
          name,
        },
      }
    );

    // Give the user access to the room
    if (room) {
      session.allow(room, session.FULL_ACCESS);
    }

    const { status, body } = await session.authorize();
    return new Response(body, { status });
  } catch (error) {
    console.error("Liveblocks auth error:", error);
    return new Response("Internal Server Error", { status: 500 });
  }
}
