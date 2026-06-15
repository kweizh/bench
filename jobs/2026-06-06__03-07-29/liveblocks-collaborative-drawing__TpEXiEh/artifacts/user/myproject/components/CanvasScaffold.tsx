"use client";

import React, { useState } from "react";

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
        <button data-testid="undo-mine">Undo my last stroke</button>
      </div>
      <svg
        data-testid="canvas"
        width={1024}
        height={720}
        viewBox="0 0 1024 720"
        style={{ background: "#fafafa", border: "1px solid #ddd" }}
      >
        {/* TODO(executor): render <polyline data-stroke-id data-user-id ... /> for each stroke. */}
      </svg>
    </div>
  );
}
