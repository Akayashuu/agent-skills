// Separate non-reactive logic with useEffectEvent (stable since React 19.2).
// The effect re-synchronizes only on `roomId`, but the connect handler needs
// the latest `theme`. An Effect Event sees fresh props/state and must stay out
// of the deps array — so a theme toggle does not reconnect.

import { useEffect, useEffectEvent } from 'react'

declare function createConnection(roomId: string): {
  on(event: 'connected', cb: () => void): void
  connect(): void
  disconnect(): void
}
declare function log(message: string, theme: string): void

function ChatRoom({ roomId, theme }: { roomId: string; theme: string }) {
  const onConnected = useEffectEvent(() => log('connected', theme))

  useEffect(() => {
    const conn = createConnection(roomId)
    conn.on('connected', () => onConnected())
    conn.connect()
    return () => conn.disconnect()
  }, [roomId])

  return null
}

export { ChatRoom }
