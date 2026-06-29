"""Example strategies for notebook backtests.

These are deliberately simple, self-contained strategies used to exercise the
backtest pipeline from a notebook. Real strategy implementations belong in the
``snowball`` package; this module only exists so the notebooks have something
runnable while strategy packages are still being built out.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from decimal import Decimal

from core import (
    Strategy,
    StrategyAction,
    StrategyContext,
    StrategyDecisionCode,
    StrategyDecisionReason,
    StrategyEvent,
    StrategyParameters,
    StrategyResult,
    StrategyState,
    Tick,
    TradeSide,
)


class MovingAverageCrossStrategy(Strategy):
    """Open/close a single position on a fast/slow moving-average crossover.

    The strategy tracks two simple moving averages of the tick mid price. When
    the fast average crosses above the slow average it emits an OPEN_POSITION
    buy signal; when it crosses back below it emits a CLOSE_POSITION signal.
    It is intentionally naive and exists only to produce strategy events for
    the backtest notebook.

    Parameters:
        fast_period: Number of ticks in the fast moving average (default 5).
        slow_period: Number of ticks in the slow moving average (default 20).
        units: Position size requested on entry (default 1000).
    """

    @classmethod
    def default_parameters(cls) -> StrategyParameters:
        """Return the default fast/slow periods and order size."""
        return StrategyParameters.of(fast_period=5, slow_period=20, units=1000)

    def __init__(
        self,
        *,
        name: str,
        parameters: StrategyParameters | Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(name=name, parameters=parameters)
        self._fast_period = int(self.parameters.require("fast_period"))
        self._slow_period = int(self.parameters.require("slow_period"))
        self._units = Decimal(str(self.parameters.require("units")))
        self._prices: deque[Decimal] = deque(maxlen=self._slow_period)
        self._in_position = False
        self._tick_count = 0

    def on_tick(self, tick: Tick, context: StrategyContext) -> StrategyResult:
        """Update the moving averages and emit crossover signals."""
        self._tick_count += 1
        price = (tick.mid or tick.bid).amount
        self._prices.append(price)

        if len(self._prices) < self._slow_period:
            return StrategyResult(state=self._state())

        fast = self._average(self._fast_period)
        slow = self._average(self._slow_period)

        if not self._in_position and fast > slow:
            self._in_position = True
            return StrategyResult(
                events=(self._signal(tick, context, opening=True),),
                state=self._state(fast=fast, slow=slow),
            )
        if self._in_position and fast < slow:
            self._in_position = False
            return StrategyResult(
                events=(self._signal(tick, context, opening=False),),
                state=self._state(fast=fast, slow=slow),
            )
        return StrategyResult(state=self._state(fast=fast, slow=slow))

    def _average(self, period: int) -> Decimal:
        window = list(self._prices)[-period:]
        return sum(window, Decimal(0)) / Decimal(len(window))

    def _signal(
        self,
        tick: Tick,
        context: StrategyContext,
        *,
        opening: bool,
    ) -> StrategyEvent:
        action = StrategyAction.OPEN_POSITION if opening else StrategyAction.CLOSE_POSITION
        code = StrategyDecisionCode.ENTRY_SIGNAL if opening else StrategyDecisionCode.EXIT_SIGNAL
        return StrategyEvent(
            task_id=context.task_id,
            instrument=context.instrument,
            action=action,
            side=TradeSide.BUY if opening else None,
            units=self._units if opening else None,
            price=tick.mid or tick.ask,
            reason=StrategyDecisionReason(code=code, rule_id="ma_cross"),
        )

    def _state(self, *, fast: Decimal | None = None, slow: Decimal | None = None) -> StrategyState:
        return StrategyState.of(
            tick_count=self._tick_count,
            in_position=self._in_position,
            fast=str(fast) if fast is not None else "",
            slow=str(slow) if slow is not None else "",
        )
