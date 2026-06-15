FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep \
        ffmpeg libxcb-shm0 libx11-xcb1 libx11-6 libxcb1 libxext6 libxrandr2 libxcomposite1 \
        libxcursor1 libxdamage1 libxfixes3 libxi6 libgtk-3-0t64 libpangocairo-1.0-0 \
        libpango-1.0-0 libatk1.0-0t64 libcairo-gobject2 libcairo2 libgdk-pixbuf-2.0-0 \
        libxrender1 libasound2t64 libfreetype6 libfontconfig1 libdbus-1-3 libnss3 libnspr4 \
        libatk-bridge2.0-0t64 libdrm2 libxkbcommon0 libatspi2.0-0t64 libcups2t64 \
        libxshmfence1 libgbm1 && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages \
        pytest-json-ctrf pytest-xprocess requests playwright && \
    python3 -m playwright install --with-deps chromium && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# ---------------------------------------------------------------------------
# Scaffold the Next.js project at /home/user/myproject.
# The scaffold provides:
#   - package.json declaring @liveblocks/{client,react,node} and Next.js
#   - tsconfig.json
#   - next.config.js
#   - app/layout.tsx
#   - app/page.tsx with placeholder canvas + toolbar (drawing NOT implemented)
#   - app/api/liveblocks-auth/route.ts with real @liveblocks/node usage
#   - lib/liveblocks.ts exporting a typed room context
# Drawing logic, eraser logic, undo logic, and storage wiring are intentionally
# left UNIMPLEMENTED for the executor to build.
# ---------------------------------------------------------------------------
RUN mkdir -p /home/user/myproject/app/api/liveblocks-auth && \
    mkdir -p /home/user/myproject/lib && \
    mkdir -p /home/user/myproject/components

RUN cat > /home/user/myproject/package.json <<'EOF'
{
  "name": "liveblocks-collaborative-drawing-strokes",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000",
    "lint": "next lint"
  },
  "dependencies": {
    "@liveblocks/client": "^2.18.3",
    "@liveblocks/node": "^2.18.3",
    "@liveblocks/react": "^2.18.3",
    "next": "14.2.15",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "devDependencies": {
    "@types/node": "20.14.10",
    "@types/react": "18.3.3",
    "@types/react-dom": "18.3.0",
    "typescript": "5.5.3"
  }
}
EOF

RUN cat > /home/user/myproject/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": false,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

RUN cat > /home/user/myproject/next.config.js <<'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};
module.exports = nextConfig;
EOF

RUN cat > /home/user/myproject/next-env.d.ts <<'EOF'
/// <reference types="next" />
/// <reference types="next/image-types/global" />
EOF

RUN cat > /home/user/myproject/lib/liveblocks.ts <<'EOF'
import { createClient, LiveList, LiveObject } from "@liveblocks/client";
import { createRoomContext } from "@liveblocks/react";

// Storage shape that the executor must populate during drawing.
export type StrokePoint = LiveObject<{ x: number; y: number }>;
export type Stroke = LiveObject<{
  id: string;
  userId: string;
  color: string;
  width: number;
  points: LiveList<StrokePoint>;
}>;

export type Presence = {
  cursor: { x: number; y: number } | null;
};

export type Storage = {
  strokes: LiveList<Stroke>;
};

export type UserMeta = {
  id: string;
  info: { name: string };
};

const client = createClient({
  authEndpoint: "/api/liveblocks-auth",
  throttle: 16,
});

export const {
  RoomProvider,
  useRoom,
  useSelf,
  useOthers,
  useMyPresence,
  useUpdateMyPresence,
  useStorage,
  useMutation,
  useHistory,
} = createRoomContext<Presence, Storage, UserMeta>(client);
EOF

RUN cat > /home/user/myproject/app/layout.tsx <<'EOF'
import React from "react";

export const metadata = {
  title: "Collaborative Drawing",
  description: "Multiplayer freeform drawing canvas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "sans-serif" }}>{children}</body>
    </html>
  );
}
EOF

RUN cat > /home/user/myproject/app/page.tsx <<'EOF'
"use client";

import React, { useMemo, useState } from "react";
import { LiveList } from "@liveblocks/client";
import { RoomProvider } from "@/lib/liveblocks";
import { CanvasScaffold } from "@/components/CanvasScaffold";

function getRoomId(): string {
  const runId =
    typeof process !== "undefined" && process.env && process.env.NEXT_PUBLIC_ZEALT_RUN_ID
      ? process.env.NEXT_PUBLIC_ZEALT_RUN_ID
      : "local-dev";
  return `liveblocks-drawing-${runId}`;
}

