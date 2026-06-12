import { init, track, pageview, optOut, optIn, createTakt } from '@vskstudio/takt-core'

// init() creates ONE shared instance, fires an initial pageview, and wires SPA nav.
// Privacy defaults (respectDnt / excludeLocalhost) are on — disable the latter in dev.
init({
  domain: 'example.com',
  outbound: true,
  files: true,
  fileExtensions: ['pdf', 'zip'],
  excludeLocalhost: false,
})

// Custom event: props values are strings; revenue amount is a STRING, currency 3 letters.
track('Signup', {
  props: { plan: 'pro' },
  revenue: { amount: '29.00', currency: 'EUR' },
})

// Manual pageview (e.g. a virtual route the SPA hook didn't catch).
pageview()

// Consent — both persisted, both no-op until init() has run.
optOut()
optIn()

// createTakt() returns a standalone instance the caller owns: no module singleton,
// no autocapture. You drive pageview()/track() yourself.
const takt = createTakt({ domain: 'example.com', sampleRate: 1 })
const stopSpa = takt.enableSpa()
const stopOutbound = takt.enableOutbound()
const stopFiles = takt.enableFiles(['pdf', 'csv'])
takt.pageview()
takt.track('Purchase', { revenue: { amount: '9.00', currency: 'USD' } })

// Disposers returned by the autocapture toggles unwire their listeners.
stopSpa()
stopOutbound()
stopFiles()
