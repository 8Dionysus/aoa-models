# Decision lane law

## Authority

Canonical `AOA-MODELS-D-####-*.md` files are the authored source of durable
`aoa-models` rationale. `generated/decision-index.md` is a lookup projection
only and must be rebuilt from source.

## Admission

Record a decision only when a future contributor would otherwise lose a
meaningful owner, object, lifecycle, evidence, validation, or consumer-boundary
rationale. Ordinary implementation notes, experiments, run receipts, proof
verdicts, and open options belong elsewhere.

## Required shape

Each accepted record must include:

- status and canonical decision ID;
- original date and owner facets;
- context and durable pressure;
- material alternatives;
- accepted decision and rationale;
- consequences and explicit non-ownership;
- source surfaces, follow-up owner, and verification.

Use the next number visible in canonical source records. Do not infer an ID
from a generated index or another repository.

## Builder and check

```bash
python scripts/generate_decision_index.py
python scripts/generate_decision_index.py --check
```

Never hand-edit `generated/decision-index.md`.
