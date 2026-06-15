"use client";

import { useParams } from "next/navigation";
import { useState, useEffect } from "react";
import { LiveObject } from "@liveblocks/client";
import { useStorage, useMutation } from "@liveblocks/react/suspense";
import { Room } from "./Room";

function Dashboard() {
  const [identity, setIdentity] = useState<string>("anonymous");

  useEffect(() => {
    const saved = localStorage.getItem("counter-identity");
    if (saved) {
      setIdentity(saved);
    }
  }, []);

  const handleIdentityChange = (val: string) => {
    setIdentity(val);
    localStorage.setItem("counter-identity", val);
  };

  const counters = useStorage((root) => root.counters);

  const [newKey, setNewKey] = useState("");
  const [newInitial, setNewInitial] = useState<number>(0);

  const createCounter = useMutation(({ storage }, key: string, initialValue: number) => {
    const countersMap = storage.get("counters");
    if (!countersMap) return;
    if (countersMap.has(key)) return;
    countersMap.set(
      key,
      new LiveObject({
        value: initialValue,
        lastIncrementBy: identity || "anonymous",
        lastUpdated: Date.now()
      })
    );
  }, [identity]);

  const handleCreateCounter = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedKey = newKey.trim();
    if (!trimmedKey) return;
    createCounter(trimmedKey, newInitial);
    setNewKey("");
    setNewInitial(0);
  };

  const increment = useMutation(({ storage }, key: string) => {
    const countersMap = storage.get("counters");
    if (!countersMap) return;
    const counter = countersMap.get(key);
    if (counter) {
      counter.set("value", counter.get("value") + 1);
      counter.set("lastIncrementBy", identity || "anonymous");
      counter.set("lastUpdated", Date.now());
    }
  }, [identity]);

  const decrement = useMutation(({ storage }, key: string) => {
    const countersMap = storage.get("counters");
    if (!countersMap) return;
    const counter = countersMap.get(key);
    if (counter) {
      counter.set("value", counter.get("value") - 1);
      counter.set("lastIncrementBy", identity || "anonymous");
      counter.set("lastUpdated", Date.now());
    }
  }, [identity]);

  const resetAll = useMutation(({ storage }) => {
    const countersMap = storage.get("counters");
    if (!countersMap) return;
    countersMap.forEach((counter) => {
      counter.set("value", 0);
      counter.set("lastIncrementBy", identity || "anonymous");
      counter.set("lastUpdated", Date.now());
    });
  }, [identity]);

  return (
    <main style={{ padding: 24, fontFamily: "system-ui", maxWidth: 600, margin: "0 auto" }}>
      <h1>Collaborative Counter Dashboard</h1>

      {/* Identity input section */}
      <div style={{ marginBottom: 24, padding: 16, border: "1px solid #ccc", borderRadius: 8 }}>
        <label style={{ display: "block", marginBottom: 8, fontWeight: "bold" }}>
          Your Identity:
        </label>
        <input
          type="text"
          data-testid="identity-input"
          value={identity}
          onChange={(e) => handleIdentityChange(e.target.value)}
          style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ccc", boxSizing: "border-box" }}
        />
      </div>

      {/* Create counter form */}
      <div style={{ marginBottom: 24, padding: 16, border: "1px solid #ccc", borderRadius: 8 }}>
        <h2 style={{ marginTop: 0 }}>Create a Counter</h2>
        <form onSubmit={handleCreateCounter} style={{ display: "flex", gap: 8, flexDirection: "column" }}>
          <div>
            <label style={{ display: "block", marginBottom: 4 }}>Counter Key:</label>
            <input
              type="text"
              data-testid="new-counter-key"
              value={newKey}
              onChange={(e) => setNewKey(e.target.value)}
              placeholder="e.g. coffee-consumed"
              style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ccc", boxSizing: "border-box" }}
              required
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 4 }}>Initial Value:</label>
            <input
              type="number"
              data-testid="new-counter-initial"
              value={newInitial}
              onChange={(e) => setNewInitial(Number(e.target.value))}
              style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ccc", boxSizing: "border-box" }}
              required
            />
          </div>
          <button
            type="submit"
            data-testid="create-counter"
            style={{ padding: "10px 16px", backgroundColor: "#0070f3", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontWeight: "bold" }}
          >
            Create counter
          </button>
        </form>
      </div>

      {/* Global Reset Button */}
      <div style={{ marginBottom: 24 }}>
        <button
          data-testid="reset-all"
          onClick={resetAll}
          style={{ width: "100%", padding: "12px", backgroundColor: "#ff0000", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontWeight: "bold" }}
        >
          Reset all
        </button>
      </div>

      {/* Counters List */}
      <div>
        <h2>Counters</h2>
        {counters && Array.from(counters.entries()).length === 0 ? (
          <p>No counters created yet. Create one above!</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {counters &&
              Array.from(counters.entries()).map(([key, counter]) => {
                if (!counter) return null;
                return (
                  <div
                    key={key}
                    data-testid="counter-row"
                    data-counter-key={key}
                    style={{
                      padding: 16,
                      border: "1px solid #eaeaea",
                      borderRadius: 8,
                      display: "flex",
                      flexDirection: "column",
                      gap: 8,
                      backgroundColor: "#fafafa"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontWeight: "bold", fontSize: "1.1rem" }}>{key}</span>
                      <span
                        data-testid="counter-value"
                        style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#0070f3" }}
                      >
                        {counter.value}
                      </span>
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        data-testid="increment"
                        onClick={() => increment(key)}
                        style={{
                          flex: 1,
                          padding: "8px",
                          backgroundColor: "#4caf50",
                          color: "#fff",
                          border: "none",
                          borderRadius: 4,
                          cursor: "pointer",
                          fontWeight: "bold"
                        }}
                      >
                        Increment
                      </button>
                      <button
                        data-testid="decrement"
                        onClick={() => decrement(key)}
                        style={{
                          flex: 1,
                          padding: "8px",
                          backgroundColor: "#f44336",
                          color: "#fff",
                          border: "none",
                          borderRadius: 4,
                          cursor: "pointer",
                          fontWeight: "bold"
                        }}
                      >
                        Decrement
                      </button>
                    </div>
                    <div
                      data-testid="last-touched"
                      style={{ fontSize: "0.85rem", color: "#666", marginTop: 4 }}
                    >
                      Last touched by {counter.lastIncrementBy} at {new Date(counter.lastUpdated).toISOString()}
                    </div>
                  </div>
                );
              })}
          </div>
        )}
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
