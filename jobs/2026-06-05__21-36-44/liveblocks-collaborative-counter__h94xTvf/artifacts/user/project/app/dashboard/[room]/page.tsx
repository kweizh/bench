"use client";

import { useParams } from "next/navigation";
import { Room } from "./Room";
import { useStorage, useMutation } from "@liveblocks/react/suspense";
import { LiveObject } from "@liveblocks/client";
import { useState, useEffect, FormEvent } from "react";

function Dashboard() {
  // Identity: persist in localStorage, default to "anonymous"
  const [identity, setIdentity] = useState<string>("anonymous");

  useEffect(() => {
    const stored = localStorage.getItem("liveblocks-identity");
    if (stored) setIdentity(stored);
  }, []);

  const handleIdentityChange = (val: string) => {
    setIdentity(val);
    localStorage.setItem("liveblocks-identity", val);
  };

  // New counter form state
  const [newKey, setNewKey] = useState("");
  const [newInitial, setNewInitial] = useState("0");

  // Read counters from Storage
  const counters = useStorage((root) => root.counters);

  // Mutation: create counter
  const createCounter = useMutation(
    ({ storage }, key: string, initialValue: number, user: string) => {
      const countersMap = storage.get("counters");
      if (countersMap.get(key) !== undefined) {
        // Key already exists — do not overwrite
        return;
      }
      countersMap.set(
        key,
        new LiveObject({
          value: initialValue,
          lastIncrementBy: user,
          lastUpdated: Date.now(),
        })
      );
    },
    []
  );

  // Mutation: increment counter
  const increment = useMutation(
    ({ storage }, key: string, user: string) => {
      const countersMap = storage.get("counters");
      const counter = countersMap.get(key);
      if (!counter) return;
      counter.set("value", counter.get("value") + 1);
      counter.set("lastIncrementBy", user);
      counter.set("lastUpdated", Date.now());
    },
    []
  );

  // Mutation: decrement counter
  const decrement = useMutation(
    ({ storage }, key: string, user: string) => {
      const countersMap = storage.get("counters");
      const counter = countersMap.get(key);
      if (!counter) return;
      counter.set("value", counter.get("value") - 1);
      counter.set("lastIncrementBy", user);
      counter.set("lastUpdated", Date.now());
    },
    []
  );

  // Mutation: reset all counters
  const resetAll = useMutation(
    ({ storage }, user: string) => {
      const countersMap = storage.get("counters");
      countersMap.forEach((counter) => {
        counter.set("value", 0);
        counter.set("lastIncrementBy", user);
        counter.set("lastUpdated", Date.now());
      });
    },
    []
  );

  const handleCreateCounter = (e: FormEvent) => {
    e.preventDefault();
    const trimmedKey = newKey.trim();
    if (!trimmedKey) return;
    const initialValue = parseInt(newInitial, 10);
    createCounter(trimmedKey, isNaN(initialValue) ? 0 : initialValue, identity);
    setNewKey("");
    setNewInitial("0");
  };

  // Convert the ReadonlyMap to a sorted array for rendering
  const counterEntries: [string, { value: number; lastIncrementBy: string; lastUpdated: number }][] =
    counters ? Array.from(counters.entries()) : [];

  return (
    <main style={{ padding: 24, fontFamily: "system-ui", maxWidth: 700 }}>
      <h1>Collaborative Counter Dashboard</h1>

      {/* Identity input */}
      <section style={{ marginBottom: 24 }}>
        <label htmlFor="identity-input" style={{ marginRight: 8 }}>
          Your identity:
        </label>
        <input
          id="identity-input"
          data-testid="identity-input"
          type="text"
          value={identity}
          onChange={(e) => handleIdentityChange(e.target.value)}
          placeholder="anonymous"
          style={{ padding: "4px 8px", minWidth: 200 }}
        />
      </section>

      {/* Create counter form */}
      <section style={{ marginBottom: 32 }}>
        <h2>Create Counter</h2>
        <form onSubmit={handleCreateCounter} style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
          <input
            data-testid="new-counter-key"
            type="text"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            placeholder="Counter key"
            style={{ padding: "4px 8px", minWidth: 160 }}
          />
          <input
            data-testid="new-counter-initial"
            type="number"
            value={newInitial}
            onChange={(e) => setNewInitial(e.target.value)}
            placeholder="Initial value"
            style={{ padding: "4px 8px", width: 120 }}
          />
          <button
            data-testid="create-counter"
            type="submit"
            style={{ padding: "4px 12px" }}
          >
            Create counter
          </button>
        </form>
      </section>

      {/* Counter list */}
      <section>
        <h2>Counters</h2>
        {counterEntries.length === 0 && (
          <p style={{ color: "#888" }}>No counters yet. Create one above.</p>
        )}
        {counterEntries.map(([key, counter]) => (
          <div
            key={key}
            data-testid="counter-row"
            data-counter-key={key}
            style={{
              border: "1px solid #ddd",
              borderRadius: 6,
              padding: "12px 16px",
              marginBottom: 12,
              display: "flex",
              flexWrap: "wrap",
              alignItems: "center",
              gap: 12,
            }}
          >
            <strong style={{ minWidth: 120 }}>{key}</strong>
            <span data-testid="counter-value" style={{ fontSize: 24, fontWeight: "bold", minWidth: 60, textAlign: "center" }}>
              {counter.value}
            </span>
            <button
              data-testid="increment"
              onClick={() => increment(key, identity)}
              style={{ padding: "4px 12px" }}
            >
              Increment
            </button>
            <button
              data-testid="decrement"
              onClick={() => decrement(key, identity)}
              style={{ padding: "4px 12px" }}
            >
              Decrement
            </button>
            <span
              data-testid="last-touched"
              style={{ fontSize: 12, color: "#666", width: "100%" }}
            >
              Last touched by {counter.lastIncrementBy} at {new Date(counter.lastUpdated).toISOString()}
            </span>
          </div>
        ))}
      </section>

      {/* Global reset */}
      {counterEntries.length > 0 && (
        <section style={{ marginTop: 16 }}>
          <button
            data-testid="reset-all"
            onClick={() => resetAll(identity)}
            style={{ padding: "8px 20px", background: "#e53e3e", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}
          >
            Reset all
          </button>
        </section>
      )}
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
