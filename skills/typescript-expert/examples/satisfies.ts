// `satisfies` validates against a type without widening: the literal types of
// each property are preserved for downstream inference.
const config = {
  port: 3000,
  host: "localhost",
} satisfies Record<string, string | number>;

// `port` is still `number`, not `string | number`.
export const doubled: number = config.port * 2;
export const host: string = config.host;
