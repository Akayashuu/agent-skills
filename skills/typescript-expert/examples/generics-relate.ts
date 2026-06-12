// A useful type parameter appears in 2+ positions to relate input and output,
// and is constrained with `extends` so the body can use the shape.
function pluck<T extends object, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { id: "u1", age: 30 };
export const id: string = pluck(user, "id"); // T[K] inferred as string
export const age: number = pluck(user, "age"); // inferred as number
