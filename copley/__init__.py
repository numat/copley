"""
Python driver for Copley JV100i Tapped Density Tester.

Distributed under the GNU General Public License v2
Copyright (C) 2023 NuMat Technologies
"""
from typing import Any

from copley.driver import TapDensity


def command_line(args: Any = None) -> None:
    """Command line tool exposed through package install."""
    import argparse
    import asyncio
    import json

    parser = argparse.ArgumentParser(description="Read scale status.")
    parser.add_argument('address', help="The serial or IP address of the copley.")
    parser.add_argument('-r', '--reset', action='store_true', help="Reset test on device.")
    args = parser.parse_args(args)

    if args.reset:
        async def reset() -> None:
            async with TapDensity(address=args.address) as copley:
                await copley.reset()
                print("OK")
        asyncio.run(reset())
    else:
        async def get() -> None:
            async with TapDensity(address=args.address) as copley:
                report = await copley.get_report()
                print(json.dumps(report, indent=4))
        asyncio.run(get())


if __name__ == '__main__':
    command_line()
