"use client";

import { useOthers, useUpdateMyPresence } from "@liveblocks/react";
import { useState, useEffect, useRef } from "react";

export default function Canvas() {
  const others = useOthers();
  const updateMyPresence = useUpdateMyPresence();

  const [camera, setCamera] = useState({ x: 0, y: 0 });
  const [following, setFollowing] = useState<string>("");
  const [isDragging, setIsDragging] = useState(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const cameraStart = useRef({ x: 0, y: 0 });

  const [windowSize, setWindowSize] = useState({ width: 1920, height: 1080 });

  // Track window size on the client
  useEffect(() => {
    if (typeof window === "undefined") return;
    setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    const handleResize = () => {
      setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Find the followed user
  const followedUser = others.find((other) => String(other.connectionId) === following);
  const followedCursor = followedUser?.presence?.cursor as { x: number; y: number } | null | undefined;

  // Track the followed user's cursor position
  useEffect(() => {
    if (followedCursor && typeof window !== "undefined") {
      setCamera({
        x: Math.round(followedCursor.x - window.innerWidth / 2),
        y: Math.round(followedCursor.y - window.innerHeight / 2),
      });
    }
  }, [
    followedCursor?.x,
    followedCursor?.y,
    following,
    windowSize,
  ]);

  // Release follow when clicking anywhere else on the document
  useEffect(() => {
    const handleDocumentPointerDown = (e: PointerEvent) => {
      const target = e.target as HTMLElement;
      // If clicking an avatar, do not release follow
      if (target.closest('[data-testid^="avatar-"]')) {
        return;
      }
      setFollowing("");
    };

    window.addEventListener("pointerdown", handleDocumentPointerDown);
    return () => {
      window.removeEventListener("pointerdown", handleDocumentPointerDown);
    };
  }, []);

  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    // If clicking an avatar, do not start dragging
    const target = e.target as HTMLElement;
    if (target.closest('[data-testid^="avatar-"]')) {
      return;
    }

    setIsDragging(true);
    dragStart.current = { x: e.clientX, y: e.clientY };
    cameraStart.current = { ...camera };
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    // Current pointer position in canvas coordinates:
    // canvasX = clientX + camera.x
    // canvasY = clientY + camera.y
    const canvasX = e.clientX + camera.x;
    const canvasY = e.clientY + camera.y;
    updateMyPresence({ cursor: { x: canvasX, y: canvasY } });

    if (isDragging) {
      const dx = e.clientX - dragStart.current.x;
      const dy = e.clientY - dragStart.current.y;
      setCamera({
        x: Math.round(cameraStart.current.x - dx),
        y: Math.round(cameraStart.current.y - dy),
      });
    }
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    if (isDragging) {
      setIsDragging(false);
      e.currentTarget.releasePointerCapture(e.pointerId);
    }
  };

  const handlePointerLeave = () => {
    updateMyPresence({ cursor: null });
  };

  const handleAvatarClick = (e: React.MouseEvent, connectionId: string) => {
    e.stopPropagation();
    if (following === connectionId) {
      setFollowing("");
    } else {
      setFollowing(connectionId);
    }
  };

  // Determine transition style: smoothly transition when following and not dragging
  const transitionStyle = following && !isDragging ? "transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)" : "none";

  return (
    <div
      style={{
        position: "relative",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        backgroundColor: "#f8f9fa",
        userSelect: "none",
      }}
    >
      {/* Translatable Canvas Viewport */}
      <div
        data-testid="canvas-viewport"
        data-camera={JSON.stringify(camera)}
        data-following={following}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerLeave}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "4000px",
          height: "4000px",
          backgroundImage: "radial-gradient(circle, #ccc 1px, transparent 1px)",
          backgroundSize: "20px 20px",
          transform: `translate3d(${-camera.x}px, ${-camera.y}px, 0)`,
          transition: transitionStyle,
          cursor: isDragging ? "grabbing" : "grab",
          touchAction: "none",
        }}
      >
        {/* Visual Cue */}
        <div
          style={{
            position: "absolute",
            top: "100px",
            left: "100px",
            pointerEvents: "none",
            fontFamily: "sans-serif",
          }}
        >
          <h1 style={{ margin: 0, color: "#1e293b", fontSize: "28px" }}>Liveblocks Cursor Follow</h1>
          <p style={{ margin: "8px 0 0 0", color: "#64748b", fontSize: "14px" }}>
            Drag anywhere to pan the canvas. Click other users' avatars to follow their cursors.
          </p>
        </div>

        {/* Render Other Users' Cursors */}
        {others.map((other) => {
          const cursor = other.presence?.cursor as { x: number; y: number } | null | undefined;
          if (!cursor) return null;
          const color = (other.info as any)?.color || "#e11d48";
          return (
            <div
              key={other.connectionId}
              style={{
                position: "absolute",
                left: cursor.x,
                top: cursor.y,
                pointerEvents: "none",
                transform: "translate(-50%, -50%)",
                zIndex: 100,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  backgroundColor: color,
                  border: "2px solid white",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
                }}
              />
              <div
                style={{
                  marginTop: "4px",
                  padding: "2px 6px",
                  backgroundColor: "rgba(15, 23, 42, 0.9)",
                  color: "white",
                  fontSize: "10px",
                  borderRadius: "4px",
                  whiteSpace: "nowrap",
                  fontWeight: "500",
                }}
              >
                {(other.info as any)?.name || `User ${other.connectionId}`}
              </div>
            </div>
          );
        })}
      </div>

      {/* Avatar Bar (Fixed Top-Right Sibling) */}
      <div
        data-testid="avatar-bar"
        style={{
          position: "absolute",
          top: "20px",
          right: "20px",
          display: "flex",
          gap: "8px",
          zIndex: 1000,
          backgroundColor: "rgba(255, 255, 255, 0.9)",
          padding: "8px 12px",
          borderRadius: "24px",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
          border: "1px solid rgba(226, 232, 240, 0.8)",
          alignItems: "center",
        }}
      >
        {others.length === 0 ? (
          <span style={{ fontSize: "12px", color: "#64748b", fontFamily: "sans-serif" }}>No other users</span>
        ) : (
          others.map((other) => {
            const isFollowed = following === String(other.connectionId);
            const color = (other.info as any)?.color || "#e11d48";
            return (
              <button
                key={other.connectionId}
                data-testid={`avatar-${other.connectionId}`}
                onClick={(e) => handleAvatarClick(e, String(other.connectionId))}
                style={{
                  width: "32px",
                  height: "32px",
                  borderRadius: "50%",
                  backgroundColor: color,
                  border: isFollowed ? "3px solid #0f172a" : "2px solid #fff",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#fff",
                  fontWeight: "bold",
                  fontSize: "12px",
                  outline: "none",
                  transition: "all 0.2s ease",
                  transform: isFollowed ? "scale(1.1)" : "scale(1)",
                  padding: 0,
                  fontFamily: "sans-serif",
                }}
                title={`Follow ${(other.info as any)?.name || `User ${other.connectionId}`}`}
              >
                {((other.info as any)?.name || String(other.connectionId)).substring(0, 2).toUpperCase()}
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
