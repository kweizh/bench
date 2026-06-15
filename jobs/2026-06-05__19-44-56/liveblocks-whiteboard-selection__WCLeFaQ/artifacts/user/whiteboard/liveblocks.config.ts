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
    Presence: {
      selectedShapeId: string | null;
      color: string;
    };
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
