# Liveblocks Collaborative Whiteboard - Multi-user Shape Selection

## Background
You are extending a Next.js + React collaborative whiteboard powered by [Liveblocks](https://liveblocks.io). A starter scaffold lives at `/home/user/whiteboard` and already renders a fixed set of colored SVG shapes loaded from the room's `Storage` (`LiveList<Shape>`). What is missing is the **multi-user selection** feature.

The goal is that when one user clicks a shape, every other user in the same room sees a colored ring drawn around that shape, color-coded to the selecting user. The selection must be powered by Liveblocks `Presence` (transient state) — not by Storage — so it disappears when a user leaves.

Use the **real Liveblocks cloud service**. Do **NOT** mock or stub the Liveblocks client. Credentials are provided through environment variables.

## Requirements
1. **Type system (`liveblocks.config.ts`)** — Add the missing `Presence` type and complete the `Storage` type:
   - `Presence` must include a `selectedShapeId: string | null` field.
   - `Storage` must include `shapes: LiveList<LiveObject<{ id: string; x: number; y: number; width: number; height: number; fill: string }>>`.
2. **Shape seeding** — On a fresh room (empty `LiveList`), seed exactly 3 deterministic shapes via a Liveblocks mutation (do **NOT** use a server-side init). The shape IDs MUST be the literal strings `shape-a`, `shape-b`, `shape-c`, in that order. The seeding logic that already exists in the scaffold can be kept; you may need to wire it into the new `Storage` type.
3. **`<Whiteboard />` component** — Renders an SVG canvas (viewBox `0 0 800 600`) containing the 3 shapes from Storage. Each shape MUST be rendered as an SVG `<rect>` with attributes:
   - `data-shape-id="<shape.id>"`
   - `data-testid="shape"`
   - position/size driven by the shape's storage values.
   Clicking a shape MUST update the local user's `Presence.selectedShapeId` to that shape's id. Clicking the empty canvas background MUST clear it (set to `null`).
4. **Other-user selection indicators** — For every other user (from `useOthers()`) whose `presence.selectedShapeId` equals the rendered shape's id, draw a visible selection ring around that shape. Use overlapping SVG `<rect>` elements (one per other user) and:
   - Add `data-testid="selection-ring"`.
   - Add `data-selection-shape-id="<shapeId>"`.
   - Add `data-selection-connection-id="<other.connectionId>"`.
   - Set the `stroke` to a per-user color (use `other.info?.color` if present, otherwise pick deterministically from a fixed palette by `connectionId`).
   - Add `data-selection-color="<the stroke color>"`.
   Multiple other users selecting the same shape MUST produce multiple stacked rings (one per user).
5. **Room wiring** — The page MUST join a Liveblocks room whose ID is `whiteboard-${NEXT_PUBLIC_ZEALT_RUN_ID}`. Use `LiveblocksProvider` with `publicApiKey={process.env.NEXT_PUBLIC_LIVEBLOCKS_PUBLIC_KEY}` and a `RoomProvider` that supplies initial presence `{ selectedShapeId: null }` and initial storage with an empty `LiveList`. The evaluation harness only injects `ZEALT_RUN_ID` (server-side); the browser bundle cannot read it directly. You **MUST** re-export it as `NEXT_PUBLIC_ZEALT_RUN_ID` through `next.config.js` (e.g. `env.NEXT_PUBLIC_ZEALT_RUN_ID = process.env.ZEALT_RUN_ID`) or by writing it into `.env`/`.env.local` during build so `NEXT_PUBLIC_ZEALT_RUN_ID` mirrors `ZEALT_RUN_ID` exactly.
6. **Stable user color** — When a user joins, set `presence` or `info` so other clients can derive a stable per-user color. Use the `?user=<n>` query string already supported by the scaffold to pick a color: `n=1` → `#DC2626` (red), `n=2` → `#2563EB` (blue), default → `#059669` (green). Expose the color via `useOthers()` (i.e., on the `info` from auth or in presence) so other clients can render the correct ring color.

## Implementation Hints
- Liveblocks types are declared globally via `declare global { interface Liveblocks { Presence: ...; Storage: ...; UserMeta: ...; } }`.
- `useMutation(({ storage, setMyPresence }) => { ... })` gives you the mutable root for seeding and updating storage.
- `useStorage((root) => root.shapes)` returns an immutable view; iterate it to render shapes.
- `useOthers()` returns an array of other users with `connectionId`, `presence`, and `info`.
- For per-user color, the public-key flow supports passing user info via the `?user=<n>` query string already handled by the scaffold's `/api/liveblocks-auth` route — you do NOT need to modify the auth route, but you DO need to make the user color visible to other clients (e.g., via `presence.color`).
- Read the run-id from `process.env.NEXT_PUBLIC_ZEALT_RUN_ID`. The scaffold's `next.config.js` already mirrors `ZEALT_RUN_ID` into `NEXT_PUBLIC_ZEALT_RUN_ID`; if you replace that file, you MUST preserve the re-export.
- DO NOT mock the Liveblocks client. The app must connect to the real Liveblocks cloud.
- Keep all selection state in `Presence`, NOT in Storage.

## Acceptance Criteria
- Project path: `/home/user/whiteboard`
- Start command: `npm run dev`
- Port: `3000`
- The Liveblocks room ID MUST be `whiteboard-${NEXT_PUBLIC_ZEALT_RUN_ID}` where `NEXT_PUBLIC_ZEALT_RUN_ID` mirrors the `ZEALT_RUN_ID` provided to the container.
- Storage layout: `Storage.shapes` is a `LiveList` of `LiveObject` shapes with ids `shape-a`, `shape-b`, `shape-c` (seeded on first connection only).
- Presence layout: `Presence.selectedShapeId: string | null` (initial `null`).
- DOM contract:
  - Each shape rect: `<rect data-testid="shape" data-shape-id="shape-a|shape-b|shape-c" ...>`.
  - Each other-user selection ring: `<rect data-testid="selection-ring" data-selection-shape-id="<id>" data-selection-connection-id="<n>" data-selection-color="<#RRGGBB>" stroke="<#RRGGBB>" ...>`.
- Browser behavior verified with Playwright across two concurrent browser contexts:
  - Both contexts navigate to `http://localhost:3000/?user=1` and `http://localhost:3000/?user=2` respectively and see 3 shapes.
  - When context 1 clicks `[data-shape-id="shape-b"]`, context 2 eventually renders a `[data-testid="selection-ring"][data-selection-shape-id="shape-b"]` with `data-selection-color="#DC2626"`.
  - When context 1 then clicks `[data-shape-id="shape-c"]`, the ring on `shape-b` disappears in context 2 and a new ring with `data-selection-color="#DC2626"` appears on `shape-c`.
  - When context 1 clicks the empty SVG canvas background, the ring disappears in context 2.

