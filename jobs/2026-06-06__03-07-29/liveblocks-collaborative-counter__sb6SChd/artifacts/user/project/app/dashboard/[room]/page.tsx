"use client";

import { useParams } from "next/navigation";
import { useStorage, useMutation } from "@liveblocks/react/suspense";
import { LiveObject } from "@liveblocks/client";
import { Room } from "./Room";
import { useState, useEffect, useCallback } from "react";

function Dashboard() {
  // Identity management with localStorage persistence
  const [identity, setIdentity] = useState<string>("anonymous");

  useEffect(() => {
    try {
      const saved = localStorage.getItem("liveblocks-identity");
      if (saved) setIdentity(saved);
    } catch {}
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("liveblocks-identity", identity);
    } catch {}
  }, [identity]);

  // Read counters from storage
  const counters = useStorage((root) => root.counters);

  // Create counter mutation
  const createCounter = useMutation(
    ({ storage }, key: string, initialValue: number) => {
      const countersMap = storage.get("counters");
      if (countersMap.has(key)) return; // Don't overwrite existing
      countersMap.set(
        key,
        new LiveObject({
          value: initialValue,
          lastIncrementBy: identity,
          lastUpdated: Date.now(),
        })
      );
    },
    [identity]
  );

  // Increment mutation
  const increment = useMutation(
    ({ storage }, key: string) => {
      const countersMap = storage.get("counters");
      const counter = countersMap.get(key);
      if (!counter) return;
      counter.set({
        value: counter.get("value") + 1,
        lastIncrementBy: identity,
        lastUpdated: Date.now(),
      });
    },
    [identity]
  );

  // Decrement mutation
  const decrement = useMutation(
    ({ storage }, key: string) => {
      const countersMap = storage.get("counters");
      const counter = countersMap.get(key);
      if (!counter) return;
      counter.set({
        value: counter.get("value") - 1,
        lastIncrementBy: identity,
        lastUpdated: Date.now(),
      });
    },
    [identity]
  );

  // Reset all mutation
  const resetAll = useMutation(
    ({ storage }) => {
      const countersMap = storage.get("counters");
      for (const counter of countersMap.values()) {
        counter.set({
          value: 0,
          lastIncrementBy: identity,
          lastUpdated: Date.now(),
        });
      }
    },
    [identity]
  );

  // State for new counter form
  const [newKey, setNewKey] = useState("");
  const [newInitial, setNewInitial] = useState(0);

  // Convert counters to array for rendering
  const counterEntries = Array.from(counters.entries());

  const handleCreateCounter = useCallback(() => {
    if (newKey.trim()) {
      createCounter(newKey.trim(), newInitial);
      setNewKey("");
      setNewInitial(0);
    }
  }, [newKey, newInitial, createCounter]);

  return (
    <main style={{ padding: 24, fontFamily: "system-ui" }}>
      <h1>Collaborative Counter Dashboard</h1>

      {/* Identity input */}
      <div style={{ marginBottom: 16 }}>
        <label htmlFor="identity">Identity: </label>
        <input
          id="identity"
          data-testid="identity-input"
          value={identity}
          onChange={(e) => setIdentity(e.target.value)}
        />
      </div>

      {/* Create counter form */}
      <div style={{ marginBottom: 16 }}>
        <h2>Create Counter</h2>
        <input
          data-testid="new-counter-key"
          placeholder="Counter key"
          value={newKey}
          onChange={(e) => setNewKey(e.target.value)}
        />
        <input
          data-testid="new-counter-initial"
          type="number"
          placeholder="Initial value"
          value={newInitial}
          onChange={(e) => setNewInitial(Number(e.target.value))}
        />
        <button data-testid="create-counter" onClick={handleCreateCounter}>
          Create counter
        </button>
      </div>

      {/* Counter list */}
      <div>
        <h2>Counters</h2>
        {counterEntries.map(([key, counter]) => (
          <div
            key={key}
            data-testid="counter-row"
            data-counter-key={key}
            style={{ marginBottom: 8, padding: 8, border: "1px solid #ccc" }}
          >
            <span>{key}: </span>
            <span data-testid="counter-value">{counter.value}</span>
            <button data-testid="increment" onClick={() => increment(key)}>
              Increment
            </button>
            <button data-testid="decrement" onClick={() => decrement(key)}>
              Decrement
            </button>
            <div data-testid="last-touched">
              Last touched by {counter.lastIncrementBy} at{" "}
              {new Date(counter.lastUpdated).toISOString()}
            </div>
          </div>
        ))}
      </div>

      {/* Reset all */}
      <div style={{ marginTop: 16 }}>
        <button data-testid="reset-all" onClick={() => resetAll()}>
          Reset all
        </button>
      </div>
    </main>
  );
}

export default function DashboardPage() {
  const params = useParams<{ room: string }>();
  const roomId =
    (Array.isArray(params?.room) ? params?.room[0] : params?.room) ||
    "default-room";

  return (
    <Room roomId={roomId}>
      <Dashboard />
    </Room>
  );
}