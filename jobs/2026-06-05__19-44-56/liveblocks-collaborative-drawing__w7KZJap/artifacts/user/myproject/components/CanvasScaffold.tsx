"use client";

import React, { useState, useRef } from "react";
import { useMutation, useStorage } from "@/lib/liveblocks";
import { LiveObject, LiveList } from "@liveblocks/client";

type Tool = "pen" | "eraser";

/**
 * Placeholder scaffold. It renders the toolbar and an empty SVG canvas with
 * the required data-testid attributes, but DOES NOT implement stroke creation,
 * eraser deletion, or undo logic. The executor must add these behaviours.
 */
export function CanvasScaffold({ userId }: { userId: string }) {
  const [tool, setTool] = useState<Tool>("pen");
  const [color, setColor] = useState<string>("#000000");
  const [width, setWidth] = useState<number>(4);

  const strokes = useStorage((root) => root.strokes);
  const [activeStrokeId, setActiveStrokeId] = useState<string | null>(null);
  const lastMoveTimeRef = useRef<number>(0);

  const startStroke = useMutation(({ storage }, x: number, y: number) => {
    const id = crypto.randomUUID();
    const newStroke = new LiveObject({
      id,
      userId,
      color,
      width,
      points: new LiveList([new LiveObject({ x, y })]),
    });
    
    storage.get("strokes").push(newStroke);
    setActiveStrokeId(id);
  }, [userId, color, width]);

  const addPointToStroke = useMutation(({ storage }, x: number, y: number) => {
    if (!activeStrokeId) return;
    
    const strokesList = storage.get("strokes");
    const strokesArray = strokesList.toArray();
    const strokeIndex = strokesArray.findIndex((s) => s.get("id") === activeStrokeId);
    if (strokeIndex !== -1) {
      const stroke = strokesList.get(strokeIndex);
      if (stroke) {
        stroke.get("points").push(new LiveObject({ x, y }));
      }
    }
  }, [activeStrokeId]);

  const endStroke = () => {
    setActiveStrokeId(null);
  };

  const eraseStroke = useMutation(({ storage }, strokeId: string) => {
    const strokesList = storage.get("strokes");
    const strokesArray = strokesList.toArray();
    const strokeIndex = strokesArray.findIndex((s) => s.get("id") === strokeId);
    if (strokeIndex !== -1) {
      strokesList.delete(strokeIndex);
    }
  }, []);

  const undoMyLastStroke = useMutation(({ storage }) => {
    const strokesList = storage.get("strokes");
    const strokesArray = strokesList.toArray();
    for (let i = strokesArray.length - 1; i >= 0; i--) {
      const stroke = strokesArray[i];
      if (stroke && stroke.get("userId") === userId) {
        strokesList.delete(i);
        break;
      }
    }
  }, [userId]);

  const handlePointerDown = (e: React.PointerEvent<SVGSVGElement>) => {
    if (tool !== "pen") return;
    e.currentTarget.setPointerCapture(e.pointerId);
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    startStroke(x, y);
    lastMoveTimeRef.current = Date.now();
  };

  const handlePointerMove = (e: React.PointerEvent<SVGSVGElement>) => {
    if (tool !== "pen" || !activeStrokeId) return;
    const now = Date.now();
    if (now - lastMoveTimeRef.current < 30) {
      return; // throttle
    }
    lastMoveTimeRef.current = now;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    addPointToStroke(x, y);
  };

  const handlePointerUp = (e: React.PointerEvent<SVGSVGElement>) => {
    if (tool !== "pen") return;
    e.currentTarget.releasePointerCapture(e.pointerId);
    endStroke();
  };

  return (
    <div style={{ padding: 16 }}>
      <h1>Collaborative Drawing</h1>
      <p>
        User: <strong data-testid="current-user">{userId}</strong>
      </p>
      <div style={{ display: "flex", gap: 8, marginBottom: 12, alignItems: "center" }}>
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
        >
          Pen
        </button>
        <button
          data-testid="tool-eraser"
          onClick={() => setTool("eraser")}
          aria-pressed={tool === "eraser"}
        >
          Eraser
        </button>
        <button data-testid="undo-mine" onClick={undoMyLastStroke}>Undo my last stroke</button>
      </div>
      <svg
        data-testid="canvas"
        width={1024}
        height={720}
        viewBox="0 0 1024 720"
        style={{ background: "#fafafa", border: "1px solid #ddd", touchAction: "none" }}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
      >
        {strokes?.map((stroke) => {
          const pointsString = stroke.points
            .map((p) => `${p.x},${p.y}`)
            .join(" ");
          return (
            <polyline
              key={stroke.id}
              data-stroke-id={stroke.id}
              data-user-id={stroke.userId}
              points={pointsString}
              stroke={stroke.color}
              strokeWidth={stroke.width}
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              onPointerDown={(e) => {
                if (tool === "eraser") {
                  e.stopPropagation();
                  eraseStroke(stroke.id);
                }
              }}
              style={{ cursor: tool === "eraser" ? "crosshair" : "default" }}
            />
          );
        })}
      </svg>
    </div>
  );
}
