import type { LiveMap, LiveObject } from "@liveblocks/client";

/**
 * Storage layout for the collaborative counter dashboard.
 *
 * Each entry of `counters` is a LiveObject with the three required fields:
 *   - value: number
 *   - lastIncrementBy: string
 *   - lastUpdated: number (ms epoch)
 *
 * The executor must use these types together with `useMutation`/`useStorage`
 * to read and write the Storage tree.
 */
export type Counter = {
  value: number;
  lastIncrementBy: string;
  lastUpdated: number;
};

export type Storage = {
  counters: LiveMap<string, LiveObject<Counter>>;
};

export type Presence = Record<string, never>;

export type UserMeta = {
  id?: string;
  info?: { name?: string };
};

declare global {
  interface Liveblocks {
    Storage: Storage;
    Presence: Presence;
    UserMeta: UserMeta;
  }
}
