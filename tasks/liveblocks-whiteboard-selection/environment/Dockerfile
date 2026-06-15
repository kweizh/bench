# syntax=docker/dockerfile:1.7
FROM ubuntu:24.04

# ---------------------------------------------------------------------------
# Base system + Node.js 20 + Playwright (Python) + verifier runtime deps
# ---------------------------------------------------------------------------
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest python3-venv \
        bash ripgrep gnupg \
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
        pytest-json-ctrf \
        pytest-xprocess \
        playwright \
        requests && \
    python3 -m playwright install chromium && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# User home directory
# ---------------------------------------------------------------------------
RUN mkdir -p /home/user && chmod 0755 /home/user

# ---------------------------------------------------------------------------
# Scaffold the Next.js + Liveblocks whiteboard project at /home/user/whiteboard
# ---------------------------------------------------------------------------
RUN mkdir -p /home/user/whiteboard/pages

# package.json
RUN cat > /home/user/whiteboard/package.json <<'JSON'
{
  "name": "whiteboard",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000"
  },
  "dependencies": {
    "@liveblocks/client": "^2.20.0",
    "@liveblocks/react": "^2.20.0",
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
JSON

# tsconfig.json
RUN cat > /home/user/whiteboard/tsconfig.json <<'JSON'
{
  "compilerOptions": {
    "target": "es2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": false,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
JSON

# next-env.d.ts
RUN cat > /home/user/whiteboard/next-env.d.ts <<'TS'
/// <reference types="next" />
/// <reference types="next/types/global" />
TS

# next.config.js — exposes ZEALT_RUN_ID as NEXT_PUBLIC_ZEALT_RUN_ID
RUN cat > /home/user/whiteboard/next.config.js <<'JS'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_ZEALT_RUN_ID: process.env.ZEALT_RUN_ID || "local",
  },
};
module.exports = nextConfig;
JS

# .env.local placeholder — real values come from container env vars at runtime.
RUN cat > /home/user/whiteboard/.env.local <<'ENV'
# Real values are injected via container environment variables and override
# these placeholders when next dev starts.
LIVEBLOCKS_SECRET_KEY=
NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY=
ENV

# liveblocks.config.ts — Presence is intentionally empty; agent must add
# selectedShapeId.
RUN cat > /home/user/whiteboard/liveblocks.config.ts <<'TS'
import type { LiveList, LiveObject } from "@liveblocks/client";

export type Shape = LiveObject<{
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
}>;

declare global {
  interface Liveblocks {
    // TODO: declare per-user transient state for multi-user selection here.
    Presence: {};
    // The Storage tree for the room.
    Storage: {
      shapes: LiveList<Shape>;
    };
    // TODO: declare UserMeta if you need per-user info (color, name, ...).
    UserMeta: {
      id?: string;
      info?: {
        color?: string;
      };
    };
  }
}

export {};
TS

# pages/_app.tsx — joins the Liveblocks room with NEXT_PUBLIC_ZEALT_RUN_ID.
RUN cat > /home/user/whiteboard/pages/_app.tsx <<'TSX'
import type { AppProps } from "next/app";
import { LiveblocksProvider, RoomProvider } from "@liveblocks/react";
import { LiveList } from "@liveblocks/client";
import "../liveblocks.config";

const RUN_ID = process.env.NEXT_PUBLIC_ZEALT_RUN_ID || "local";
const ROOM_ID = `whiteboard-${RUN_ID}`;

export default function App({ Component, pageProps }: AppProps) {
  const publicKey = process.env.NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY || "";
  return (
    <LiveblocksProvider publicApiKey={publicKey}>
      <RoomProvider
        id={ROOM_ID}
        initialPresence={{}}
        initialStorage={{ shapes: new LiveList([]) }}
      >
        <Component {...pageProps} />
      </RoomProvider>
    </LiveblocksProvider>
  );
}
TSX

# pages/index.tsx — renders the shapes from Storage with seeding, but NO
# Presence-based selection. The agent must add the selection feature.
RUN cat > /home/user/whiteboard/pages/index.tsx <<'TSX'
import { useEffect } from "react";
import { LiveObject } from "@liveblocks/client";
import {
  ClientSideSuspense,
  useMutation,
  useStorage,
} from "@liveblocks/react";

type SeedShape = {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
};

const SEED_SHAPES: SeedShape[] = [
  { id: "shape-a", x: 80,  y: 80,  width: 140, height: 90,  fill: "#FCD34D" },
  { id: "shape-b", x: 320, y: 200, width: 140, height: 140, fill: "#A78BFA" },
  { id: "shape-c", x: 560, y: 360, width: 160, height: 100, fill: "#34D399" },
];

function Whiteboard() {
  const shapes = useStorage((root) => root.shapes);

  const seedShapes = useMutation(({ storage }) => {
    const list = storage.get("shapes");
    if (list.length === 0) {
      for (const s of SEED_SHAPES) {
        list.push(new LiveObject(s));
      }
    }
  }, []);

  useEffect(() => {
    if (shapes && shapes.length === 0) {
      seedShapes();
    }
  }, [shapes, seedShapes]);

  if (!shapes) {
    return <div>Loading…</div>;
  }

  return (
    <svg
      viewBox="0 0 800 600"
      width="100%"
      height="100vh"
      style={{ background: "#f8fafc", display: "block" }}
    >
      {shapes.map((shape) => (
        <rect
          key={shape.id}
          data-testid="shape"
          data-shape-id={shape.id}
          x={shape.x}
          y={shape.y}
          width={shape.width}
          height={shape.height}
          fill={shape.fill}
        />
      ))}
    </svg>
  );
}

export default function Page() {
  return (
    <ClientSideSuspense fallback={<div>Loading…</div>}>
      {() => <Whiteboard />}
    </ClientSideSuspense>
  );
}
TSX

# Install dependencies so the project is ready to `npm run dev` immediately.
WORKDIR /home/user/whiteboard
RUN npm install --no-audit --no-fund --loglevel=error

WORKDIR /

LABEL Author="generate-harbor-tasks"
LABEL Description="Node.js 20 + Next.js + Liveblocks whiteboard scaffold with Playwright (Python) for two-context cross-user selection verification."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest python3-venv bash ripgrep gnupg + Playwright browser system libs
#   - required pip3 packages: pytest-json-ctrf pytest-xprocess playwright requests (Playwright Chromium installed)
#   - Node.js 20 installed via nodesource (for Next.js dev server)
#   - /home/user/whiteboard: scaffolded Next.js + Liveblocks project with shapes seeded
#       and Presence-based selection intentionally NOT implemented yet
#   - /home/user/whiteboard/node_modules: pre-installed npm dependencies
