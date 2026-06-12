<?php

declare(strict_types=1);

namespace Acme\PaymentBundle\DependencyInjection;

use Symfony\Component\Config\FileLocator;
use Symfony\Component\DependencyInjection\ContainerBuilder;
use Symfony\Component\DependencyInjection\Extension\Extension;
use Symfony\Component\DependencyInjection\Extension\PrependExtensionInterface;
use Symfony\Component\DependencyInjection\Loader\PhpFileLoader;

/**
 * A bundle's Extension is the bridge between the user's bundle config
 * (acme_payment:) and the container. The class name MUST follow the
 * convention <BundleAlias>Extension so Symfony auto-registers it; the
 * alias derived from the class name MUST match the Configuration root.
 */
final class AcmePaymentExtension extends Extension implements PrependExtensionInterface
{
    /**
     * @param array<array-key, mixed> $configs
     */
    public function load(array $configs, ContainerBuilder $container): void
    {
        // Merge + validate the user's config against the tree.
        $config = $this->processConfiguration(new Configuration(), $configs);

        // Load the bundle's service definitions.
        $loader = new PhpFileLoader($container, new FileLocator(__DIR__ . '/../../config'));
        $loader->load('services.php');

        // Turn validated config into container parameters / bind it into
        // a service. Don't read $_ENV here — expose it as config instead.
        $container->setParameter('acme_payment.api_key', $config['api_key']);
        $container->setParameter('acme_payment.timeout', $config['timeout']);

        // Conditionally wire services based on config — far cleaner than
        // a compiler pass when the decision is purely config-driven.
        if ($config['retries']['enabled']) {
            $container->getDefinition('acme_payment.client')
                ->addMethodCall('setMaxRetries', [$config['retries']['max']]);
        }
    }

    /**
     * prepend runs before other extensions load, letting a bundle set
     * sane defaults on *another* bundle (e.g. register a Twig path or a
     * framework http_client scope) without forcing the user to do it.
     */
    public function prepend(ContainerBuilder $container): void
    {
        if (!$container->hasExtension('framework')) {
            return;
        }

        $container->prependExtensionConfig('framework', [
            'http_client' => [
                'scoped_clients' => [
                    'acme_payment.http' => ['base_uri' => 'https://api.acme.test'],
                ],
            ],
        ]);
    }

    public function getAlias(): string
    {
        return 'acme_payment';
    }
}
