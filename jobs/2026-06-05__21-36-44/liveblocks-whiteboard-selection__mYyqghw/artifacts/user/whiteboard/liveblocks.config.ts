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
    // Per-user transient state: which shape (if any) the user has selected.
    Presence: {
      selectedShapeId: string | null;
      color?: string;
    };
    // The Storage tree for the room.
    Storage: {
      shapes: LiveList<Shape>;
    };
    // Per-user metadata: stable color for selection rings.
    UserMeta: {
      id?: string;
      info?: {
        color?: string;
      };
    };
  }
}

export {};
