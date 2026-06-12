// `using` gives deterministic, LIFO cleanup at scope end — even on throw or
// early return — without manual try/finally. Needs lib ESNext.Disposable.
const log: string[] = [];

function startSpan(name: string): Disposable {
  log.push(`start ${name}`);
  return {
    [Symbol.dispose]() {
      log.push(`end ${name}`);
    },
  };
}

function acquireLock(): AsyncDisposable {
  return {
    async [Symbol.asyncDispose]() {
      log.push("released");
    },
  };
}

export async function work(): Promise<void> {
  using _span = startSpan("work");
  await using _lock = acquireLock();
  // _lock disposed, then _span, when this block exits.
}
