// Reusable React patterns. Verified against react.dev for the React 19 era.
// These compile under TS strict + @types/react 19. Trim to taste.

import {
  useState,
  useEffect,
  useEffectEvent, // stable since React 19.2
} from 'react'

// ---------------------------------------------------------------------------
// (a) Abortable fetch inside an effect, done correctly.
//
// WHY both an ignore flag AND AbortController:
//  - AbortController cancels the in-flight request (saves bandwidth, fires a
//    catchable AbortError) — but a response can still be mid-resolution when
//    deps change, so the `ignore` flag guards against a stale `setState`.
//  - Without this, a slow earlier request can resolve last and clobber newer
//    data (a race / out-of-order write).
//
// PREFER a data library (TanStack Query, SWR) or a Server Component / RSC
// loader in a real app: they handle caching, dedup, retries, and races for
// you. Hand-rolled effect fetching is the fallback, not the goal.
// ---------------------------------------------------------------------------
interface User {
  id: string
  name: string
}

function useUser(id: string): User | null {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    let ignore = false
    const controller = new AbortController()

    fetch(`/api/users/${id}`, { signal: controller.signal })
      .then((r) => r.json() as Promise<User>)
      .then((data) => {
        if (!ignore) setUser(data) // drop stale resolutions
      })
      .catch((err: unknown) => {
        // Aborts are expected on cleanup — ignore them, surface real errors.
        if (!ignore && (err as Error).name !== 'AbortError') throw err
      })

    return () => {
      ignore = true
      controller.abort()
    }
  }, [id]) // re-fetch only when the id actually changes

  return user
}

// ---------------------------------------------------------------------------
// (b) Derive state during render instead of an effect.
//
// WHY: `fullName` and `filtered` are pure functions of existing state. Mirroring
// them into useState + useEffect adds an extra render, briefly shows a stale
// frame, and invites desync. Just compute during render. Reach for useMemo only
// if profiling proves the work is expensive (and the React Compiler may make
// even that unnecessary).
// ---------------------------------------------------------------------------
interface Todo {
  id: string
  text: string
  done: boolean
}

function TodoList({ todos }: { todos: Todo[] }) {
  const [query, setQuery] = useState('')

  // derived — no state, no effect
  const filtered = todos.filter((t) => t.text.includes(query))
  const remaining = todos.filter((t) => !t.done).length

  return (
    <section>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <p>{remaining} remaining</p>
      <ul>
        {filtered.map((t) => (
          <li key={t.id}>{t.text}</li> // stable id key, never the index
        ))}
      </ul>
    </section>
  )
}

// ---------------------------------------------------------------------------
// (c) Correct useEffectEvent usage.
//
// WHY: the effect should re-synchronize (reconnect) only when `roomId` changes,
// but the connect handler needs the *latest* `theme`. Putting `theme` in the
// deps array would reconnect on every theme toggle; omitting it would read a
// stale theme. useEffectEvent splits the non-reactive part out: it always sees
// fresh props/state and must NOT appear in the dependency array.
// ---------------------------------------------------------------------------
declare function createConnection(roomId: string): {
  on(event: 'connected', cb: () => void): void
  connect(): void
  disconnect(): void
}
declare function showNotification(message: string, theme: string): void

function ChatRoom({ roomId, theme }: { roomId: string; theme: string }) {
  const onConnected = useEffectEvent(() => {
    showNotification('Connected!', theme) // reads latest theme, non-reactively
  })

  useEffect(() => {
    const connection = createConnection(roomId)
    connection.on('connected', () => onConnected())
    connection.connect()
    return () => connection.disconnect()
  }, [roomId]) // onConnected intentionally excluded — it is an Effect Event

  return null
}

export { useUser, TodoList, ChatRoom }
