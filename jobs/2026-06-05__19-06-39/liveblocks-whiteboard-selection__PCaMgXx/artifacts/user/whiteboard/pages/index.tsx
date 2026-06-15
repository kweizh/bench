import { useEffect } from "react";
import { LiveObject } from "@liveblocks/client";
import {
  ClientSideSuspense,
  useMutation,
  useStorage,
  useOthers,
  useUpdateMyPresence,
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

const PALETTE = ["#DC2626", "#2563EB", "#059669", "#F59E0B", "#EC4899"];

function getOtherColor(other: any) {
  if (other.info?.color) {
    return other.info.color;
  }
  if (other.presence?.color) {
    return other.presence.color;
  }
  return PALETTE[other.connectionId % PALETTE.length];
}

function Whiteboard() {
  const shapes = useStorage((root) => root.shapes);
  const others = useOthers();
  const updateMyPresence = useUpdateMyPresence();

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
    if (user === "1") {
      color = "#DC2626";
    } else if (user === "2") {
      color = "#2563EB";
    }
    updateMyPresence({ color });
  }, [updateMyPresence]);

  if (!shapes) {
    return <div>Loading…</div>;
  }

  const handleShapeClick = (e: React.MouseEvent, shapeId: string) => {
    e.stopPropagation();
    updateMyPresence({ selectedShapeId: shapeId });
  };

  const handleCanvasClick = () => {
    updateMyPresence({ selectedShapeId: null });
  };

  return (
    <svg
      viewBox="0 0 800 600"
      width="100%"
      height="100vh"
      style={{ background: "#f8fafc", display: "block" }}
      onClick={handleCanvasClick}
    >
      {shapes.map((shape) => {
        // Find other users who have selected this shape
        const selectors = others.filter(
          (other) => other.presence?.selectedShapeId === shape.id
        );

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
              onClick={(e) => handleShapeClick(e, shape.id)}
              style={{ cursor: "pointer" }}
            />
            {selectors.map((other) => {
              const color = getOtherColor(other);
              return (
                <rect
                  key={other.connectionId}
                  data-testid="selection-ring"
                  data-selection-shape-id={shape.id}
                  data-selection-connection-id={other.connectionId}
                  data-selection-color={color}
                  x={shape.x - 4}
                  y={shape.y - 4}
                  width={shape.width + 8}
                  height={shape.height + 8}
                  fill="none"
                  stroke={color}
                  strokeWidth={3}
                  style={{ pointerEvents: "none" }}
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
