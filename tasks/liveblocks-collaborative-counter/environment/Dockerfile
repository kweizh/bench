FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        curl wget ca-certificates git bash ripgrep \
        python3 python3-pip python3-pytest \
        ffmpeg libxcb-shm0 libx11-xcb1 libx11-6 libxcb1 libxext6 libxrandr2 \
        libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 \
        libgtk-3-0t64 libpangocairo-1.0-0 libpango-1.0-0 libatk1.0-0t64 \
        libcairo-gobject2 libcairo2 libgdk-pixbuf-2.0-0 libxrender1 \
        libasound2t64 libfreetype6 libfontconfig1 libdbus-1-3 libnss3 \
        libnspr4 libatk-bridge2.0-0t64 libdrm2 libxkbcommon0 \
        libatspi2.0-0t64 libcups2t64 libxshmfence1 libgbm1 && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages \
        pytest-json-ctrf requests pytest-xprocess playwright && \
    playwright install chromium && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# --- Scaffold the Next.js + Liveblocks starter project ------------------
RUN mkdir -p /home/user/project/app/dashboard/\[room\] && \
    mkdir -p /home/user/project/app/api/liveblocks-auth

WORKDIR /home/user/project

RUN cat >/home/user/project/package.json <<'EOF'
{
  "name": "liveblocks-collaborative-counter",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000",
    "lint": "next lint"
  },
  "dependencies": {
    "@liveblocks/client": "2.20.0",
    "@liveblocks/node": "2.20.0",
    "@liveblocks/react": "2.20.0",
    "next": "14.2.15",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "devDependencies": {
    "@types/node": "20.14.10",
    "@types/react": "18.3.3",
    "@types/react-dom": "18.3.0",
    "typescript": "5.4.5"
  }
}
EOF

RUN cat >/home/user/project/tsconfig.json <<'EOF'
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
    "plugins": [{ "name": "next" }]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
EOF

RUN cat >/home/user/project/next.config.mjs <<'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true }
};
export default nextConfig;
EOF

RUN cat >/home/user/project/next-env.d.ts <<'EOF'
/// <reference types="next" />
/// <reference types="next/image-types/global" />
EOF

RUN cat >/home/user/project/liveblocks.config.ts <<'EOF'
import type { LiveMap, LiveObject } from "@liveblocks/client";

/**
 * Storage layout for the collaborative counter dashboard.
 *
 * Each entry of `counters` is a LiveObject with the three required fields:
 *   - value: number
 *   - lastIncrementBy: string
 *   - lastUpdated: number (ms epoch)
 *
 * The executor must use these types together with `useMutation`/`useStorage`
 * to read and write the Storage tree.
 */
export type Counter = {
  value: number;
  lastIncrementBy: string;
  lastUpdated: number;
};

export type Storage = {
  counters: LiveMap<string, LiveObject<Counter>>;
};

export type Presence = Record<string, never>;

export type UserMeta = {
  id?: string;
  info?: { name?: string };
};

declare global {
  interface Liveblocks {
    Storage: Storage;
    Presence: Presence;
    UserMeta: UserMeta;
  }
}
EOF

RUN cat >/home/user/project/app/layout.tsx <<'EOF'
import React from "react";

export const metadata = {
  title: "Liveblocks Collaborative Counter",
  description: "Multi-counter dashboard built on Liveblocks Storage"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
EOF

RUN cat >/home/user/project/app/page.tsx <<'EOF'
import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Liveblocks Collaborative Counter</h1>
      <p>
        Open <Link href="/dashboard/demo">/dashboard/demo</Link> in two
        browser windows to collaborate.
      </p>
    </main>
  );
}
EOF

RUN cat >/home/user/project/app/api/liveblocks-auth/route.ts <<'EOF'
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
EOF

# Dashboard skeleton: RoomProvider is set up, but the Storage-backed UI and
# mutations are intentionally left TODO so the executor can implement them.
# The provider wiring is delegated to a separate helper so the page itself
# stays free of any Storage primitives.
RUN cat >/home/user/project/app/dashboard/\[room\]/Room.tsx <<'EOF'
"use client";

import { LiveMap } from "@liveblocks/client";
import {
  LiveblocksProvider,
  RoomProvider,
  ClientSideSuspense
} from "@liveblocks/react/suspense";
import type { ReactNode } from "react";

export function Room({ roomId, children }: { roomId: string; children: ReactNode }) {
  return (
    <LiveblocksProvider authEndpoint="/api/liveblocks-auth">
      <RoomProvider id={roomId} initialStorage={{ counters: new LiveMap() }}>
        <ClientSideSuspense fallback={<div>Loading…</div>}>
          {() => <>{children}</>}
        </ClientSideSuspense>
      </RoomProvider>
    </LiveblocksProvider>
  );
}
EOF

RUN cat >/home/user/project/app/dashboard/\[room\]/page.tsx <<'EOF'
"use client";

import { useParams } from "next/navigation";
import { Room } from "./Room";

// TODO: implement the collaborative multi-counter dashboard here.
//
// See instruction.md for the full specification of the UI, Storage layout,
// mutation behavior, and required DOM contract. The provider wiring lives in
// ./Room.tsx and is already in place — render your dashboard as children of
// <Room>.

function Dashboard() {
  return (
    <main style={{ padding: 24, fontFamily: "system-ui" }}>
      <h1>Collaborative Counter Dashboard</h1>
      <p>TODO: build the dashboard UI per the task instructions.</p>
    </main>
  );
}

export default function DashboardPage() {
  const params = useParams<{ room: string }>();
  const roomId =
    (Array.isArray(params?.room) ? params?.room[0] : params?.room) ||
    "default-room";

  return (
    <Room roomId={roomId}>
      <Dashboard />
    </Room>
  );
}
EOF

# Install dependencies ahead of time so the executor (and tests) do not pay
# the install cost at run time. Use --no-audit/--no-fund to keep the build
# log small. `npm install` is used (not `ci`) because there is no lockfile
# committed inside the image.
RUN cd /home/user/project && \
    npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="Next.js 14 + Liveblocks starter for the collaborative-counter task. Pre-installs Node 20, Playwright Chromium, and the Liveblocks SDK skeleton at /home/user/project."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - apt packages: curl wget ca-certificates git python3 python3-pip
#     python3-pytest bash ripgrep + Playwright system libs + ffmpeg
#   - Node.js v20 (LTS) via NodeSource
#   - pip3 packages: pytest-json-ctrf requests pytest-xprocess playwright
#   - Playwright Chromium pre-installed for browser verification
#   - /home/user/project: Next.js 14 + Liveblocks starter with the dashboard
#     skeleton at app/dashboard/[room]/page.tsx (Storage mutations TODO),
#     `/api/liveblocks-auth` already wired with @liveblocks/node, and
#     liveblocks.config.ts declaring Storage.counters as
#     LiveMap<string, LiveObject<{value, lastIncrementBy, lastUpdated}>>.
#   - node_modules pre-installed.
