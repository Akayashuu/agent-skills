// derived-not-effect.svelte.ts — prefer $derived; break effect loops with untrack.
//
// An $effect that reads AND writes the same $state loops forever. The fix is almost
// always $derived. When you genuinely must write state from inside an effect, read the
// looping dependency through `untrack` so it isn't registered as a tracked dependency.

import { untrack } from 'svelte';

// ✅ The right tool: a computed value, no effect, no loop.
export function createFilter() {
  let query = $state('');
  let all = $state<string[]>([]);
  const matches = $derived(all.filter((s) => s.includes(query)));

  return {
    get matches() {
      return matches;
    },
    set query(q: string) {
      query = q;
    },
    set all(xs: string[]) {
      all = xs;
    },
  };
}

// Escape hatch: must write state in an effect (e.g. logging a count elsewhere).
// Read the trigger normally; read the value you also WRITE via untrack to avoid re-running.
export function syncWithUntrack(getTrigger: () => number) {
  let writes = $state(0);
  $effect(() => {
    getTrigger(); // tracked: this is what should re-run the effect
    untrack(() => {
      writes += 1; // writing `writes` here would self-loop if it were tracked
    });
  });
  return {
    get writes() {
      return writes;
    },
  };
}
