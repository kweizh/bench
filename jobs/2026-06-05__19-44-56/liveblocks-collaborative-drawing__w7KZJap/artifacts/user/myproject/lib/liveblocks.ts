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
