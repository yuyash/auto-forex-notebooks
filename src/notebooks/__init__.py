"""Support code for AutoForexV2 exploration notebooks.

This package holds the small, reusable helpers that notebooks rely on so the
notebook cells themselves stay focused on the analysis. It is intentionally
thin: production logic belongs in ``core``, ``server``, ``oanda``, or
``snowball``.
"""

from notebooks.strategies import MovingAverageCrossStrategy

__all__ = [
    "MovingAverageCrossStrategy",
]
