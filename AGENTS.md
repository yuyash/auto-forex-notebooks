# Notebooks Package Guide

`notebooks` is the JupyterLab environment for AutoForexV2 exploration,
analysis, and backtesting experiments.

## Responsibilities

- Provide an interactive environment for ad-hoc analysis and prototyping.
- Use `core` for domain logic, `server` for orchestration/task primitives, and
  `oanda` for OANDA communication.

## Boundaries

- Keep production logic out of notebooks; promote stabilized code into the
  appropriate package (`core`, `server`, `oanda`).
- This is an environment-only project (`package = false`); it is not published.

## Commands

```bash
uv sync
uv run jupyter lab
uv run ruff check .
uv run ruff format .
uv run ty check
```
