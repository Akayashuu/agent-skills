import { createStore, produce } from "solid-js/store";

// createStore for nested objects: only the touched paths update.
export function nestedStore() {
  const [state, setState] = createStore({ user: { name: "Ada", tags: ["a"] } });
  setState("user", "name", "Grace"); // path setter, surgical
  setState("user", "tags", produce((t) => t.push("b"))); // mutate-style via produce
  return state;
}
