// effect-cleanup.svelte.ts — $effect for external systems, with teardown.
//
// $effect is for side effects that reach outside Svelte (sockets, timers, subscriptions),
// NOT for deriving values. Always return a cleanup function: it runs before each re-run
// (when a tracked dep changes) and on teardown, so listeners/timers don't leak.
// These are plain functions so the module compiles via compileModule; in a real component
// the body would live directly inside <script>.

type Msg = { id: string; body: string };

// Re-subscribes whenever the reactive `roomId` getter changes; closes the old socket first.
export function subscribeRoom(getRoomId: () => string, messages: Msg[]) {
  $effect(() => {
    const id = getRoomId(); // tracked read -> effect re-runs when it changes
    const timer = setInterval(() => {
      messages.push({ id: `${id}-${Date.now()}`, body: 'tick' });
    }, 1000);
    return () => clearInterval(timer); // cleanup before re-run / on unmount
  });
}

// $effect.pre runs BEFORE the DOM updates — the rare case where you must read layout
// (e.g. capture scroll position) ahead of a render.
export function autoscrollOnAppend(getCount: () => number, el: () => HTMLElement | null) {
  $effect.pre(() => {
    getCount(); // depend on the list length
    const node = el();
    if (!node) return;
    const atBottom = node.scrollTop + node.clientHeight >= node.scrollHeight - 1;
    if (atBottom) queueMicrotask(() => (node.scrollTop = node.scrollHeight));
  });
}
