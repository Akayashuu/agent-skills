<?php

declare(strict_types=1);

namespace Acme\PaymentBundle\Service;

use Psr\Log\LoggerInterface;
use Symfony\Component\DependencyInjection\Attribute\Autowire;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\RequestStack;

/**
 * Why inject RequestStack and never the Request:
 * services are instantiated once and shared, but the Request is created
 * per HTTP request and does not exist at all in CLI/messenger/sub-request
 * contexts. Injecting Request would freeze a stale (or missing) object.
 * RequestStack is the stable handle; you ask it for the *current* request
 * each time, and handle the null (no active request) case.
 */
final class RequestContext
{
    public function __construct(
        private readonly RequestStack $requestStack,
        private readonly LoggerInterface $logger,
        // Bind a scalar/env arg at the autowiring point — no services.yaml
        // entry needed. The container resolves %env()% lazily.
        #[Autowire('%env(string:APP_LOCALE)%')]
        private readonly string $defaultLocale = 'en',
    ) {
    }

    public function clientIp(): ?string
    {
        return $this->current()?->getClientIp();
    }

    public function locale(): string
    {
        return $this->current()?->getLocale() ?? $this->defaultLocale;
    }

    private function current(): ?Request
    {
        $request = $this->requestStack->getCurrentRequest();
        if (null === $request) {
            // Running off-request (CLI/worker) — caller must tolerate this.
            $this->logger->debug('RequestContext used with no active request.');
        }

        return $request;
    }
}
