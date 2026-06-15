'use client'

import { useState, useRef } from 'react'
import {
  KnockProvider,
  KnockFeedProvider,
  NotificationIconButton,
  NotificationFeedPopover,
} from '@knocklabs/react'
import '@knocklabs/react/dist/index.css'

const KNOCK_PUBLIC_API_KEY = process.env.NEXT_PUBLIC_KNOCK_PUBLIC_API_KEY!
const KNOCK_FEED_CHANNEL_ID = process.env.NEXT_PUBLIC_KNOCK_FEED_CHANNEL_ID!
const ZEALT_RUN_ID = process.env.NEXT_PUBLIC_ZEALT_RUN_ID!

export default function Home() {
  const [isVisible, setIsVisible] = useState(false)
  const buttonRef = useRef<HTMLButtonElement>(null)

  const userId = `popover-user-${ZEALT_RUN_ID}`

  return (
    <KnockProvider apiKey={KNOCK_PUBLIC_API_KEY} userId={userId}>
      <KnockFeedProvider feedId={KNOCK_FEED_CHANNEL_ID}>
        <div style={{ padding: '20px' }}>
          <h1>Knock Popover Demo</h1>
          <p>Run ID: {ZEALT_RUN_ID}</p>
          <p>User ID: {userId}</p>

          <NotificationIconButton
            ref={buttonRef}
            onClick={() => setIsVisible(!isVisible)}
          />

          <NotificationFeedPopover
            buttonRef={buttonRef}
            isVisible={isVisible}
            onClose={() => setIsVisible(false)}
          />
        </div>
      </KnockFeedProvider>
    </KnockProvider>
  )
}