export default function Page() {
  // Default user id read on first render from window.location to support ?user=
  const [userId, setUserId] = useState<string>("anonymous");
  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const u = params.get("user");
    if (u && u.length > 0) setUserId(u);
  }, []);

  const roomId = useMemo(() => getRoomId(), []);

  return (
    <RoomProvider
      id={roomId}
      initialPresence={{ cursor: null }}
      initialStorage={{ strokes: new LiveList([]) }}
    >
      <CanvasScaffold userId={userId} />
    </RoomProvider>
  );
}
EOF

RUN cat > /home/user/myproject/components/CanvasScaffold.tsx <<'EOF'
"use client";

import React, { useState } from "react";

type Tool = "pen" | "eraser";

/**
 * Placeholder scaffold. It renders the toolbar and an empty SVG canvas with
 * the required data-testid attributes, but DOES NOT implement stroke creation,
 * eraser deletion, or undo logic. The executor must add these behaviours.
 */
export function CanvasScaffold({ userId }: { userId: string }) {
  const [tool, setTool] = useState<Tool>("pen");
  const [color, setColor] = useState<string>("#000000");
  const [width, setWidth] = useState<number>(4);

  return (
    <div style={{ padding: 16 }}>
      <h1>Collaborative Drawing</h1>
      <p>
        User: <strong data-testid="current-user">{userId}</strong>
      </p>
      <div style={{ display: "flex", gap: 8, marginBottom: 12, alignItems: "center" }}>
        <label>
          Color
          <input
            data-testid="color-picker"
            type="text"
            value={color}
            onChange={(e) => setColor(e.target.value)}
            style={{ marginLeft: 4, width: 96 }}
          />
        </label>
        <label>
          Width
          <input
            data-testid="width-picker"
            type="number"
            min={1}
            max={32}
            value={width}
            onChange={(e) => setWidth(Number(e.target.value))}
            style={{ marginLeft: 4, width: 64 }}
          />
        </label>
        <button
          data-testid="tool-pen"
          onClick={() => setTool("pen")}
          aria-pressed={tool === "pen"}
        >
          Pen
        </button>
        <button
          data-testid="tool-eraser"
          onClick={() => setTool("eraser")}
          aria-pressed={tool === "eraser"}
        >
          Eraser
        </button>
        <button data-testid="undo-mine">Undo my last stroke</button>
      </div>
      <svg
        data-testid="canvas"
        width={1024}
        height={720}
        viewBox="0 0 1024 720"
        style={{ background: "#fafafa", border: "1px solid #ddd" }}
      >
        {/* TODO(executor): render <polyline data-stroke-id data-user-id ... /> for each stroke. */}
      </svg>
    </div>
  );
}
EOF

RUN cat > /home/user/myproject/app/api/liveblocks-auth/route.ts <<'EOF'
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
EOF

# ---------------------------------------------------------------------------
# Install Node dependencies up front so the container is fully ready to run
# `npm run dev` without internet access.
# ---------------------------------------------------------------------------
RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund --loglevel=error

# Expose NEXT_PUBLIC_ZEALT_RUN_ID at runtime in the client by writing a tiny
# helper script that the executor or verifier will source. The actual value
# is supplied via the ZEALT_RUN_ID env var at run time.
RUN cat > /home/user/myproject/.env.example <<'EOF'
# Required at runtime (the harness sets these for the container):
#   LIVEBLOCKS_SECRET_KEY
#   NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY
#   ZEALT_RUN_ID
#   NEXT_PUBLIC_ZEALT_RUN_ID  (must mirror ZEALT_RUN_ID so the client can derive the room id)
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Next.js Liveblocks collaborative drawing scaffold (canvas + toolbar pre-rendered; drawing/eraser/undo NOT yet implemented)."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#                   + chromium browser shared libs (gtk/cairo/nss/etc.)
#   - pip3 packages: pytest-json-ctrf pytest-xprocess requests playwright
#   - Playwright Chromium (via `playwright install --with-deps chromium`)
#   - Node.js v20 (NodeSource)
#   - /home/user/myproject: scaffolded Next.js App Router project
#       - package.json with @liveblocks/{client,react,node}
#       - app/layout.tsx, app/page.tsx (placeholder UI)
#       - components/CanvasScaffold.tsx (toolbar + empty SVG canvas)
#       - app/api/liveblocks-auth/route.ts (real Liveblocks Node SDK)
#       - lib/liveblocks.ts (typed Liveblocks room context)
#       - node_modules pre-installed
