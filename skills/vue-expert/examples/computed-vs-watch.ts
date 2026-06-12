import { ref, computed } from 'vue'

interface Item {
  name: string
  price: number
}

// Derived state belongs in `computed`, not a `watch` that writes another ref.
// computed is cached, lazy, and always consistent — no extra ref to keep in
// sync, no flush-timing window where source and mirror disagree.
export function useCart() {
  const items = ref<Item[]>([])

  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.price, 0),
  )

  function add(item: Item) {
    items.value.push(item)
  }

  return { items, total, add }
}
