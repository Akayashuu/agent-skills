// Reusable SolidJS primitives demonstrating idioms.
// Verified against Solid 1.9.x APIs (createSignal, createEffect, on, onCleanup).
// A "primitive" is just a function calling Solid primitives — composition is the whole point.

import { createSignal, createEffect, on, onCleanup, type Signal } from "solid-js";
import { isServer } from "solid-js/web";

/**
 * createPersistedSignal — a signal mirrored to localStorage.
 *
 * WHY a primitive and not inline code: the reactive read/write, the storage
 * sync effect, and the cross-tab listener all share one lifecycle. Wrapping
 * them means callers get a plain Signal<T> and onCleanup runs automatically
 * when the owning component is disposed — no leaked listeners.
 *
 * SSR-safe: on the server there is no localStorage, so we skip persistence and
 * just return a normal signal seeded with the fallback (avoids hydration crash).
 */
export function createPersistedSignal<T>(
  key: string,
  fallback: T,
  // serializer is injectable so non-JSON values (Date, Map…) still work
  serde: { parse: (s: string) => T; stringify: (v: T) => string } = JSON,
): Signal<T> {
  if (isServer) return createSignal(fallback);

  const read = (): T => {
    const raw = localStorage.getItem(key);
    if (raw === null) return fallback;
    try {
      return serde.parse(raw);
    } catch {
      // Corrupt/legacy value — don't blow up the app, fall back gracefully.
      return fallback;
    }
  };

  const [value, setValue] = createSignal<T>(read());

  // on(value, …, { defer: true }): write to storage only when value CHANGES,
  // not on the initial run — otherwise we'd re-write what we just read.
  createEffect(
    on(
      value,
      (v) => localStorage.setItem(key, serde.stringify(v)),
      { defer: true },
    ),
  );

  // Keep tabs in sync. The "storage" event fires only in OTHER tabs.
  const onStorage = (e: StorageEvent) => {
    if (e.key === key) setValue(() => (e.newValue === null ? fallback : serde.parse(e.newValue)));
  };
  window.addEventListener("storage", onStorage);
  onCleanup(() => window.removeEventListener("storage", onStorage)); // no leak

  return [value, setValue];
}

/**
 * createEventListener — declarative, auto-cleaned event binding.
 *
 * WHY: addEventListener in a component body would leak across the component's
 * life because nothing removes it. onCleanup ties removal to the reactive
 * owner, so the listener disappears exactly when the component is disposed.
 *
 * `target` may be a getter so the listener can follow a changing element
 * (e.g. a ref that arrives after mount); the effect re-binds on change.
 */
export function createEventListener<K extends keyof WindowEventMap>(
  target: EventTarget | (() => EventTarget | undefined),
  type: K,
  handler: (e: WindowEventMap[K]) => void,
  options?: AddEventListenerOptions,
): void {
  createEffect(() => {
    const el = typeof target === "function" ? target() : target;
    if (!el) return;
    el.addEventListener(type, handler as EventListener, options);
    // onCleanup inside an effect runs before each re-run AND on disposal,
    // so a changing target detaches the old binding before attaching the new.
    onCleanup(() => el.removeEventListener(type, handler as EventListener, options));
  });
}
