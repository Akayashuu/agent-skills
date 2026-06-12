// Tiny copy-paste utilities. Zero deps. Compiles under the strict baseline.

/**
 * Exhaustiveness guard. Put it in a switch `default` (or an else branch):
 * the parameter type is `never`, so if a new union member appears, the call
 * stops compiling — turning "forgot a case" from a runtime bug into a type error.
 */
export function assertNever(value: never, message = "Unexpected value"): never {
  throw new Error(`${message}: ${JSON.stringify(value)}`);
}

/**
 * Branded (nominal) types. TS is structural, so `UserId` and `OrderId` are both
 * just `string` and freely interchangeable — a real source of bugs. A brand adds
 * a phantom tag that exists only at compile time (zero runtime cost) so the two
 * can't be mixed up. The maker is the single intentional cast.
 *
 *   type UserId = Brand<string, "UserId">;
 *   const UserId = makeBrand<string, "UserId">();
 *   const id = UserId("u_123");   // UserId
 *   takesUserId("u_123");         // ❌ raw string rejected
 */
declare const __brand: unique symbol;
export type Brand<T, B extends string> = T & { readonly [__brand]: B };

export function makeBrand<T, B extends string>() {
  // The cast is the whole point: validate `raw` here if you want a smart constructor.
  return (raw: T): Brand<T, B> => raw as Brand<T, B>;
}

/**
 * Result<T, E> — explicit success/failure without throwing. Forces callers to
 * handle the error path (the union won't narrow until they check `.ok`), and
 * keeps error types in the signature instead of invisible `throw`s.
 *
 *   function parse(s: string): Result<number, "NaN"> {
 *     const n = Number(s);
 *     return Number.isNaN(n) ? err("NaN") : ok(n);
 *   }
 *   const r = parse(input);
 *   if (r.ok) use(r.value); else handle(r.error);
 */
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const err = <E>(error: E): Result<never, E> => ({ ok: false, error });
