import { useEffect } from "react";
import { LiveObject } from "@liveblocks/client";
import {
  ClientSideSuspense,
  useMutation,
  useStorage,
  useMyPresence,
  useOthers,
} from "@liveblocks/react";

type SeedShape = {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
};

const SEED_SHAPES: SeedShape[] = [
  { id: "shape-a", x: 80,  y: 80,  width: 140, height: 90,  fill: "#FCD34D" },
  { id: "shape-b", x: 320, y: 200, width: 140, height: 140, fill: "#A78BFA" },
  { id: "shape-c", x: 560, y: 360, width: 160, height: 100, fill: "#34D399" },
];

function Whiteboard() {
  const shapes = useStorage((root) => root.shapes);
  const [{ selectedShapeId }, setMyPresence] = useMyPresence();
  const others = useOthers();

  const seedShapes = useMutation(({ storage }) => {
    const list = storage.get("shapes");
    if (list.length === 0) {
      for (const s of SEED_SHAPES) {
        list.push(new LiveObject(s));
      }
    }
  }, []);

  useEffect(() => {
    if (shapes && shapes.length === 0) {
      seedShapes();
    }
  }, [shapes, seedShapes]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const user = params.get("user");
    let color = "#059669";
    if (user === "1") color = "#DC2626";
    else if (user === "2") color = "#2563EB";
    setMyPresence({ color });
  }, [setMyPresence]);

  if (!shapes) {
    return <div>Loading…</div>;
  }

  return (
    <svg
      viewBox="0 0 800 600"
      width="100%"
      height="100vh"
      style={{ background: "#f8fafc", display: "block" }}
      onPointerDown={(e) => {
        // If they click the background (svg itself), clear selection
        if (e.target === e.currentTarget) {
          setMyPresence({ selectedShapeId: null });
        }
      }}
    >
      {shapes.map((shape) => {
        // Find other users who have selected this shape
        const selectors = others.filter((other) => other.presence.selectedShapeId === shape.id);

        return (
          <g key={shape.id}>
            <rect
              data-testid="shape"
              data-shape-id={shape.id}
              x={shape.x}
              y={shape.y}
              width={shape.width}
              height={shape.height}
              fill={shape.fill}
              onPointerDown={(e) => {
                e.stopPropagation();
                setMyPresence({ selectedShapeId: shape.id });
              }}
            />
            {selectors.map((selector, index) => {
              // Calculate offset for stacked rings
              const offset = (index + 1) * 4;
              const color = (selector.presence.color as string) || (selector.info?.color as string) || "#059669";
              return (
                <rect
                  key={selector.connectionId}
                  data-testid="selection-ring"
                  data-selection-shape-id={shape.id}
                  data-selection-connection-id={selector.connectionId}
                  data-selection-color={color}
                  x={shape.x - offset}
                  y={shape.y - offset}
                  width={shape.width + offset * 2}
                  height={shape.height + offset * 2}
                  fill="none"
                  stroke={color}
                  strokeWidth={2}
                  pointerEvents="none"
                />
              );
            })}
          </g>
        );
      })}
    </svg>
  );
}

export default function Page() {
  return (
    <ClientSideSuspense fallback={<div>Loading…</div>}>
      {() => <Whiteboard />}
    </ClientSideSuspense>
  );
}
