# Maintainability-Brainstormer report

1. **Major — customization envelope.** Arbitrary substitutions multiply convergence/performance/accuracy combinations. Define bounded parameters and named device models, distinguish validated and experimental combinations; keep arbitrary topology editing outside initial scope.
2. **Major — coupling.** Circuit equations tied to JUCE, format adapters or solver details make experiments and upgrades expensive. Keep circuit/numerical engine host independent and use it for offline validation and benchmarks; avoid a speculative general framework.
3. **Major — state transitions.** Components, stored energy, cached coefficients and failure recovery interact. Classify live controls/reset-requiring settings and establish one continuity/failed-update/recovery policy with bounded audio work.
4. **Major — reference drift.** Separate copies of model values, presets and fixtures can drift. Version reference packages with schematic/model provenance, redistribution rights, values, conditions and expected results; identify versions in saved configurations and results.
5. **Major — saved model interpretation.** A new solver/model can change sound even with identical seeds/values. Define model-revision behavior, stable parameter identities and versioned state; retain old behavior or migrate explicitly.

Files read:
- `/home/alexandre/.codex/plugins/cache/egm/egm/0.1.0/agents/structural.md`
- `/home/alexandre/.codex/plugins/cache/egm/egm/0.1.0/skills/egm-brainstorm/SKILL.md`
- `/home/alexandre/.codex/plugins/cache/egm/egm/0.1.0/docs/codex.md`
- `/home/alexandre/projetos/emulador_tube_screamer/concepts_brief.md`

Read-only reviewer; persisted by synthesizer.
