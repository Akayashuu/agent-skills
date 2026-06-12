// Discriminated union: each variant carries exactly its own data, so illegal
// combinations (e.g. loading AND data present) cannot be constructed.
interface User {
  id: string;
  name: string;
}

export type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "success"; data: User[] };

export function render(state: State): string {
  switch (state.status) {
    case "loading":
      return "…";
    case "error":
      return state.message;
    case "success":
      return `${state.data.length} users`;
  }
}
