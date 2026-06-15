import React from "react";
import { LiveblocksProviderWrapper } from "./providers";

export const metadata = { title: "Multiplayer Form" };

const ROOM_ID = `harbor-typing-form-${process.env.ZEALT_RUN_ID || "local"}`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "sans-serif", maxWidth: 640, margin: "40px auto" }}>
        <LiveblocksProviderWrapper roomId={ROOM_ID}>
          {children}
        </LiveblocksProviderWrapper>
      </body>
    </html>
  );
}