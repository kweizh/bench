"use client";

import React, { Suspense } from "react";
import { Room } from "./Room";
import {
  useStorage,
  useMutation,
  useUpdateMyPresence,
  useOthers,
} from "./liveblocks.config";

function Form() {
  const form = useStorage((root) => root.form);
  const updateMyPresence = useUpdateMyPresence();
  const others = useOthers();

  const updateField = useMutation(({ storage }, field: "name" | "email" | "bio", value: string) => {
    storage.get("form").set(field, value);
  }, []);

  if (!form) return <div>Loading...</div>;

  const getTypingUsers = (field: "name" | "email" | "bio") => {
    return others
      .filter((other) => other.presence?.typing === field)
      .map((other) => other.presence?.info?.name || "Anonymous");
  };

  const renderField = (
    id: "name" | "email" | "bio",
    label: string,
    type: "text" | "email" | "textarea"
  ) => {
    const typingUsers = getTypingUsers(id);
    const isLocked = typingUsers.length > 0;

    return (
      <div style={{ marginTop: id === "name" ? 24 : 16 }}>
        {isLocked && (
          <div
            data-testid={`typing-indicator-${id}`}
            style={{ fontSize: "0.875rem", color: "#666", marginBottom: 4 }}
          >
            {typingUsers.join(", ")} {typingUsers.length > 1 ? "are" : "is"} typing in {label}...
          </div>
        )}
        <label htmlFor={id}>{label}</label>
        <div style={{ position: "relative" }}>
          {isLocked && (
            <div
              data-testid={`lock-overlay-${id}`}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: "rgba(200, 200, 200, 0.5)",
                pointerEvents: "none",
                zIndex: 10,
              }}
            />
          )}
          {type === "textarea" ? (
            <textarea
              id={id}
              data-testid={`input-${id}`}
              value={form[id]}
              onChange={(e) => {
                updateField(id, e.target.value);
                updateMyPresence({ typing: id });
              }}
              onFocus={() => updateMyPresence({ typing: id })}
              onBlur={() => updateMyPresence({ typing: null })}
              rows={4}
              style={{ display: "block", width: "100%", padding: 8 }}
            />
          ) : (
            <input
              id={id}
              data-testid={`input-${id}`}
              type={type}
              value={form[id]}
              onChange={(e) => {
                updateField(id, e.target.value);
                updateMyPresence({ typing: id });
              }}
              onFocus={() => updateMyPresence({ typing: id })}
              onBlur={() => updateMyPresence({ typing: null })}
              style={{ display: "block", width: "100%", padding: 8 }}
            />
          )}
        </div>
      </div>
    );
  };

  return (
    <main style={{ padding: 24, maxWidth: 600, margin: "0 auto" }}>
      <h1>Multiplayer Form</h1>
      <p>Collaborate with other users in real time.</p>

      {renderField("name", "Name", "text")}
      {renderField("email", "Email", "email")}
      {renderField("bio", "Bio", "textarea")}
    </main>
  );
}

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Room>
        <Form />
      </Room>
    </Suspense>
  );
}
