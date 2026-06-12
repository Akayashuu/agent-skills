import { track } from '@vskstudio/takt-core'
import type { Config, InitOptions, Revenue, TrackOptions } from '@vskstudio/takt-core'

// Revenue is { amount: string; currency: string } — never a number.
const sale: Revenue = { amount: '29.00', currency: 'EUR' }

// TrackOptions carries optional string-keyed props and an optional revenue.
const opts: TrackOptions = {
  props: { plan: 'pro', source: 'pricing-page' },
  revenue: sale,
}
track('Purchase', opts)

// Config (createTakt) and InitOptions (init) share the privacy/sampling fields;
// InitOptions adds the autocapture toggles (auto / outbound / files / fileExtensions).
const baseConfig: Config = {
  domain: 'example.com',
  respectDnt: true,
  excludeLocalhost: true,
  sampleRate: 0.5,
  trackQuery: true,
  queryParams: ['ref', 'utm_source'],
  scrubUrl: (rawUrl) => rawUrl.split('?')[0],
}

const initOptions: InitOptions = {
  ...baseConfig,
  auto: true,
  outbound: true,
  files: true,
  fileExtensions: ['pdf', 'zip'],
}

export { baseConfig, initOptions }
