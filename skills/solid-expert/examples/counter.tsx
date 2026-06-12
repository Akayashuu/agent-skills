import { createSignal, createMemo } from "solid-js";

// Read signals inside a tracking scope (JSX or a memo) so updates reach the DOM.
export default function Counter() {
  const [count, setCount] = createSignal(0);
  const doubled = createMemo(() => count() * 2);
  return <p onClick={() => setCount(count() + 1)}>{doubled()}</p>;
}
