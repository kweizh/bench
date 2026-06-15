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
    // Per-user transient state for multi-user selection.
    Presence: {
      selectedShapeId: string | null;
      color: string;
    };
    // The Storage tree for the room.
    Storage: {
      shapes: LiveList<Shape>;
    };
    // The UserMeta interface for per-user info.
    UserMeta: {
      id?: string;
      info?: {
        color?: string;
      };
    };
  }
}

export {};
