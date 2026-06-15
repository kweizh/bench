import { useEffect } from "react";
import { LiveObject } from "@liveblocks/client";
import {
  ClientSideSuspense,
  useMutation,
  useOthers,
  useMyPresence,
  useStorage,
} from "@liveblocks/react";
import "../liveblocks.config";

type SeedShape = {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
};

const SEED_SHAPES: SeedShape[] = [
  { id: "shape-a", x: 80, y: 80, width: 140, height: 90, fill: "#FCD34D" },
  { id: "shape-b", x: 320, y: 200, width: 140, height: 140, fill: "#A78BFA" },
  { id: "shape-c", x: 560, y: 360, width: 160, height: 100, fill: "#34D399" },
];

const PALETTE = [
  "#DC2626",
  "#2563EB",
  "#059669",
  "#D97706",
  "#7C3AED",
  "#DB2777",
  "#0891B2",
  "#4338CA",
];

function getColorForConnectionId(connectionId: number): string {
  return PALETTE[connectionId % PALETTE.length];
}

function Whiteboard() {
  const shapes = useStorage((root) => root.shapes);
  const others = useOthers();
  const [myPresence, updateMyPresence] = useMyPresence();

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

  if (!shapes) {
    return <div>Loading…</div>;
  }

  const handleShapeClick = (shapeId: string) => {
    updateMyPresence({ selectedShapeId: shapeId });
  };

  const handleCanvasClick = () => {
    updateMyPresence({ selectedShapeId: null });
  };

  const handleRectClick = (e: React.MouseEvent<SVGRectElement>, shapeId: string) => {
    e.stopPropagation();
    handleShapeClick(shapeId);
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
        // Find other users who have this shape selected
        const otherSelections = others.filter(
          (other) => other.presence?.selectedShapeId === shape.id
        );

        return (
          <g key={shape.id}>
            {/* Render selection rings for other users */}
            {otherSelections.map((other) => {
              const strokeColor: string =
                other.presence?.color ||
                (other.info?.color as string) ||
                getColorForConnectionId(other.connectionId);
              return (
                <rect
                  key={`selection-${other.connectionId}`}
                  data-testid="selection-ring"
                  data-selection-shape-id={shape.id}
                  data-selection-connection-id={other.connectionId}
                  data-selection-color={strokeColor}
                  x={shape.x - 4}
                  y={shape.y - 4}
                  width={shape.width + 8}
                  height={shape.height + 8}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={3}
                  rx={4}
                  pointerEvents="none"
                />
              );
            })}
            {/* The shape itself */}
            <rect
              data-testid="shape"
              data-shape-id={shape.id}
              x={shape.x}
              y={shape.y}
              width={shape.width}
              height={shape.height}
              fill={shape.fill}
              onClick={(e) => handleRectClick(e, shape.id)}
              style={{ cursor: "pointer" }}
            />
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