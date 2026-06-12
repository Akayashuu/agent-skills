import { ref, watch, onWatcherCleanup, type Ref } from 'vue'

interface User {
  id: number
  name: string
}

declare function fetchUser(id: number, signal: AbortSignal): Promise<User>

// `watch` is for side effects. When the source changes before the previous
// effect settled, cancel the stale work. `onWatcherCleanup` (3.5+) registers
// teardown that runs on the next invocation and on unmount — but it must be
// called synchronously, BEFORE the first `await`, or it won't be tracked.
export function useUser(id: Ref<number>) {
  const data = ref<User | null>(null)

  watch(
    id,
    async (newId) => {
      const ctrl = new AbortController()
      onWatcherCleanup(() => ctrl.abort())
      data.value = await fetchUser(newId, ctrl.signal)
    },
    { immediate: true },
  )

  return { data }
}
