"use client";

import React, { useState, useCallback, useRef } from "react";
import { useStorage, useMutation, useSelf, Stroke, StrokePoint } from "@/lib/liveblocks";
import { LiveList, LiveObject } from "@liveblocks/client";
import { nanoid } from "nanoid";

type Tool = "pen" | "eraser";

export function CanvasScaffold({ userId }: { userId: string }) {
  const [tool, setTool] = useState<Tool>("pen");
  const [color, setColor] = useState<string>("#000000");
  const [width, setWidth] = useState<number>(4);

  const strokes = useStorage((root) => root.strokes);
  const self = useSelf();
  
  const activeStrokeId = useRef<string | null>(null);
  const lastUpdate = useRef<number>(0);

  const startDrawing = useMutation(({ storage }, x: number, y: number) => {
    const id = nanoid();
    activeStrokeId.current = id;
    const newStroke: Stroke = new LiveObject({
      id,
      userId,
      color,
      width,
      points: new LiveList([new LiveObject({ x, y })]),
    });
    storage.get("strokes").push(newStroke);
  }, [userId, color, width]);

  const updateDrawing = useMutation(({ storage }, x: number, y: number) => {
    const now = Date.now();
    if (now - lastUpdate.current < 30) return;
    lastUpdate.current = now;

    const strokes = storage.get("strokes");
    const strokeIndex = strokes.findIndex(s => s.get("id") === activeStrokeId.current);
    if (strokeIndex !== -1) {
      strokes.get(strokeIndex).get("points").push(new LiveObject({ x, y }));
    }
  }, []);

  const stopDrawing = useCallback(() => {
    activeStrokeId.current = null;
  }, []);

  const eraseStroke = useMutation(({ storage }, strokeId: string) => {
    const strokes = storage.get("strokes");
    const index = strokes.findIndex((s) => s.get("id") === strokeId);
    if (index !== -1) {
      strokes.delete(index);
    }
  }, []);

  const undoLastStroke = useMutation(({ storage }) => {
    const strokes = storage.get("strokes");
    for (let i = strokes.length - 1; i >= 0; i--) {
      if (strokes.get(i).get("userId") === userId) {
        strokes.delete(i);
        break;
      }
    }
  }, [userId]);

  const onPointerDown = (e: React.PointerEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (tool === "pen") {
      startDrawing(x, y);
    }
  };

  const onPointerMove = (e: React.PointerEvent) => {
    if (activeStrokeId.current && tool === "pen") {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      updateDrawing(x, y);
    }
  };

  const onPointerUp = () => {
    stopDrawing();
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
          style={{ backgroundColor: tool === "pen" ? "#eee" : "transparent" }}
        >
          Pen
        </button>
        <button
          data-testid="tool-eraser"
          onClick={() => setTool("eraser")}
          style={{ backgroundColor: tool === "eraser" ? "#eee" : "transparent" }}
        >
          Eraser
        </button>
        <button data-testid="undo-mine" onClick={() => undoLastStroke()}>
          Undo my last stroke
        </button>
      </div>
      <svg
        data-testid="canvas"
        width={1024}
        height={720}
        viewBox="0 0 1024 720"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
        style={{ background: "#fafafa", border: "1px solid #ddd", touchAction: "none" }}
      >
        {strokes?.map((stroke) => {
          const id = stroke.id;
          const strokeUserId = stroke.userId;
          const points = stroke.points.map((p) => `${p.x},${p.y}`).join(" ");
          return (
            <polyline
              key={id}
              data-stroke-id={id}
              data-user-id={strokeUserId}
              points={points}
              fill="none"
              stroke={stroke.color}
              strokeWidth={stroke.width}
              strokeLinecap="round"
              strokeLinejoin="round"
              onClick={() => {
                if (tool === "eraser") {
                  eraseStroke(id);
                }
              }}
              style={{ cursor: tool === "eraser" ? "pointer" : "crosshair" }}
            />
          );
        })}
      </svg>
    </div>
  );
}
