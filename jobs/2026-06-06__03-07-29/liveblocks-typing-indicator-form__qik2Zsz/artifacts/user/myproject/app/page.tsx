"use client";

import {
  useStorage,
  useMutation,
  useOthers,
  useUpdateMyPresence,
} from "@liveblocks/react";
import { LiveObject } from "@liveblocks/client";
import { useEffect, useMemo } from "react";

type FieldId = "name" | "email" | "bio";

const FIELD_LABELS: Record<FieldId, string> = {
  name: "Name",
  email: "Email",
  bio: "Bio",
};

const FIELDS: FieldId[] = ["name", "email", "bio"];

export default function Page() {
  const form = useStorage((root: any) => root.form);
  const updateMyPresence = useUpdateMyPresence();
  const others = useOthers();

  // Get display name from URL query string
  const displayName = useMemo(() => {
    if (typeof window === "undefined") return "Anonymous";
    const params = new URLSearchParams(window.location.search);
    return params.get("name") || "Anonymous";
  }, []);

  // Update presence with display name from URL
  useEffect(() => {
    updateMyPresence({ info: { name: displayName } });
  }, [displayName, updateMyPresence]);

  // Mutation to update a form field in Storage
  const updateField = useMutation(
    ({ storage }, field: FieldId, value: string) => {
      const form = storage.get("form") as LiveObject<{ name: string; email: string; bio: string }>;
      if (form) {
        form.set(field, value);
      }
    },
    []
  );

  // Compute which other users are typing in each field
  const typingUsersByField = useMemo(() => {
    const result: Record<FieldId, string[]> = {
      name: [],
      email: [],
      bio: [],
    };
    others.forEach((other: any) => {
      const typing = other.presence?.typing as FieldId | null | undefined;
      if (typing && typing in result) {
        const name = other.presence?.info?.name || "Anonymous";
        result[typing].push(name);
      }
    });
    return result;
  }, [others]);

  const handleFocus = (field: FieldId) => {
    updateMyPresence({ typing: field });
  };

  const handleBlur = (field: FieldId) => {
    updateMyPresence({ typing: null });
  };

  const handleChange = (field: FieldId, value: string) => {
    updateField(field, value);
  };

  return (
    <main>
      <h1>Multiplayer Form</h1>
      <p>Collaborate with other users in real time.</p>

      {FIELDS.map((field) => {
        const label = FIELD_LABELS[field];
        const typingUsers = typingUsersByField[field];
        const isTypingByOther = typingUsers.length > 0;

        return (
          <div key={field} style={{ marginTop: field === "name" ? 24 : 16 }}>
            <label htmlFor={field}>{label}</label>
            {isTypingByOther && (
              <div data-testid={`typing-indicator-${field}`}>
                {typingUsers.join(", ")} is typing in {label}...
              </div>
            )}
            <div style={{ position: "relative" }}>
              {field === "bio" ? (
                <textarea
                  id={field}
                  data-testid={`input-${field}`}
                  value={form?.get("bio") ?? ""}
                  onChange={(e) => handleChange("bio", e.target.value)}
                  onFocus={() => handleFocus("bio")}
                  onBlur={() => handleBlur("bio")}
                  rows={4}
                  style={{ display: "block", width: "100%", padding: 8 }}
                />
              ) : (
                <input
                  id={field}
                  data-testid={`input-${field}`}
                  type={field === "email" ? "email" : "text"}
                  value={form?.get(field) ?? ""}
                  onChange={(e) => handleChange(field, e.target.value)}
                  onFocus={() => handleFocus(field)}
                  onBlur={() => handleBlur(field)}
                  style={{ display: "block", width: "100%", padding: 8 }}
                />
              )}
              {isTypingByOther && (
                <div
                  data-testid={`lock-overlay-${field}`}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: "rgba(200, 200, 200, 0.5)",
                    pointerEvents: "none",
                    borderRadius: 4,
                  }}
                />
              )}
            </div>
          </div>
        );
      })}
    </main>
  );
}