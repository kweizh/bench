"use client";

import { useParams } from "next/navigation";
import { Room } from "./Room";
import { useStorage, useMutation } from "@liveblocks/react/suspense";
import { LiveObject } from "@liveblocks/client";
import { useState, useEffect } from "react";

function Dashboard() {
  const [identity, setIdentity] = useState("anonymous");
  
  useEffect(() => {
    const saved = localStorage.getItem("identity");
    if (saved) setIdentity(saved);
  }, []);

  const handleIdentityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newIdentity = e.target.value;
    setIdentity(newIdentity);
    localStorage.setItem("identity", newIdentity);
  };

  const counters = useStorage((root) => root.counters);

  const [newKey, setNewKey] = useState("");
  const [newInitial, setNewInitial] = useState(0);

  const createCounter = useMutation(({ storage }, key: string, initialValue: number) => {
    const countersMap = storage.get("counters");
    if (!countersMap.has(key)) {
      countersMap.set(
        key,
        new LiveObject({
          value: initialValue,
          lastIncrementBy: identity,
          lastUpdated: Date.now()
        })
      );
    }
  }, [identity]);

  const increment = useMutation(({ storage }, key: string) => {
    const countersMap = storage.get("counters");
    const counter = countersMap.get(key);
    if (counter) {
      counter.set("value", counter.get("value") + 1);
      counter.set("lastIncrementBy", identity);
      counter.set("lastUpdated", Date.now());
    }
  }, [identity]);

  const decrement = useMutation(({ storage }, key: string) => {
    const countersMap = storage.get("counters");
    const counter = countersMap.get(key);
    if (counter) {
      counter.set("value", counter.get("value") - 1);
      counter.set("lastIncrementBy", identity);
      counter.set("lastUpdated", Date.now());
    }
  }, [identity]);

  const resetAll = useMutation(({ storage }) => {
    const countersMap = storage.get("counters");
    const now = Date.now();
    for (const [key, counter] of countersMap.entries()) {
      counter.set("value", 0);
      counter.set("lastIncrementBy", identity);
      counter.set("lastUpdated", now);
    }
  }, [identity]);

  return (
    <main style={{ padding: 24, fontFamily: "system-ui" }}>
      <h1>Collaborative Counter Dashboard</h1>
      
      <div style={{ marginBottom: 20 }}>
        <label>
          Identity:{" "}
          <input
            data-testid="identity-input"
            value={identity}
            onChange={handleIdentityChange}
          />
        </label>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (newKey) {
            createCounter(newKey, newInitial);
            setNewKey("");
            setNewInitial(0);
          }
        }}
        style={{ marginBottom: 20 }}
      >
        <input
          data-testid="new-counter-key"
          placeholder="Counter Key"
          value={newKey}
          onChange={(e) => setNewKey(e.target.value)}
        />
        <input
          type="number"
          data-testid="new-counter-initial"
          value={newInitial}
          onChange={(e) => setNewInitial(Number(e.target.value))}
        />
        <button type="submit" data-testid="create-counter">
          Create counter
        </button>
      </form>

      <button data-testid="reset-all" onClick={() => resetAll()} style={{ marginBottom: 20 }}>
        Reset all
      </button>

      <div>
        {Array.from(counters.entries()).map(([key, counter]) => (
          <div key={key} data-testid="counter-row" data-counter-key={key} style={{ border: "1px solid #ccc", padding: 10, marginBottom: 10 }}>
            <h3>{key}</h3>
            <p data-testid="counter-value">{counter.value}</p>
            <button data-testid="increment" onClick={() => increment(key)}>
              Increment
            </button>
            <button data-testid="decrement" onClick={() => decrement(key)}>
              Decrement
            </button>
            <p data-testid="last-touched">
              Last touched by {counter.lastIncrementBy} at {new Date(counter.lastUpdated).toISOString()}
            </p>
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
