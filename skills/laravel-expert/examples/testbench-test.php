<?php

declare(strict_types=1);

namespace Vendor\Package\Tests;

use Orchestra\Testbench\TestCase;
use Vendor\Package\Contracts\Reporter;
use Vendor\Package\PackageServiceProvider;

/**
 * Testing a *package* (no host app) with Orchestra Testbench. Testbench boots a
 * minimal Laravel app in memory so the container, config, migrations and your
 * service provider all behave as they would in a real install.
 *
 * App developers don't need this — they extend the framework's TestCase and use
 * RefreshDatabase. This file is the package-author path.
 */
final class ReporterTest extends TestCase
{
    /** @return array<int, class-string> */
    protected function getPackageProviders($app): array
    {
        // Register the provider under test, exactly as auto-discovery would.
        return [PackageServiceProvider::class];
    }

    protected function defineEnvironment($app): void
    {
        // Override config for the test app; mirrors a consumer's published config.
        $app['config']->set('package.endpoint', 'https://example.test/ingest');
        $app['config']->set('package.timeout', 5);
    }

    protected function defineDatabaseMigrations(): void
    {
        $this->loadMigrationsFrom(__DIR__ . '/../database/migrations');
    }

    public function test_reporter_is_bound_as_a_singleton(): void
    {
        $a = $this->app->make(Reporter::class);
        $b = $this->app->make(Reporter::class);

        $this->assertInstanceOf(Reporter::class, $a);
        $this->assertSame($a, $b, 'singleton() must return the same instance');
    }

    public function test_config_merges_without_clobbering_user_values(): void
    {
        // The user-set endpoint must survive mergeConfigFrom's defaults.
        $this->assertSame('https://example.test/ingest', config('package.endpoint'));
    }
}
