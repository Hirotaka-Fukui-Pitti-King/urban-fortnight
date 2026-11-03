# Statistical-Mechanical New Keynesian Economics

A research program joining heterogeneous-agent New Keynesian macroeconomics and non-equilibrium statistical mechanics. The central question is: **How do socially interacting expectations and endogenous wealth distributions change monetary transmission, fluctuations, and macroeconomic tipping points?**

## Stages

| Stage | Mechanism | Research plan |
|:---:|---|---|
| 0 | New Keynesian and HANK Baseline | [Stage 0](stage-0-nk-hank-baseline/README.md) |
| 1 | Ising Expectations and Social Interactions | [Stage 1](stage-1-ising-social-expectations/README.md) |
| 2 | Kinetic Exchange and Wealth Distribution | [Stage 2](stage-2-kinetic-exchange-wealth/README.md) |
| 3 | Statistical Equilibrium and Entropy | [Stage 3](stage-3-statistical-equilibrium/README.md) |
| 4 | Bouchaud-Inspired Firm Fragility | [Stage 4](stage-4-bouchaud-firm-fragility/README.md) |
| 5 | Minority Game and Financial Markets | [Stage 5](stage-5-minority-game-financial-markets/README.md) |
| 6 | Random Matrix Methods and Systemic Risk | [Stage 6](stage-6-random-matrix-systemic-risk/README.md) |

**Agent-based methods run through the entire project**, rather than being added as a separate final stage. Every stage adds a mechanism to a model with explicit household/firm budgets and goods, labor and asset market clearing. New mechanisms must be compared with matched switch-off baselines and verified against numerical residuals.

Each stage contains `plan.json` (machine-readable contract), `README.md` (research plan), `RESEARCH.me` (literal plain-text `.me` memo), and `results/` (future validated outputs). The aggregate schema is in `research-plan.json`. No numerical research results are claimed at this point.

## English research paper and slides

- Paper: `paper/article.qmd`, Quarto's native **Typst article** format.
- Slides: `slides/research-agenda.qmd`, **quarto-clean-typst** from [Kazuharu Yanagimoto](https://github.com/kazuyanagimoto/quarto-clean-typst).
- GitHub Actions: `.github/workflows/build-paper.yml`, plan validation, both renders, PDF artifact upload.

The specified Clean Typst theme is a **slide theme**, not an academic article template. Its MIT-licensed upstream code is vendored in `_extensions/clean/`; see `UPSTREAM.md` for source hashes.

With Quarto >= 1.8, render using:

```bash
quarto render paper/article.qmd --to typst
quarto render slides/research-agenda.qmd --to clean-typst
```

## Reproducibility rule

Record economic equations, parameter values, input provenance, seeds, tolerances, accounting and optimality residuals, ablations and convergence diagnostics with each new result. Entropy maximization and critical phenomena must be *derived under explicit assumptions*, not inferred from a plot alone.
