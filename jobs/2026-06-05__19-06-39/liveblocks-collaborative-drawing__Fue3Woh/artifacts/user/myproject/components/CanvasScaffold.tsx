"use client";

import React, { useState, useRef } from "react";
import { LiveList, LiveObject } from "@liveblocks/client";
import { useStorage, useMutation } from "@/lib/liveblocks";

type Tool = "pen" | "eraser";

const generateId = () => {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).substring(2, 9);
};

const getStrokeId = (stroke: any): string => {
  return typeof stroke.get === "function" ? stroke.get("id") : stroke.id;
};

const getStrokeUserId = (stroke: any): string => {
  return typeof stroke.get === "function" ? stroke.get("userId") : stroke.userId;
};

const getStrokeColor = (stroke: any): string => {
  return typeof stroke.get === "function" ? stroke.get("color") : stroke.color;
};

const getStrokeWidth = (stroke: any): number => {
  return typeof stroke.get === "function" ? stroke.get("width") : stroke.width;
};

const getStrokePoints = (stroke: any): any[] => {
  const pts = typeof stroke.get === "function" ? stroke.get("points") : stroke.points;
  if (!pts) return [];
  if (typeof pts.toArray === "function") return pts.toArray();
  return Array.from(pts);
};

const getPointCoords = (point: any): { x: number; y: number } => {
  if (typeof point.get === "function") {
    return { x: point.get("x"), y: point.get("y") };
  }
  return { x: point.x, y: point.y };
};

const getPointsString = (stroke: any): string => {
  const points = getStrokePoints(stroke);
  return points
    .map((p) => {
      const coords = getPointCoords(p);
      return `${coords.x},${coords.y}`;
    })
    .join(" ");
};

export function CanvasScaffold({ userId }: { userId: string }) {
  const [tool, setTool] = useState<Tool>("pen");
  const [color, setColor] = useState<string>("#000000");
  const [width, setWidth] = useState<number>(4);
  const [activeStrokeId, setActiveStrokeId] = useState<string | null>(null);

  const lastAppendTimeRef = useRef<number>(0);

  const strokes = useStorage((root) => root.strokes);

  const insertStroke = useMutation(({ storage }, { id, userId, color, width, x, y }) => {
    const strokesList = storage.get("strokes");
    const pointsList = new LiveList<LiveObject<{ x: number; y: number }>>([
      new LiveObject({ x, y })
    ]);
    const newStroke = new LiveObject({
      id,
      userId,
      color,
      width,
      points: pointsList,
    });
    strokesList.push(newStroke);
  }, []);

  const appendPoint = useMutation(({ storage }, { strokeId, x, y }) => {
    const strokesList = storage.get("strokes");
    for (let i = 0; i < strokesList.length; i++) {
      const stroke = strokesList.get(i);
      if (stroke && stroke.get("id") === strokeId) {
        stroke.get("points").push(new LiveObject({ x, y }));
        break;
      }
    }
  }, []);

  const deleteStroke = useMutation(({ storage }, strokeId: string) => {
    const strokesList = storage.get("strokes");
    for (let i = 0; i < strokesList.length; i++) {
      const stroke = strokesList.get(i);
      if (stroke && stroke.get("id") === strokeId) {
        strokesList.delete(i);
        break;
      }
    }
  }, []);

  const undoLastStroke = useMutation(({ storage }, currentUserId: string) => {
    const strokesList = storage.get("strokes");
    for (let i = strokesList.length - 1; i >= 0; i--) {
      const stroke = strokesList.get(i);
      if (stroke && stroke.get("userId") === currentUserId) {
        strokesList.delete(i);
        break;
      }
    }
  }, []);

  const getCoordinates = (e: React.PointerEvent<SVGSVGElement>) => {
    const svg = e.currentTarget;
    const rect = svg.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (1024 / rect.width);
    const y = (e.clientY - rect.top) * (720 / rect.height);
    return { x: Math.round(x), y: Math.round(y) };
  };

  const handlePointerDown = (e: React.PointerEvent<SVGSVGElement>) => {
    if (tool !== "pen") return;
    const { x, y } = getCoordinates(e);
    const strokeId = generateId();
    insertStroke({ id: strokeId, userId, color, width, x, y });
    setActiveStrokeId(strokeId);
    lastAppendTimeRef.current = Date.now();
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!activeStrokeId || tool !== "pen") return;
    const now = Date.now();
    if (now - lastAppendTimeRef.current >= 30) {
      const { x, y } = getCoordinates(e);
      appendPoint({ strokeId: activeStrokeId, x, y });
      lastAppendTimeRef.current = now;
    }
  };

  const handlePointerUp = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!activeStrokeId) return;
    const { x, y } = getCoordinates(e);
    appendPoint({ strokeId: activeStrokeId, x, y });
    setActiveStrokeId(null);
    try {
      e.currentTarget.releasePointerCapture(e.pointerId);
    } catch (err) {
      // ignore if already released or invalid
    }
  };

  const handlePointerCancel = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!activeStrokeId) return;
    setActiveStrokeId(null);
    try {
      e.currentTarget.releasePointerCapture(e.pointerId);
    } catch (err) {
      // ignore
    }
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
          style={{
            backgroundColor: tool === "pen" ? "#ddd" : "#fff",
            fontWeight: tool === "pen" ? "bold" : "normal",
            padding: "4px 8px",
            cursor: "pointer",
          }}
        >
          Pen
        </button>
        <button
          data-testid="tool-eraser"
          onClick={() => setTool("eraser")}
          aria-pressed={tool === "eraser"}
          style={{
            backgroundColor: tool === "eraser" ? "#ddd" : "#fff",
            fontWeight: tool === "eraser" ? "bold" : "normal",
            padding: "4px 8px",
            cursor: "pointer",
          }}
        >
          Eraser
        </button>
        <button
          data-testid="undo-mine"
          onClick={() => undoLastStroke(userId)}
          style={{ padding: "4px 8px", cursor: "pointer" }}
        >
          Undo my last stroke
        </button>
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
        onPointerCancel={handlePointerCancel}
      >
        {strokes &&
          Array.from(strokes).map((stroke, index) => {
            const strokeId = getStrokeId(stroke);
            const strokeUserId = getStrokeUserId(stroke);
            const strokeColor = getStrokeColor(stroke);
            const strokeWidth = getStrokeWidth(stroke);
            const pointsString = getPointsString(stroke);

            return (
              <polyline
                key={strokeId || index}
                data-stroke-id={strokeId}
                data-user-id={strokeUserId}
                points={pointsString}
                stroke={strokeColor}
                strokeWidth={strokeWidth}
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
                onClick={(e) => {
                  if (tool === "eraser") {
                    e.stopPropagation();
                    deleteStroke(strokeId);
                  }
                }}
                style={{ cursor: tool === "eraser" ? "pointer" : "inherit" }}
              />
            );
          })}
      </svg>
    </div>
  );
}
