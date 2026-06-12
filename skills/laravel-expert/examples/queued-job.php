<?php

declare(strict_types=1);

namespace App\Jobs;

use App\Models\Order;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\DB;
use Throwable;

/**
 * A well-behaved queued job.
 *
 * ShouldQueue   => pushed onto the queue instead of running inline.
 * ShouldBeUnique => Laravel won't enqueue a duplicate while one is pending.
 *
 * Queues retry, so handle() MUST be idempotent: a job that runs twice must
 * have the same effect as running once. Guard side effects with a state check
 * inside a transaction, not just "did we send it" booleans set after the fact.
 */
final class ChargeOrder implements ShouldQueue, ShouldBeUnique
{
    use Dispatchable;
    use InteractsWithQueue;
    use Queueable;
    use SerializesModels;

    public int $tries = 5;
    public int $backoff = 30;          // seconds; pass an array for incremental backoff
    public int $timeout = 60;

    // SerializesModels stores only the id and re-fetches on unserialize, so the
    // job always sees fresh DB state — never a stale snapshot from dispatch time.
    public function __construct(public readonly Order $order)
    {
    }

    public function uniqueId(): string
    {
        return (string) $this->order->id;
    }

    public function handle(): void
    {
        // Idempotency: claim the row atomically. If another attempt already
        // charged it, this update affects 0 rows and we bail without re-charging.
        $claimed = DB::transaction(function (): bool {
            $fresh = Order::query()->whereKey($this->order->id)->lockForUpdate()->first();

            if ($fresh === null || $fresh->status !== 'pending') {
                return false;
            }

            $fresh->update(['status' => 'charging']);

            return true;
        });

        if (! $claimed) {
            return;
        }

        // ... call the payment gateway, then mark 'paid' ...
    }

    /** @return array<int, object> */
    public function middleware(): array
    {
        // e.g. new WithoutOverlapping($this->order->id) for extra safety.
        return [];
    }

    public function failed(Throwable $e): void
    {
        // Runs after the final attempt. Compensate / notify here; the record
        // is also written to the failed_jobs table for `queue:retry`.
        $this->order->update(['status' => 'charge_failed']);
    }
}
