"use client";

import React, { useEffect, useState } from "react";
import {
  useStorage,
  useMutation,
  useOthers,
  useUpdateMyPresence,
} from "../../liveblocks.config";

type FieldId = "name" | "email" | "bio";

const FIELD_LABELS: Record<FieldId, string> = {
  name: "Name",
  email: "Email",
  bio: "Bio",
};

function TypingIndicator({ field }: { field: FieldId }) {
  const others = useOthers();
  const typingUsers = others.filter(
    (other) => other.presence?.typing === field
  );

  if (typingUsers.length === 0) return null;

  const label = FIELD_LABELS[field];

  return (
    <div
      data-testid={`typing-indicator-${field}`}
      style={{ fontSize: 12, color: "#888", minHeight: 18, marginBottom: 2 }}
    >
      {typingUsers.map((user, i) => {
        const userName = user.presence?.info?.name ?? "Someone";
        return (
          <span key={user.connectionId}>
            {i > 0 ? ", " : ""}
            {userName} is typing in {label}…
          </span>
        );
      })}
    </div>
  );
}

function LockOverlay({ field }: { field: FieldId }) {
  const others = useOthers();
  const isLockedByOther = others.some(
    (other) => other.presence?.typing === field
  );

  if (!isLockedByOther) return null;

  return (
    <div
      data-testid={`lock-overlay-${field}`}
      style={{
        position: "absolute",
        inset: 0,
        backgroundColor: "rgba(200, 200, 200, 0.4)",
        borderRadius: 4,
        pointerEvents: "none",
        zIndex: 1,
      }}
    />
  );
}

export function MultiplayerForm() {
  const [displayName, setDisplayName] = useState("Anonymous");
  const updateMyPresence = useUpdateMyPresence();

  // Read display name from URL query param on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const nameParam = params.get("name");
    const name = nameParam || "Anonymous";
    setDisplayName(name);
    // Update presence with the resolved display name
    updateMyPresence({ info: { name } });
  }, [updateMyPresence]);

  // Read form values from Storage
  const formData = useStorage((root) => root.form);

  // Mutation to update a single field in storage
  const updateField = useMutation(
    ({ storage }, field: FieldId, value: string) => {
      storage.get("form").set(field, value);
    },
    []
  );

  const handleFocus = (field: FieldId) => {
    updateMyPresence({ typing: field });
  };

  const handleBlur = () => {
    updateMyPresence({ typing: null });
  };

  const handleChange = (field: FieldId, value: string) => {
    updateField(field, value);
    updateMyPresence({ typing: field });
  };

  if (formData === null) {
    return <div>Loading…</div>;
  }

  return (
    <main>
      <h1>Multiplayer Form</h1>
      <p>Collaborate with other users in real time.</p>

      {/* Name field */}
      <div style={{ marginTop: 24 }}>
        <label htmlFor="name">Name</label>
        <TypingIndicator field="name" />
        <div style={{ position: "relative" }}>
          <LockOverlay field="name" />
          <input
            id="name"
            data-testid="input-name"
            type="text"
            value={formData.name ?? ""}
            onFocus={() => handleFocus("name")}
            onBlur={handleBlur}
            onChange={(e) => handleChange("name", e.target.value)}
            style={{ display: "block", width: "100%", padding: 8, boxSizing: "border-box" }}
          />
        </div>
      </div>

      {/* Email field */}
      <div style={{ marginTop: 16 }}>
        <label htmlFor="email">Email</label>
        <TypingIndicator field="email" />
        <div style={{ position: "relative" }}>
          <LockOverlay field="email" />
          <input
            id="email"
            data-testid="input-email"
            type="email"
            value={formData.email ?? ""}
            onFocus={() => handleFocus("email")}
            onBlur={handleBlur}
            onChange={(e) => handleChange("email", e.target.value)}
            style={{ display: "block", width: "100%", padding: 8, boxSizing: "border-box" }}
          />
        </div>
      </div>

      {/* Bio field */}
      <div style={{ marginTop: 16 }}>
        <label htmlFor="bio">Bio</label>
        <TypingIndicator field="bio" />
        <div style={{ position: "relative" }}>
          <LockOverlay field="bio" />
          <textarea
            id="bio"
            data-testid="input-bio"
            value={formData.bio ?? ""}
            onFocus={() => handleFocus("bio")}
            onBlur={handleBlur}
            onChange={(e) => handleChange("bio", e.target.value)}
            rows={4}
            style={{ display: "block", width: "100%", padding: 8, boxSizing: "border-box" }}
          />
        </div>
      </div>
    </main>
  );
}
