"""Dry-run: live market data, simulated execution."""

from trading_platform.adapters.execution.simulated import SimulatedExecutionBase
from trading_platform.core.ports import ExecutionPort


class BitunixDryRunExecution(SimulatedExecutionBase, ExecutionPort):
    """Uses real tickers but never sends orders to exchange."""

    pass
