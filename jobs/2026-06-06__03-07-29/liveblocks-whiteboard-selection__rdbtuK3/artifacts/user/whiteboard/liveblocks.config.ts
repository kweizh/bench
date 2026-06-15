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
    Presence: {
      selectedShapeId: string | null;
      color: string;
    };
    Storage: {
      shapes: LiveList<Shape>;
    };
    UserMeta: {
      id?: string;
      info?: {
        color?: string;
      };
    };
  }
}

export {};