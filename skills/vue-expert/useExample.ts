import {
  onScopeDispose,
  toValue,
  watch,
  type MaybeRefOrGetter,
} from 'vue'

/**
 * useEventListener — attach a DOM listener that tracks a reactive target and
 * cleans itself up. A small but genuinely reusable composable that shows the
 * idioms you want in every composable you write.
 *
 * WHY these choices:
 * - `MaybeRefOrGetter<T>` for the target: callers pass a raw element, a `ref`,
 *   a `useTemplateRef`, or a `() => el` getter — all work. This is the standard
 *   composable input shape (same contract `watch`/`computed` accept).
 * - `toValue()` normalizes that union to a plain value inside the watcher, so
 *   the getter is re-read whenever its dependencies change (e.g. a template ref
 *   resolving after mount, or the user swapping `window` for an element).
 * - `watch(..., { immediate: true })` (re)binds on every target change and runs
 *   the returned cleanup first, so we never double-bind or leak the old target.
 * - `onScopeDispose` ties teardown to the owning effect scope — works in
 *   `setup()` AND inside another composable or a detached `effectScope()`,
 *   unlike `onUnmounted` which only fires for component instances.
 * - Generic over `EventTarget` + event name so `event` is typed (e.g. a
 *   `'click'` handler receives a `MouseEvent`, not a bare `Event`).
 */
export function useEventListener<
  T extends EventTarget,
  K extends keyof (T extends Window
    ? WindowEventMap
    : T extends Document
      ? DocumentEventMap
      : HTMLElementEventMap),
>(
  target: MaybeRefOrGetter<T | null | undefined>,
  event: K,
  handler: (
    this: T,
    ev: (T extends Window
      ? WindowEventMap
      : T extends Document
        ? DocumentEventMap
        : HTMLElementEventMap)[K],
  ) => void,
  options?: AddEventListenerOptions,
): () => void {
  const stopWatch = watch(
    () => toValue(target),
    (el, _prev, onCleanup) => {
      if (!el) return
      el.addEventListener(event as string, handler as EventListener, options)
      // Runs before the next watch invocation and on scope teardown.
      onCleanup(() =>
        el.removeEventListener(event as string, handler as EventListener, options),
      )
    },
    { immediate: true },
  )

  // Manual stop handle for callers who unbind early; also fires automatically
  // when the surrounding component/scope is disposed.
  const stop = () => stopWatch()
  onScopeDispose(stop)
  return stop
}

/* Usage:
 *   const el = useTemplateRef<HTMLButtonElement>('btn')
 *   useEventListener(el, 'click', (e) => console.log(e.offsetX))
 *   useEventListener(window, 'resize', () => { ... })
 */
