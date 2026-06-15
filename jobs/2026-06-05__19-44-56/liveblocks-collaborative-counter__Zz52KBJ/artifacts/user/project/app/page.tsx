import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Liveblocks Collaborative Counter</h1>
      <p>
        Open <Link href="/dashboard/demo">/dashboard/demo</Link> in two
        browser windows to collaborate.
      </p>
    </main>
  );
}
