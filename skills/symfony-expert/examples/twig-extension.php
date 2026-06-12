<?php

declare(strict_types=1);

namespace Acme\PaymentBundle\Twig;

use Acme\PaymentBundle\Service\PriceFormatter;
use Twig\Extension\AbstractExtension;
use Twig\TwigFilter;
use Twig\TwigFunction;

/**
 * A Twig extension exposing a filter and a function. Autoconfiguration
 * tags this automatically (it implements ExtensionInterface), so no
 * manual service tag is needed when autoconfigure is on.
 *
 * The html-safety judgment call: a callable that returns markup MUST be
 * declared is_safe => ['html'] so Twig does NOT double-escape it. But
 * that makes YOU responsible for escaping any interpolated user input —
 * is_safe on a function that injects unescaped input is an XSS hole.
 */
final class PriceExtension extends AbstractExtension
{
    public function __construct(private readonly PriceFormatter $formatter)
    {
    }

    public function getFilters(): array
    {
        return [
            // Plain filter — Twig still auto-escapes the returned string.
            new TwigFilter('price', $this->formatPrice(...)),
        ];
    }

    public function getFunctions(): array
    {
        return [
            // Returns a <span> — declared html-safe, so we escape inside.
            new TwigFunction(
                'price_badge',
                $this->priceBadge(...),
                ['is_safe' => ['html']],
            ),
        ];
    }

    public function formatPrice(int $cents, string $currency = 'EUR'): string
    {
        return $this->formatter->format($cents, $currency);
    }

    public function priceBadge(int $cents, string $currency = 'EUR'): string
    {
        // $currency is escaped because we promised html-safe output.
        $label = htmlspecialchars(
            $this->formatter->format($cents, $currency),
            \ENT_QUOTES | \ENT_SUBSTITUTE,
            'UTF-8',
        );

        return \sprintf('<span class="price-badge">%s</span>', $label);
    }
}
