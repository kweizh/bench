"use client";

import { useParams } from "next/navigation";
import { Room } from "./Room";
import { useState, useEffect, useCallback } from "react";
import { useStorage, useMutation } from "@liveblocks/react/suspense";
import { LiveObject } from "@liveblocks/client";

function Dashboard() {
  const [identity, setIdentity] = useState("anonymous");
  const [newCounterKey, setNewCounterKey] = useState("");
  const [newCounterInitialValue, setNewCounterInitialValue] = useState(0);

  // Load identity from localStorage on mount
  useEffect(() => {
    const savedIdentity = localStorage.getItem("counter-identity");
    if (savedIdentity) {
      setIdentity(savedIdentity);
    }
  }, []);

  // Save identity to localStorage when it changes
  const handleIdentityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newId = e.target.value;
    setIdentity(newId);
    localStorage.setItem("counter-identity", newId);
  };

  const counters = useStorage((root) => root.counters);

  const createCounter = useMutation(({ storage }, key: string, initialValue: number, userId: string) => {
    const countersMap = storage.get("counters");
    if (!countersMap.has(key)) {
      countersMap.set(key, new LiveObject({
        value: initialValue,
        lastIncrementBy: userId,
        lastUpdated: Date.now(),
      }));
    }
  }, []);

  const increment = useMutation(({ storage }, key: string, userId: string) => {
    const countersMap = storage.get("counters");
    const counter = countersMap.get(key);
    if (counter) {
      counter.update({
        value: counter.get("value") + 1,
        lastIncrementBy: userId,
        lastUpdated: Date.now(),
      });
    }
  }, []);

  const decrement = useMutation(({ storage }, key: string, userId: string) => {
    const countersMap = storage.get("counters");
    const counter = countersMap.get(key);
    if (counter) {
      counter.update({
        value: counter.get("value") - 1,
        lastIncrementBy: userId,
        lastUpdated: Date.now(),
      });
    }
  }, []);

  const resetAll = useMutation(({ storage }, userId: string) => {
    const countersMap = storage.get("counters");
    countersMap.forEach((counter) => {
      counter.update({
        value: 0,
        lastIncrementBy: userId,
        lastUpdated: Date.now(),
      });
    });
  }, []);

  const handleCreateCounter = (e: React.FormEvent) => {
    e.preventDefault();
    if (newCounterKey.trim()) {
      createCounter(newCounterKey, newCounterInitialValue, identity || "anonymous");
      setNewCounterKey("");
      setNewCounterInitialValue(0);
    }
  };

  return (
    <main style={{ padding: 24, fontFamily: "system-ui" }}>
      <h1>Collaborative Counter Dashboard</h1>
      
      <div style={{ marginBottom: 24 }}>
        <label>
          Your Identity:{" "}
          <input
            type="text"
            value={identity}
            onChange={handleIdentityChange}
            data-testid="identity-input"
          />
        </label>
      </div>

      <form onSubmit={handleCreateCounter} style={{ marginBottom: 24 }}>
        <input
          type="text"
          placeholder="Counter key"
          value={newCounterKey}
          onChange={(e) => setNewCounterKey(e.target.value)}
          data-testid="new-counter-key"
        />
        <input
          type="number"
          placeholder="Initial value"
          value={newCounterInitialValue}
          onChange={(e) => setNewCounterInitialValue(Number(e.target.value))}
          data-testid="new-counter-initial"
        />
        <button type="submit" data-testid="create-counter">
          Create counter
        </button>
      </form>

      <div style={{ marginBottom: 24 }}>
        <button onClick={() => resetAll(identity || "anonymous")} data-testid="reset-all">
          Reset all
        </button>
      </div>

      <div>
        {Array.from(counters.entries()).map(([key, counter]) => (
          <div
            key={key}
            data-testid="counter-row"
            data-counter-key={key}
            style={{ border: "1px solid #ccc", padding: 12, marginBottom: 8 }}
          >
            <strong>{key}</strong>: <span data-testid="counter-value">{counter.value}</span>
            <div style={{ marginTop: 8 }}>
              <button onClick={() => increment(key, identity || "anonymous")} data-testid="increment">
                Increment
              </button>
              <button onClick={() => decrement(key, identity || "anonymous")} data-testid="decrement">
                Decrement
              </button>
            </div>
            <div style={{ marginTop: 8, fontSize: "0.9em", color: "#666" }} data-testid="last-touched">
              Last touched by {counter.lastIncrementBy} at {new Date(counter.lastUpdated).toISOString()}
            </div>
          </div>
        ))}
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
