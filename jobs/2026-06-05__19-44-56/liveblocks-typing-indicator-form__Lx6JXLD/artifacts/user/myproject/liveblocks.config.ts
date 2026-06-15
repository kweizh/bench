import { LiveObject } from "@liveblocks/client";

declare global {
  interface Liveblocks {
    Presence: {
      typing: "name" | "email" | "bio" | null;
      info: {
        name: string;
      };
    };
    Storage: {
      form: LiveObject<{
        name: string;
        email: string;
        bio: string;
      }>;
    };
  }
}
