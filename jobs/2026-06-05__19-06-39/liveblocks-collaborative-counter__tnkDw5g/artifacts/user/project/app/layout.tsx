import React from "react";

export const metadata = {
  title: "Liveblocks Collaborative Counter",
  description: "Multi-counter dashboard built on Liveblocks Storage"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
