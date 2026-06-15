import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Knock Popover Demo',
  description: 'Knock Notification Feed Popover Demo',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}