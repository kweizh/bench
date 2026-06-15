FROM ubuntu:24.04

# --- Base system + browser dependencies + Node.js 20 + Python tooling ---
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep \
        ffmpeg libxcb-shm0 libx11-xcb1 libx11-6 libxcb1 libxext6 libxrandr2 libxcomposite1 \
        libxcursor1 libxdamage1 libxfixes3 libxi6 libgtk-3-0t64 libpangocairo-1.0-0 \
        libpango-1.0-0 libatk1.0-0t64 libcairo-gobject2 libcairo2 libgdk-pixbuf-2.0-0 \
        libxrender1 libasound2t64 libfreetype6 libfontconfig1 libdbus-1-3 libnss3 \
        libnspr4 libatk-bridge2.0-0t64 libdrm2 libxkbcommon0 libatspi2.0-0t64 libcups2t64 \
        libxshmfence1 libgbm1 && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages \
        pytest-json-ctrf pytest-xprocess requests playwright && \
    playwright install --with-deps chromium && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# --- Scaffold the Next.js starter project at /home/user/myproject ---
RUN mkdir -p /home/user/myproject/app

# package.json (Next.js 14 App Router + Liveblocks SDKs)
RUN cat > /home/user/myproject/package.json <<'EOF'
{
  "name": "liveblocks-typing-form-starter",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "@liveblocks/client": "^2.10.0",
    "@liveblocks/node": "^2.10.0",
    "@liveblocks/react": "^2.10.0",
    "next": "14.2.15",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "devDependencies": {
    "@types/node": "20.12.7",
    "@types/react": "18.3.3",
    "@types/react-dom": "18.3.0",
    "typescript": "5.4.5"
  }
}
EOF

# tsconfig.json
RUN cat > /home/user/myproject/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
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

# next.config.js
RUN cat > /home/user/myproject/next.config.js <<'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = { reactStrictMode: false };
module.exports = nextConfig;
EOF

# next-env.d.ts
RUN cat > /home/user/myproject/next-env.d.ts <<'EOF'
/// <reference types="next" />
/// <reference types="next/image-types/global" />
EOF

# app/layout.tsx
RUN cat > /home/user/myproject/app/layout.tsx <<'EOF'
import React from "react";

export const metadata = { title: "Multiplayer Form" };

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "sans-serif", maxWidth: 640, margin: "40px auto" }}>
        {children}
      </body>
    </html>
  );
}
EOF

# app/page.tsx — STATIC form skeleton only. The presence-driven typing
# indicator, the per-field lock overlay, the Liveblocks Storage wiring,
# and the auth endpoint are all the executor's responsibility.
RUN cat > /home/user/myproject/app/page.tsx <<'EOF'
"use client";

import React, { useState } from "react";

export default function Page() {
  // NOTE: This local React state is a placeholder. The executor is expected
  // to replace it with Liveblocks Storage + Presence so the form is synced
  // across users in real time, with per-field typing indicators and a soft
  // lock overlay.
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [bio, setBio] = useState("");

  return (
    <main>
      <h1>Multiplayer Form</h1>
      <p>Collaborate with other users in real time.</p>

      <div style={{ marginTop: 24 }}>
        <label htmlFor="name">Name</label>
        <div style={{ position: "relative" }}>
          <input
            id="name"
            data-testid="input-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ display: "block", width: "100%", padding: 8 }}
          />
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <label htmlFor="email">Email</label>
        <div style={{ position: "relative" }}>
          <input
            id="email"
            data-testid="input-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ display: "block", width: "100%", padding: 8 }}
          />
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <label htmlFor="bio">Bio</label>
        <div style={{ position: "relative" }}>
          <textarea
            id="bio"
            data-testid="input-bio"
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            rows={4}
            style={{ display: "block", width: "100%", padding: 8 }}
          />
        </div>
      </div>
    </main>
  );
}
EOF

# Install npm dependencies during image build so node_modules is preinstalled
# and the initial-state test passes without network at task start time.
RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="Next.js 14 App Router starter for a Liveblocks multiplayer form task; Liveblocks SDKs preinstalled, Playwright + Chromium ready for two-context verification."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#     plus the Chromium runtime libs for Playwright.
#   - Node.js 20 (per task requirement).
#   - pip3 packages: pytest-json-ctrf, pytest-xprocess, requests, playwright (with Chromium browser preinstalled).
#   - /home/user/myproject: Next.js 14 App Router starter with a static three-field form skeleton
#     (data-testid="input-name" / "input-email" / "input-bio"). @liveblocks/client, @liveblocks/react,
#     and @liveblocks/node are preinstalled, but no Liveblocks wiring, no /api/liveblocks-auth route,
#     no typing indicator, and no lock overlay yet — those are the executor's job.
