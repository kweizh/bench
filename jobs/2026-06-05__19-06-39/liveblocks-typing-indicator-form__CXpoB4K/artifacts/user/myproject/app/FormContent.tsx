"use client";

import React, { useEffect } from "react";
import { useStorage, useMutation, useUpdateMyPresence, useOthers } from "@liveblocks/react";
import { useSearchParams } from "next/navigation";

export default function FormContent() {
  const name = useStorage((root: any) => root.form?.name) ?? "";
  const email = useStorage((root: any) => root.form?.email) ?? "";
  const bio = useStorage((root: any) => root.form?.bio) ?? "";

  const updateMyPresence = useUpdateMyPresence();
  const others = useOthers();
  const searchParams = useSearchParams();
  const nameParam = searchParams.get("name") || "Anonymous";

  // Keep the presence info/user name updated if query params change
  useEffect(() => {
    updateMyPresence({
      info: { name: nameParam },
      user: { name: nameParam },
    });
  }, [nameParam, updateMyPresence]);

  const updateField = useMutation(({ storage }, field: "name" | "email" | "bio", value: string) => {
    const form = storage.get("form") as any;
    if (form) {
      form.set(field, value);
    }
  }, []);

  const handleFocus = (field: "name" | "email" | "bio") => {
    updateMyPresence({ typing: field });
  };

  const handleBlur = () => {
    updateMyPresence({ typing: null });
  };

  const handleChange = (field: "name" | "email" | "bio", value: string) => {
    updateField(field, value);
    updateMyPresence({ typing: field });
  };

  const getOthersTyping = (field: "name" | "email" | "bio") => {
    return others.filter((other) => other.presence?.typing === field);
  };

  const getUserName = (other: any) => {
    return (
      other.presence?.info?.name ||
      other.presence?.user?.name ||
      other.info?.name ||
      "Anonymous"
    );
  };

  const renderTypingIndicator = (field: "name" | "email" | "bio", label: string) => {
    const typingUsers = getOthersTyping(field);
    if (typingUsers.length === 0) return null;

    const names = typingUsers.map(getUserName).join(", ");
    return (
      <div
        data-testid={`typing-indicator-${field}`}
        style={{
          color: "#dc2626",
          fontSize: "0.85rem",
          fontWeight: "500",
          marginBottom: 4,
        }}
      >
        {names} is typing in {label}...
      </div>
    );
  };

  return (
    <main style={{ padding: "20px", border: "1px solid #ccc", borderRadius: "8px", background: "#fff" }}>
      <h1 style={{ marginTop: 0 }}>Multiplayer Form</h1>
      <p style={{ color: "#666" }}>Collaborate with other users in real time.</p>

      {/* Name Field */}
      <div style={{ marginTop: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <label htmlFor="name" style={{ fontWeight: "600" }}>Name</label>
          {renderTypingIndicator("name", "Name")}
        </div>
        <div style={{ position: "relative", marginTop: 4 }}>
          <input
            id="name"
            data-testid="input-name"
            type="text"
            value={name}
            onChange={(e) => handleChange("name", e.target.value)}
            onFocus={() => handleFocus("name")}
            onBlur={handleBlur}
            style={{ display: "block", width: "100%", padding: 8, boxSizing: "border-box" }}
          />
          {getOthersTyping("name").length > 0 && (
            <div
              data-testid="lock-overlay-name"
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: "rgba(220, 220, 220, 0.4)",
                pointerEvents: "none",
                border: "1px solid rgba(0, 0, 0, 0.1)",
                borderRadius: 4,
              }}
            />
          )}
        </div>
      </div>

      {/* Email Field */}
      <div style={{ marginTop: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <label htmlFor="email" style={{ fontWeight: "600" }}>Email</label>
          {renderTypingIndicator("email", "Email")}
        </div>
        <div style={{ position: "relative", marginTop: 4 }}>
          <input
            id="email"
            data-testid="input-email"
            type="email"
            value={email}
            onChange={(e) => handleChange("email", e.target.value)}
            onFocus={() => handleFocus("email")}
            onBlur={handleBlur}
            style={{ display: "block", width: "100%", padding: 8, boxSizing: "border-box" }}
          />
          {getOthersTyping("email").length > 0 && (
            <div
              data-testid="lock-overlay-email"
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: "rgba(220, 220, 220, 0.4)",
                pointerEvents: "none",
                border: "1px solid rgba(0, 0, 0, 0.1)",
                borderRadius: 4,
              }}
            />
          )}
        </div>
      </div>

      {/* Bio Field */}
      <div style={{ marginTop: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <label htmlFor="bio" style={{ fontWeight: "600" }}>Bio</label>
          {renderTypingIndicator("bio", "Bio")}
        </div>
        <div style={{ position: "relative", marginTop: 4 }}>
          <textarea
            id="bio"
            data-testid="input-bio"
            value={bio}
            onChange={(e) => handleChange("bio", e.target.value)}
            onFocus={() => handleFocus("bio")}
            onBlur={handleBlur}
            rows={4}
            style={{ display: "block", width: "100%", padding: 8, boxSizing: "border-box", fontFamily: "sans-serif" }}
          />
          {getOthersTyping("bio").length > 0 && (
            <div
              data-testid="lock-overlay-bio"
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: "rgba(220, 220, 220, 0.4)",
                pointerEvents: "none",
                border: "1px solid rgba(0, 0, 0, 0.1)",
                borderRadius: 4,
              }}
            />
          )}
        </div>
      </div>
    </main>
  );
}
