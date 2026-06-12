<?php

declare(strict_types=1);

// Result/Either via a union return type. Use this for *expected* failures
// (parse, validate, lookup) that the caller must handle — not for bugs.
// Reserve exceptions for the exceptional. `match` then forces both arms.

/**
 * @template T
 */
final class Ok
{
    /** @param T $value */
    public function __construct(public readonly mixed $value) {}
}

final class Err
{
    public function __construct(public readonly string $message) {}
}

/**
 * @return Ok<int>|Err
 */
function parsePositiveInt(string $raw): Ok|Err
{
    if (!ctype_digit($raw)) {
        return new Err("not an integer: {$raw}");
    }
    $n = (int) $raw;

    return $n > 0 ? new Ok($n) : new Err('must be positive');
}

foreach (['42', 'abc', '0'] as $input) {
    $result = parsePositiveInt($input);
    $shown = match (true) {
        $result instanceof Ok  => "ok({$result->value})",
        $result instanceof Err => "err({$result->message})",
    };
    echo str_pad($input, 5), ' -> ', $shown, PHP_EOL;
}
