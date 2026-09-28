# CyRIS — Cyber Risk Information System (SIH26105)

Boardroom cyber-financial terminal. Expected Annual Loss and VaR in Indian rupees, attack-path digital twin, counterfactual control simulation, Red/Blue/Judge evidence record, compliance mapping, and telemetry.

This frontend uses a typed mock risk engine until live APIs exist (`src/services/riskService.ts`).

## Run

```bash
npm install
npm run dev
```

Open the printed local URL (typically http://localhost:5173).

## Validate

```bash
npm test
npm run lint
npm run build
```

## Demo path

1. Dashboard — EAL ₹4,20,00,000, contributors, budget slider.
2. Digital Twin — select Attack Path #7, inspect privileged identity node.
3. Counterfactuals — approve **Enable MFA for privileged accounts**.
4. Return to Dashboard — EAL animates to ₹3,35,00,000.
5. Twin, telemetry, compliance, and agent debate reflect the same decision.

## Design

CSS tokens live in `src/styles/app.css`. Currency is formatted only via `formatINR`.
