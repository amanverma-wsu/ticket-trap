# TicketTrap frontend

A static dashboard that visualizes the experiment: the security-vs-utility rates per
configuration, and every trial's full agent transcript with outcome badges. No backend or
API key is needed — it reads a bundled `public/results.json`.

## Run

```bash
cd frontend
npm install
npm run dev
```

Open the printed localhost URL. `npm run build` produces a static `dist/` for the demo.

## Refresh with real data

`public/results.json` ships as a sample from the offline reference agent. To regenerate it
from a real run, from the repo root:

```bash
python -m experiments.harness --live --repeats 5
python -m experiments.export_frontend --out frontend/public/results.json --real
```

The `--real` flag marks the bundle as live data so the UI badge reflects it.
