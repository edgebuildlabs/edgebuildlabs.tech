# edgebuildlabs.tech

Brand site of Edge Build Labs. Static HTML built with [Astro](https://astro.build); `dist/` is committed and is what our own
server serves (a Caddy host on the same VPS that runs Living World, pulled from this repository every 15 minutes).

- Text and brand (symbol, wordmark): (c) Edge Build Labs. Facts on the site carry a date or the words NOT VERIFIED.
- Theme: derived from [blackspike astro landing page](https://github.com/blackspike/blackspike-astro-landing-page) by
  blackspike design, CC BY 4.0 (`LICENSE-blackspike-CC-BY-4.0.txt`).
- Typeface: Source Serif 4, SIL Open Font License 1.1 (`public/fonte/OFL.txt`).
- No trackers, no cookies, no third-party requests at runtime; the YouTube player loads only after a click.

## Build

```
npm install
npm run build          # -> dist/
python -m http.server 8766 --directory dist
```

The thesis site (method, in English) lives at https://edgebuildlabs.github.io; the public contracts at
https://github.com/edgebuildlabs/evidence-contracts.
