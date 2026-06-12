<?php

declare(strict_types=1);

// Program to an interface, not an implementation. Depend on the PSR contract
// (here a PSR-3-style logger) so any conforming library — Monolog, a test
// spy, a null sink — drops in without touching call sites.
//
// Real code: `use Psr\Log\LoggerInterface;` from psr/log via Composer.
// This file inlines a minimal compatible interface so it runs standalone.

interface LoggerInterface
{
    /** @param array<string,mixed> $context */
    public function info(string $message, array $context = []): void;
}

final class StdoutLogger implements LoggerInterface
{
    public function info(string $message, array $context = []): void
    {
        $suffix = $context === [] ? '' : ' ' . json_encode($context);
        echo "[info] {$message}{$suffix}", PHP_EOL;
    }
}

// Fire-and-forget analytics: NEVER let a tracking failure break the request.
// Swallow at the edge; do not bubble. The first-class callable `$fn(...)`
// captures the method as a Closure without a wrapper lambda.
final class Analytics
{
    public function __construct(private readonly LoggerInterface $log) {}

    /** @param array<string,mixed> $props */
    public function track(string $event, array $props = []): void
    {
        try {
            $this->log->info("event:{$event}", $props);
        } catch (\Throwable) {
            // Intentionally ignored — analytics must not affect control flow.
        }
    }
}

$analytics = new Analytics(new StdoutLogger());
$emit = $analytics->track(...); // first-class callable syntax (PHP 8.1)

$emit('checkout', ['amount' => 1250, 'currency' => 'EUR']); // named-ish via array
$emit('page_view');
