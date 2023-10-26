"""
A Python driver for Copley JV100i Tapped Density Tester.

Distributed under the GNU General Public License v2
Copyright (C) 2023 NuMat Technologies
"""
import asyncio
import logging
from typing import Any

from copley.util import Client, SerialClient, TcpClient

logger = logging.getLogger('copley')


class TapDensity:
    """Driver for Copley Tapped Density Tester.

    Command syntax and format from the manual:
    - Commands are not case sensitive
    - Commands must end in CR or LF (or both)
    - All responses end with a CR.
    """

    # ASCII command set
    READ_CYCLE_COUNT = "C"
    READ_CYCLE_COUNT_SP = "CS"
    READ_DATE = "DATE"
    READ_DURATION = "D"
    READ_DURATION_SP = "DS"
    READ_MODEL = "MODEL"
    PRINT_REPORT = "PR"  # THIS IS THE ONE WE REALLY CARE ABOUT
    PRINT_REPORT_LEFT = "PR1"
    PRINT_REPORT_RIGHT = "PR2"
    READ_SPEED_INT = "RPM?"
    READ_ACTUAL_SPEED = "S"
    READ_SET_SPEED = "SS"
    READ_SERIAL_NUMBER = "SN"
    READ_FIRMWARE = "V"
    RESET_TEST = "TRESET"

    def __init__(self, address, **kwargs):
        """Set up connection parameters, serial or IP address and port."""
        if address.startswith('/dev') or address.startswith('COM'):  # serial
            self.hw: Client = SerialClient(address=address, **kwargs)
        else:
            self.hw = TcpClient(address=address, **kwargs)
        self.lock = None  # needs to be initialized later, when the event loop exists

    async def __aenter__(self, *args: Any) -> 'TapDensity':
        """Provide async enter to context manager."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Provide async exit to context manager."""
        return

    async def query(self, query) -> str:
        """Query the device and return its response."""
        if not self.lock:
            self.lock = asyncio.Lock()
        async with self.lock:  # lock releases on CancelledError
            return await self.hw._write_and_read(query)

    async def get_report(self):
        """Get run report from the tapped density tester."""
        response = await self.query(self.PRINT_REPORT)
        return self._parse(response)

    async def reset(self):
        """Reset the Copley."""
        await self.hw._write(self.RESET_TEST)

    def _parse(self, response: str) -> dict:
        """Parse a tapped density report. Data output format is ASCII."""
        if response is None:
            return {'on': False}
        else:
            for line in response:
                value = line.strip().split(':')[1].strip()
                if "Serial number" in line:
                    sn = int(value)
                elif "Calculation type" in line:
                    calc_type = value
                elif "Set Speed" in line:
                    set_speed = value
                elif "Total Taps" in line:
                    total_taps = int(value)
                elif "Sample Weight, W" in line:
                    sample_weight = value
                elif "Initial Volume" in line:
                    init_volume = value
                elif "Final Volume" in line:
                    final_volume = value
                elif "Bulk Density" in line:
                    bulk_density = value
                elif "Tapped Density (g/mL)" in line:
                    tapped_density = value
                elif "Hausner Ratio" in line:
                    hausner_ratio = value
                elif "Compress. Index" in line:
                    compress_index = value
            try:
                return {
                    'serial_number': sn,
                    'calc_type': calc_type,
                    'set_speed': set_speed,
                    'total_taps': total_taps,
                    'sample_weight': sample_weight,
                    'init_volume': init_volume,
                    'final_volume': final_volume,
                    'bulk_density': bulk_density,
                    'tapped_density': tapped_density,
                    'hausner_ratio': hausner_ratio,
                    'compress_index': compress_index
                }
            except Exception as e:
                raise e
