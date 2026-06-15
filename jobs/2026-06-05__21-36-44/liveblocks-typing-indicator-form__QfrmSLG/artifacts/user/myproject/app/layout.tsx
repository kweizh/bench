import React from "react";

export const metadata = { title: "Multiplayer Form" };

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "sans-serif", maxWidth: 640, margin: "40px auto" }}>
        {children}
      </body>
    </html>
  );
}
