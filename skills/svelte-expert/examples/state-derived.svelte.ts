// state-derived.svelte.ts — compute with $derived, never with $effect.
//
// A $state factory plus $derived values. `$derived` recomputes lazily and stays
// fresh; using an $effect to mirror state into another variable would add an extra
// pass and risk stale reads. Exposed via getters so reads stay reactive for callers.

type Item = { id: string; price: number };

export function createCart(initial: Item[] = []) {
  let items = $state(initial);

  const total = $derived(items.reduce((n, i) => n + i.price, 0));
  const count = $derived(items.length);
  const summary = $derived.by(() => `${count} item(s), ${total.toFixed(2)}`);

  return {
    get items() {
      return items;
    },
    get total() {
      return total;
    },
    get count() {
      return count;
    },
    get summary() {
      return summary;
    },
    add(item: Item) {
      items.push(item); // deep proxy: mutate in place, don't reassign the array
    },
    clear() {
      items = [];
    },
  };
}
