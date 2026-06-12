<?php

declare(strict_types=1);

namespace Acme\PaymentBundle\DependencyInjection;

use Symfony\Component\Config\Definition\Builder\TreeBuilder;
use Symfony\Component\Config\Definition\ConfigurationInterface;

/**
 * The Configuration tree is the bundle's public config contract. It
 * gives users validation, defaults, normalization and IDE autocompletion
 * (via bin/console config:dump-reference). The root name MUST equal the
 * Extension alias ('acme_payment').
 */
final class Configuration implements ConfigurationInterface
{
    public function getConfigTreeBuilder(): TreeBuilder
    {
        $treeBuilder = new TreeBuilder('acme_payment');
        $root = $treeBuilder->getRootNode();

        // @phpstan-ignore-next-line — fluent ArrayNodeDefinition API
        $root
            ->children()
                ->scalarNode('api_key')
                    ->isRequired()
                    ->cannotBeEmpty()
                    ->info('Secret key; reference an env var: %env(ACME_API_KEY)%')
                ->end()
                ->integerNode('timeout')
                    ->defaultValue(10)
                    ->min(1)
                    ->info('Request timeout in seconds.')
                ->end()
                ->enumNode('mode')
                    ->values(['live', 'sandbox'])
                    ->defaultValue('sandbox')
                ->end()
                ->arrayNode('retries')
                    ->addDefaultsIfNotSet()
                    ->children()
                        ->booleanNode('enabled')->defaultFalse()->end()
                        ->integerNode('max')->defaultValue(3)->min(0)->end()
                    ->end()
                ->end()
            ->end();

        return $treeBuilder;
    }
}
