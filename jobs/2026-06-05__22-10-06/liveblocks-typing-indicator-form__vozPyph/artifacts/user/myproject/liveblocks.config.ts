import { createClient, LiveObject } from "@liveblocks/client";
import { createRoomContext } from "@liveblocks/react";

const client = createClient({
  authEndpoint: "/api/liveblocks-auth",
});

type Presence = {
  typing: "name" | "email" | "bio" | null;
  info: {
    name: string;
  };
};

type Storage = {
  form: LiveObject<{
    name: string;
    email: string;
    bio: string;
  }>;
};

export const {
  RoomProvider,
  useMyPresence,
  useUpdateMyPresence,
  useOthers,
  useStorage,
  useMutation,
} = createRoomContext<Presence, Storage>(client);
