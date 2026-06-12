<?php

declare(strict_types=1);

// PHP has no native generics. Encode them in docblocks with @template so
// PHPStan/Psalm (at level max) check element types — the runtime stays
// untyped but the analyzer treats `pop()` as returning the element type.
// Named arguments make the call site self-documenting without overloads.

/**
 * @template T
 */
final class TypedStack
{
    /** @var list<T> */
    private array $items = [];

    /** @param T $item */
    public function push(mixed $item): void
    {
        $this->items[] = $item;
    }

    /** @return T */
    public function pop(): mixed
    {
        $item = array_pop($this->items);
        if ($item === null && $this->items === []) {
            throw new UnderflowException('stack is empty');
        }

        return $item;
    }

    public function size(): int
    {
        return count($this->items);
    }
}

/**
 * @template TValue
 * @param TValue $default
 * @return TValue
 */
function envOr(string $key, mixed $default): mixed
{
    $raw = getenv($key);

    return $raw === false ? $default : $raw;
}

/** @var TypedStack<string> $stack */
$stack = new TypedStack();
$stack->push('a');
$stack->push('b');

echo $stack->pop(), $stack->pop(), PHP_EOL; // ba

// Named argument documents intent at the call site.
$timeout = envOr(key: 'HTTP_TIMEOUT', default: 30);
echo "timeout={$timeout} size={$stack->size()}", PHP_EOL;
