// Effects are for external systems and must clean up to dodge races. An ignore
// flag drops stale resolutions; AbortController cancels the in-flight request.
// Prefer TanStack Query / SWR / an RSC loader in a real app — this is the
// fallback, not the goal.

import { useEffect, useState } from 'react'

interface User {
  id: string
  name: string
}

function useUser(id: string): User | null {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    let active = true
    const controller = new AbortController()

    fetch(`/api/u/${id}`, { signal: controller.signal })
      .then((r) => r.json() as Promise<User>)
      .then((u) => {
        if (active) setUser(u)
      })
      .catch((err: unknown) => {
        if (active && (err as Error).name !== 'AbortError') throw err
      })

    return () => {
      active = false
      controller.abort()
    }
  }, [id])

  return user
}

export { useUser }
