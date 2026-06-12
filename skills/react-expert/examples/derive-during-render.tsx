// Derive during render instead of mirroring props/state into an effect.
// The effect runs after paint, so a stored copy flashes a stale value and
// wastes a render. A total is just a value — compute it.

interface Item {
  id: string
  price: number
}

function Cart({ items }: { items: Item[] }) {
  const total = items.reduce((s, i) => s + i.price, 0)
  return <p>{total}</p>
}

export { Cart }
