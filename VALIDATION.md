# Validation routes

Run model and research-intake checks on demand after changing model sources,
fit projections, or their tests:

```bash
python scripts/validate_models.py
python scripts/validate_research_intake.py
python scripts/build_model_fit_projections.py --check
python scripts/generate_decision_index.py --check
python scripts/check_live_codex_catalog.py
python -m unittest discover -s tests -v
```

## Decisions

```bash
python scripts/generate_decision_index.py
```

Then use the decision-index check in the model route above.
