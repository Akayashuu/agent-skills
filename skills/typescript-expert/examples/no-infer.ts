// NoInfer pins the generic from the first argument only: the second argument is
// checked against E but cannot widen it.
function on<E extends string>(events: E[], initial: NoInfer<E>): E {
  return initial;
}

export const picked = on(["a", "b"], "a"); // ok: 'a' is a member
// on(["a", "b"], "c") // ❌ 'c' is not assignable to 'a' | 'b'
