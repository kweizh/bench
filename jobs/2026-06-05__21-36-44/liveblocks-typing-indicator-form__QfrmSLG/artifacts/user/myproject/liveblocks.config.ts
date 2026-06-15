import { createClient } from "@liveblocks/client";
import { createRoomContext } from "@liveblocks/react";
import { LiveObject } from "@liveblocks/client";

// Define the shape of Presence for each user
type Presence = {
  typing: "name" | "email" | "bio" | null;
  info: {
    name: string;
  };
};

// Define the shape of Storage
type Storage = {
  form: LiveObject<{
    name: string;
    email: string;
    bio: string;
  }>;
};

// Create the Liveblocks client
const client = createClient({
  authEndpoint: "/api/liveblocks-auth",
});

// Create typed room context
export const {
  RoomProvider,
  useMyPresence,
  useUpdateMyPresence,
  useOthers,
  useStorage,
  useMutation,
} = createRoomContext<Presence, Storage>(client);
