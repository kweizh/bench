import { Room } from "./_components/Room";
import Canvas from "./_components/Canvas";

export default function Page() {
  const runId = process.env.ZEALT_RUN_ID || "local";
  const roomId = `cursor-follow-${runId}`;
  return (
    <Room roomId={roomId}>
      <Canvas />
    </Room>
  );
}
