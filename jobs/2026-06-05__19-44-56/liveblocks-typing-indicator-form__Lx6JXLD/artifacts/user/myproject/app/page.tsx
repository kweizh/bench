"use client";

import React, { Suspense, useEffect, useState } from "react";
import { LiveblocksProvider, RoomProvider, useStorage, useMutation, useUpdateMyPresence, useOthers, ClientSideSuspense } from "@liveblocks/react";
import { LiveObject } from "@liveblocks/client";
import { useSearchParams } from "next/navigation";

function FormField({ 
  id, 
  label, 
  type = "text", 
  isTextarea = false, 
  value, 
  onChange,
  onFocus,
  onBlur
}: {
  id: "name" | "email" | "bio";
  label: string;
  type?: string;
  isTextarea?: boolean;
  value: string;
  onChange: (val: string) => void;
  onFocus: () => void;
  onBlur: () => void;
}) {
  const others = useOthers();
  const othersTyping = others.filter((other) => other.presence?.typing === id);
  const isLocked = othersTyping.length > 0;

  return (
    <div style={{ marginTop: 16 }}>
      <label htmlFor={id}>{label}</label>
      
      {isLocked && (
        <div data-testid={`typing-indicator-${id}`} style={{ fontSize: 12, color: "gray", marginBottom: 4 }}>
          {othersTyping.map(o => o.presence?.info?.name || "Anonymous").join(", ")} is typing in {label}...
        </div>
      )}

      <div style={{ position: "relative" }}>
        {isTextarea ? (
          <textarea
            id={id}
            data-testid={`input-${id}`}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={onFocus}
            onBlur={onBlur}
            rows={4}
            style={{ display: "block", width: "100%", padding: 8 }}
          />
        ) : (
          <input
            id={id}
            data-testid={`input-${id}`}
            type={type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={onFocus}
            onBlur={onBlur}
            style={{ display: "block", width: "100%", padding: 8 }}
          />
        )}
        
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
              pointerEvents: "none"
            }}
          />
        )}
      </div>
    </div>
  );
}

function MultiplayerForm() {
  const form = useStorage((root) => root.form);
  
  const updateField = useMutation(({ storage }, field: "name" | "email" | "bio", value: string) => {
    const formObj = storage.get("form");
    if (formObj) {
      formObj.set(field, value);
    }
  }, []);

  const updatePresence = useUpdateMyPresence();

  if (!form) {
    return <div>Loading form...</div>;
  }

  return (
    <main>
      <h1>Multiplayer Form</h1>
      <p>Collaborate with other users in real time.</p>

      <FormField
        id="name"
        label="Name"
        value={form.name}
        onChange={(val) => updateField("name", val)}
        onFocus={() => updatePresence({ typing: "name" })}
        onBlur={() => updatePresence({ typing: null })}
      />

      <FormField
        id="email"
        label="Email"
        type="email"
        value={form.email}
        onChange={(val) => updateField("email", val)}
        onFocus={() => updatePresence({ typing: "email" })}
        onBlur={() => updatePresence({ typing: null })}
      />

      <FormField
        id="bio"
        label="Bio"
        isTextarea
        value={form.bio}
        onChange={(val) => updateField("bio", val)}
        onFocus={() => updatePresence({ typing: "bio" })}
        onBlur={() => updatePresence({ typing: null })}
      />
    </main>
  );
}

function RoomWrapper() {
  const searchParams = useSearchParams();
  const name = searchParams.get("name") || "Anonymous";
  const roomId = process.env.ZEALT_RUN_ID ? `harbor-typing-form-${process.env.ZEALT_RUN_ID}` : "harbor-typing-form-local";

  return (
    <RoomProvider 
      id={roomId} 
      initialPresence={{ typing: null, info: { name } }}
      initialStorage={{ form: new LiveObject({ name: "", email: "", bio: "" }) }}
    >
      <ClientSideSuspense fallback={<div>Loading...</div>}>
        <MultiplayerForm />
      </ClientSideSuspense>
    </RoomProvider>
  );
}

export default function Page() {
  return (
    <LiveblocksProvider authEndpoint="/api/liveblocks-auth">
      <Suspense fallback={<div>Loading app...</div>}>
        <RoomWrapper />
      </Suspense>
    </LiveblocksProvider>
  );
}
