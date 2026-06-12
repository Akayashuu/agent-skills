// Exhaustive switch with assertNever: adding a new variant turns "forgot a
// case" into a compile error at the default branch.
import { assertNever } from "../types.js";

interface User {
  id: string;
}

type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "success"; data: User[] };

export function describe(state: State): string {
  switch (state.status) {
    case "loading":
      return "loading";
    case "error":
      return state.message;
    case "success":
      return `${state.data.length} users`;
    default:
      return assertNever(state);
  }
}
