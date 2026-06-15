import { useEffect } from "react";
import { LiveObject } from "@liveblocks/client";
import {
  ClientSideSuspense,
  useMutation,
  useStorage,
  useOthers,
  useMyPresence,
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
  const others = useOthers();
  const [{ selectedShapeId }, setMyPresence] = useMyPresence();

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

  return (
    <svg
      viewBox="0 0 800 600"
      width="100%"
      height="100vh"
      style={{ background: "#f8fafc", display: "block" }}
      onClick={() => setMyPresence({ selectedShapeId: null })}
    >
      {shapes.map((shape) => {
        const shapeOthers = others.filter(
          (other) => other.presence.selectedShapeId === shape.id
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
              onClick={(e) => {
                e.stopPropagation();
                setMyPresence({ selectedShapeId: shape.id });
              }}
              style={{ cursor: "pointer" }}
            />
            {shapeOthers.map((other) => (
              <rect
                key={other.connectionId}
                data-testid="selection-ring"
                data-selection-shape-id={shape.id}
                data-selection-connection-id={other.connectionId}
                data-selection-color={other.presence.color}
                x={shape.x - 4}
                y={shape.y - 4}
                width={shape.width + 8}
                height={shape.height + 8}
                fill="none"
                stroke={other.presence.color}
                strokeWidth={2}
                pointerEvents="none"
              />
            ))}
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
