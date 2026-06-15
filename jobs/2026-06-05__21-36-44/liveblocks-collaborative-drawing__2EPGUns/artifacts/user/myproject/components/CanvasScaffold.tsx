"use client";

import React, { useCallback, useRef, useState } from "react";
import { LiveList, LiveObject } from "@liveblocks/client";
import { useStorage, useMutation } from "@/lib/liveblocks";
import { nanoid } from "nanoid";

type Tool = "pen" | "eraser";

/**
 * Full collaborative drawing canvas backed by Liveblocks.
 *
 * - Pen tool: pointerdown starts a new stroke, pointermove appends points
 *   (throttled to ~30 ms), pointerup finalises.
 * - Eraser tool: clicking a polyline deletes that stroke from the LiveList.
 * - Undo button: removes the most recent stroke whose userId matches the
 *   current user (other users' strokes are untouched).
 */
export function CanvasScaffold({ userId }: { userId: string }) {
  const [tool, setTool] = useState<Tool>("pen");
  const [color, setColor] = useState<string>("#000000");
  const [width, setWidth] = useState<number>(4);

  // Track which stroke id is currently being drawn
  const activeStrokeId = useRef<string | null>(null);
  // Throttle timestamp for pointermove
  const lastMoveTime = useRef<number>(0);

  // Read all strokes from shared storage
  const strokes = useStorage((root) => root.strokes);

  // ── Mutations ─────────────────────────────────────────────────────────────

  /** Start a new stroke on pointerdown */
  const startStroke = useMutation(
    ({ storage }, x: number, y: number, id: string) => {
      const strokesList = storage.get("strokes");
      const pointsList = new LiveList([
        new LiveObject({ x, y }),
      ]);
      const stroke = new LiveObject({
        id,
        userId,
        color,
        width,
        points: pointsList,
      });
      strokesList.push(stroke);
    },
    [userId, color, width]
  );

  /** Append a point to the active stroke */
  const addPoint = useMutation(
    ({ storage }, id: string, x: number, y: number) => {
      const strokesList = storage.get("strokes");
      for (let i = 0; i < strokesList.length; i++) {
        const s = strokesList.get(i);
        if (s && s.get("id") === id) {
          s.get("points").push(new LiveObject({ x, y }));
          break;
        }
      }
    },
    []
  );

  /** Delete a stroke by id (eraser) */
  const deleteStroke = useMutation(({ storage }, id: string) => {
    const strokesList = storage.get("strokes");
    for (let i = 0; i < strokesList.length; i++) {
      const s = strokesList.get(i);
      if (s && s.get("id") === id) {
        strokesList.delete(i);
        break;
      }
    }
  }, []);

  /** Undo the current user's most recent stroke */
  const undoMine = useMutation(
    ({ storage }) => {
      const strokesList = storage.get("strokes");
      // Walk backwards to find the last stroke owned by this user
      for (let i = strokesList.length - 1; i >= 0; i--) {
        const s = strokesList.get(i);
        if (s && s.get("userId") === userId) {
          strokesList.delete(i);
          break;
        }
      }
    },
    [userId]
  );

  // ── Pointer handlers ──────────────────────────────────────────────────────

  const getSVGCoords = (e: React.PointerEvent<SVGSVGElement>) => {
    const svg = e.currentTarget as SVGSVGElement;
    const rect = svg.getBoundingClientRect();
    // Map from client coordinates to SVG viewBox coordinates
    const vb = svg.viewBox.baseVal;
    const scaleX = vb.width / rect.width;
    const scaleY = vb.height / rect.height;
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  };

  const handlePointerDown = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      if (tool !== "pen") return;
      e.currentTarget.setPointerCapture(e.pointerId);
      const { x, y } = getSVGCoords(e);
      const id = nanoid();
      activeStrokeId.current = id;
      lastMoveTime.current = Date.now();
      startStroke(x, y, id);
    },
    [tool, startStroke]
  );

  const handlePointerMove = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      if (tool !== "pen" || !activeStrokeId.current) return;
      const now = Date.now();
      if (now - lastMoveTime.current < 30) return; // ~30 ms throttle
      lastMoveTime.current = now;
      const { x, y } = getSVGCoords(e);
      addPoint(activeStrokeId.current, x, y);
    },
    [tool, addPoint]
  );

  const handlePointerUp = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      if (tool !== "pen") return;
      activeStrokeId.current = null;
    },
    [tool]
  );

  /** Handle eraser clicks on a polyline */
  const handlePolylineClick = useCallback(
    (e: React.MouseEvent<SVGPolylineElement>, strokeId: string) => {
      if (tool !== "eraser") return;
      e.stopPropagation();
      deleteStroke(strokeId);
    },
    [tool, deleteStroke]
  );

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div style={{ padding: 16 }}>
      <h1>Collaborative Drawing</h1>
      <p>
        User: <strong data-testid="current-user">{userId}</strong>
      </p>
      <div
        style={{ display: "flex", gap: 8, marginBottom: 12, alignItems: "center" }}
      >
        <label>
          Color
          <input
            data-testid="color-picker"
            type="text"
            value={color}
            onChange={(e) => setColor(e.target.value)}
            style={{ marginLeft: 4, width: 96 }}
          />
        </label>
        <label>
          Width
          <input
            data-testid="width-picker"
            type="number"
            min={1}
            max={32}
            value={width}
            onChange={(e) => setWidth(Number(e.target.value))}
            style={{ marginLeft: 4, width: 64 }}
          />
        </label>
        <button
          data-testid="tool-pen"
          onClick={() => setTool("pen")}
          aria-pressed={tool === "pen"}
          style={{ fontWeight: tool === "pen" ? "bold" : "normal" }}
        >
          Pen
        </button>
        <button
          data-testid="tool-eraser"
          onClick={() => setTool("eraser")}
          aria-pressed={tool === "eraser"}
          style={{ fontWeight: tool === "eraser" ? "bold" : "normal" }}
        >
          Eraser
        </button>
        <button data-testid="undo-mine" onClick={() => undoMine()}>
          Undo my last stroke
        </button>
      </div>

      <svg
        data-testid="canvas"
        width={1024}
        height={720}
        viewBox="0 0 1024 720"
        style={{
          background: "#fafafa",
          border: "1px solid #ddd",
          cursor: tool === "eraser" ? "crosshair" : "default",
          touchAction: "none",
        }}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
      >
        {strokes &&
          strokes.map((stroke) => {
            const id = stroke.id;
            const uid = stroke.userId;
            const pts = stroke.points;
            if (!pts || pts.length === 0) return null;

            // Build the SVG points string: "x1,y1 x2,y2 ..."
            const pointsStr = pts
              .map((p) => `${p.x},${p.y}`)
              .join(" ");

            return (
              <polyline
                key={id}
                data-stroke-id={id}
                data-user-id={uid}
                points={pointsStr}
                stroke={stroke.color}
                strokeWidth={stroke.width}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{
                  cursor: tool === "eraser" ? "pointer" : "default",
                  pointerEvents: tool === "eraser" ? "stroke" : "none",
                }}
                onClick={(e) => handlePolylineClick(e, id)}
              />
            );
          })}
      </svg>
    </div>
  );
}
