<?php

declare(strict_types=1);

namespace Acme\PaymentBundle\EventListener;

use Symfony\Component\EventDispatcher\Attribute\AsEventListener;
use Symfony\Component\HttpKernel\Event\ResponseEvent;
use Symfony\Component\HttpKernel\KernelEvents;

/**
 * #[AsEventListener] declares the subscription inline, so autoconfiguration
 * registers it — no kernel.event_listener tag in services.yaml. Prefer this
 * over EventSubscriberInterface for a single hook; use a subscriber when one
 * class handles several events and you want them listed in one getSubscribedEvents.
 *
 * priority: higher runs earlier. Listen to a kernel event by its constant,
 * not the string, so a typo is a fatal error rather than a silent no-op.
 */
#[AsEventListener(event: KernelEvents::RESPONSE, priority: -10)]
final class SecurityHeadersListener
{
    public function __construct(private readonly bool $hsts = true)
    {
    }

    public function __invoke(ResponseEvent $event): void
    {
        // Only decorate the main request, not sub-requests (ESI/fragments).
        if (!$event->isMainRequest()) {
            return;
        }

        $headers = $event->getResponse()->headers;
        $headers->set('X-Content-Type-Options', 'nosniff');
        $headers->set('X-Frame-Options', 'DENY');

        if ($this->hsts) {
            $headers->set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
        }
    }
}
