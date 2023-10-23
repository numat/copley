"""Contains mocks for driver objects for offline testing."""
from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from .driver import TapDensity as RealTapDensity


class AsyncClientMock(MagicMock):
    """Magic mock that works with async methods."""

    async def __call__(self, *args, **kwargs):
        """Convert regular mocks into into an async coroutine."""
        return super().__call__(*args, **kwargs)


class TapDensity(RealTapDensity):
    """Mocks the overhead stirrer driver for offline testing."""

    def __init__(self, *args, **kwargs):
        """Set up connection parameters with default port."""
        super().__init__(*args, **kwargs)
        self.hw = AsyncClientMock()

    async def query(self, command):
        """Return mock requests to query."""
        if not self.lock:
            self.lock = asyncio.Lock()
        async with self.lock:  # lock releases on CancelledError
            if self.hw.address == "NO_RESPONSE":
                return None
            elif command == self.PRINT_REPORT:
                return 'hello world :)'

    def _parse(self, response):
        """Return mock requests to parsing."""
        if response is None:
            return {'on': False}
        else:
            return {
                'serial_number': 12345,
                'calc_type': "Fixed weight",
                'set_speed': "300",
                'total_taps': 1250,
                'sample_weight': "2.77",
                'init_volume': "170.0",
                'final_volume': "155.0",
                'bulk_density': "0.016",
                'tapped_density': "0.018",
                'hausner_ratio': "1.097",
                'compress_index': "8.82"
            }
