<?php

declare(strict_types=1);

namespace Vendor\Package;

use Illuminate\Contracts\Foundation\Application;
use Illuminate\Support\ServiceProvider;
use Vendor\Package\Contracts\Reporter;
use Vendor\Package\Reporting\HttpReporter;

/**
 * Package service provider.
 *
 * register(): only bind things into the container. Never resolve other
 * services here — they may not be registered yet.
 *
 * boot(): everything that touches the booted framework — routes, migrations,
 * publishing, view/Blade registration, event listeners.
 *
 * Auto-discovery: declare this class in composer.json under
 *   "extra": { "laravel": { "providers": ["Vendor\\Package\\PackageServiceProvider"] } }
 * so consumers never edit config/app.php. Use "dont-discover" to opt out.
 */
final class PackageServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        // mergeConfigFrom is shallow: it only fills top-level keys the app
        // hasn't already set, so published user config always wins.
        $this->mergeConfigFrom(__DIR__ . '/../config/package.php', 'package');

        // Bind an interface to a concrete. Use a closure so resolution is lazy
        // and config is read at resolve time, not at register time.
        $this->app->singleton(Reporter::class, function (Application $app): Reporter {
            return new HttpReporter(
                endpoint: $app['config']->get('package.endpoint'),
            );
        });

        // Contextual binding: a different implementation for one consumer.
        $this->app->when(HttpReporter::class)
            ->needs('$timeout')
            ->giveConfig('package.timeout');
    }

    public function boot(): void
    {
        // Let the app override config/views/assets via `php artisan vendor:publish`.
        if ($this->app->runningInConsole()) {
            $this->publishes([
                __DIR__ . '/../config/package.php' => $this->app->configPath('package.php'),
            ], 'package-config');
        }

        $this->loadMigrationsFrom(__DIR__ . '/../database/migrations');
        $this->loadRoutesFrom(__DIR__ . '/../routes/package.php');
        $this->loadViewsFrom(__DIR__ . '/../resources/views', 'package');
    }
}

/**
 * Deferred provider: nothing boots until one of provides() is resolved.
 * Only valid when register() does no eager work (no routes, no publishing).
 */
final class DeferredReporterProvider extends ServiceProvider
{
    protected bool $defer = true;

    public function register(): void
    {
        $this->app->singleton(Reporter::class, HttpReporter::class);
    }

    /** @return array<int, class-string> */
    public function provides(): array
    {
        return [Reporter::class];
    }
}
