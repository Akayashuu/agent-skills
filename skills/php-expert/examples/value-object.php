<?php

declare(strict_types=1);

// Immutable value object: readonly + constructor promotion (PHP 8.1).
// Validate in the constructor so an invalid instance can never exist.
// NOTE: `public readonly` promoted props work in 8.1; the class-level
// `readonly class Money` form is 8.2+. Per-property is the portable choice.

enum Currency: string
{
    case EUR = 'EUR';
    case USD = 'USD';

    public function symbol(): string
    {
        return match ($this) {
            self::EUR => '€',
            self::USD => '$',
        };
    }
}

final class Money implements Stringable
{
    public function __construct(
        public readonly int $amountMinor, // cents — never floats for money
        public readonly Currency $currency,
    ) {
        if ($amountMinor < 0) {
            throw new InvalidArgumentException('amount must be non-negative');
        }
    }

    // "Mutation" returns a new instance; the original is never touched.
    public function add(self $other): self
    {
        if ($this->currency !== $other->currency) {
            throw new InvalidArgumentException('currency mismatch');
        }

        return new self($this->amountMinor + $other->amountMinor, $this->currency);
    }

    public function __toString(): string
    {
        return sprintf('%s%.2f', $this->currency->symbol(), $this->amountMinor / 100);
    }
}

$lunch = new Money(1250, Currency::EUR);
$coffee = new Money(350, Currency::EUR);

echo $lunch->add($coffee), PHP_EOL; // €16.00

try {
    $lunch->amountMinor = 0; // readonly: fatal Error, caught here
} catch (Error $e) {
    echo 'blocked: ', $e->getMessage(), PHP_EOL;
}
