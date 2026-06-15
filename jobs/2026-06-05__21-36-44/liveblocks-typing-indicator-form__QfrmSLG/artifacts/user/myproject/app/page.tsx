import React from "react";
import { Room } from "./components/Room";
import { MultiplayerForm } from "./components/MultiplayerForm";

export default function Page() {
  return (
    <Room>
      <MultiplayerForm />
    </Room>
  );
}
