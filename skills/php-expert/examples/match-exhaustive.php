<?php

declare(strict_types=1);

// `match` over `switch`: strict (===) comparison, no fall-through, it is an
// expression (returns a value), and an unhandled case throws
// UnhandledMatchError instead of silently doing nothing.
// Paired with a pure enum, PHPStan flags a missing arm at analysis time.

enum HttpMethod
{
    case Get;
    case Post;
    case Put;
    case Delete;
}

function isIdempotent(HttpMethod $method): bool
{
    return match ($method) {
        HttpMethod::Get, HttpMethod::Put, HttpMethod::Delete => true,
        HttpMethod::Post => false,
    };
}

// `never` documents a function that always exits — improves flow analysis.
function fail(string $why): never
{
    throw new RuntimeException($why);
}

foreach (HttpMethod::cases() as $m) {
    printf("%-7s idempotent=%s%s", $m->name, isIdempotent($m) ? 'yes' : 'no', PHP_EOL);
}

// No default arm: an unmapped value is a loud error, never a silent skip.
$code = 418;
try {
    echo match ($code) {
        200 => 'ok',
        404 => 'not found',
    }, PHP_EOL;
    fail('unreachable'); // demonstrates the `never` return type
} catch (\UnhandledMatchError) {
    echo "no mapping for status {$code} — handled, not skipped", PHP_EOL;
}
