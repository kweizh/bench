import React, { Suspense } from "react";
import FormClient from "./FormClient";

export default function Page() {
  const runId = process.env.ZEALT_RUN_ID || "local";
  const roomId = `harbor-typing-form-${runId}`;

  return (
    <Suspense fallback={<div>Loading form...</div>}>
      <FormClient roomId={roomId} />
    </Suspense>
  );
}
