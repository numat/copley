"""Base functionality for async communication.

Distributed under the GNU General Public License v2
Copyright (C) 2019 NuMat Technologies
"""
from __future__ import annotations

import asyncio
import logging
from abc import abstractmethod

import serial

logger = logging.getLogger('copley')

class Client:
    """Serial or TCP client."""

    def __init__(self, timeout):
        """Initialize common attributes."""
        self.address = ''
        self.open = False
        self.timeout = timeout
        self.timeouts = 0
        self.max_timeouts = 10
        self.connection = {}
        self.reconnecting = False
        self.eol = b'\r'

    @abstractmethod
    async def _write(self, message):
        """Write a message to the device."""
        pass

    @abstractmethod
    async def _read(self, length):
        """Read a fixed number of bytes from the device."""
        pass

    @abstractmethod
    async def _readline(self):
        """Read until a LF terminator."""
        pass

    async def _write_and_read(self, command):
        """Write a command and read a response."""
        await self._handle_connection()
        if self.open:
            try:
                response = await self._handle_communication(command)
                if response is None:
                    return None
                else:
                    return response
            except asyncio.exceptions.IncompleteReadError:
                logger.error('IncompleteReadError.  Are there multiple connections?')
                return None
        else:
            return None

    async def _clear(self):
        """Clear the reader stream when it has been corrupted from multiple connections."""
        logger.warning("Multiple connections detected; clearing reader stream.")
        try:
            junk = await asyncio.wait_for(self._read(100), timeout=60)
            logger.warning(junk)
        except TimeoutError:
            pass

    @abstractmethod
    async def _handle_communication(self, command):
        """Manage communication, including timeouts and logging."""
        pass

    @abstractmethod
    def _handle_connection(self):
        pass

    @abstractmethod
    def close(self):
        """Close the connection."""
        pass


class TcpClient(Client):
    """A generic reconnecting asyncio TCP client.

    This base functionality can be used by any industrial control device
    communicating over TCP.
    """

    def __init__(self, address, timeout=1):
        """Communicator using a TCP/IP<=>serial gateway."""
        super().__init__(timeout)
        try:
            self.address, self.port = address.split(':')
        except ValueError as e:
            raise ValueError('address must be hostname:port') from e

    async def __aenter__(self):
        """Provide async entrance to context manager.

        Contrasting synchronous access, this will connect on initialization.
        """
        await self._handle_connection()
        return self

    def __exit__(self, *args):
        """Provide exit to context manager."""
        self.close()

    async def __aexit__(self, *args):
        """Provide async exit to context manager."""
        self.close()

    async def _connect(self):
        """Asynchronously open a TCP connection with the server."""
        self.close()
        reader, writer = await asyncio.open_connection(self.address, self.port)
        self.connection = {'reader': reader, 'writer': writer}
        self.open = True

    async def _read(self, length: int):
        """Read a fixed number of bytes from the device."""
        await self._handle_connection()
        response = await self.connection['reader'].read(length)
        return response.decode().strip()

    async def _readline(self):
        """Read until a line terminator."""
        await self._handle_connection()
        response = await self.connection['reader'].readuntil(self.eol)
        return response.decode().strip()

    async def _readlines(self, num_lines):
        """Read lines."""
        await self._handle_connection()
        lines: list[str] = []
        while len(lines) < num_lines:
            try:
                line = await self.connection['reader'].readuntil(self.eol)
                lines.append(line.decode().strip())
            except asyncio.CancelledError:
                print(f'Timed out! Did not get to {num_lines} lines.')
        return lines

    async def _write(self, command: str):
        """Write a command and do not expect a response.

        As industrial devices are commonly unplugged, this has been expanded to
        handle recovering from disconnects.
        """
        await self._handle_connection()
        to_write = command.encode() + self.eol
        self.connection['writer'].write(to_write)

    async def _handle_connection(self):
        """Automatically maintain TCP connection."""
        if self.open:
            return
        try:
            await asyncio.wait_for(self._connect(), timeout=0.75)
            self.reconnecting = False
        except (asyncio.TimeoutError, OSError):
            if not self.reconnecting:
                logger.error(f'Connecting to {self.address} timed out.')
            self.reconnecting = True

    async def _handle_communication(self, command):
        """Manage communication, including timeouts and logging."""
        try:
            await self._write(command)
            future = self._readlines(27)
            result = await asyncio.wait_for(future, timeout=10)
            self.timeouts = 0
            return result
        except (asyncio.TimeoutError, TypeError, OSError) as e:
            self.timeouts += 1
            if self.timeouts == self.max_timeouts:
                logger.error(f'Reading from {self.address} timed out '
                            f'{self.timeouts} times.')
                self.close()
            logger.exception(f'Exception: {e}')

    def close(self):
        """Close the TCP connection."""
        if self.open:
            self.connection['writer'].close()
        self.open = False


class SerialClient(Client):
    """Client using a directly-connected RS232 serial device."""

    def __init__(self, address=None, baudrate=9600, timeout=.15, bytesize=serial.EIGHTBITS,
                 stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE):
        """Initialize serial port."""
        super().__init__(timeout)
        self.address = address
        assert isinstance(self.address, str)
        self.serial_details = {'baudrate': baudrate,
                               'bytesize': bytesize,
                               'stopbits': stopbits,
                               'parity': parity,
                               'timeout': timeout}
        self.ser = serial.Serial(self.address, **self.serial_details)

    async def _read(self, length: int):
        """Read a fixed number of bytes from the device."""
        return self.ser.read(length).decode()

    async def _readline(self):
        """Read until a LF terminator."""
        return self.ser.readline().strip().decode()

    async def _write(self, message: str):
        """Write a message to the device."""
        self.ser.write(message.encode() + self.eol)

    def close(self):
        """Release resources."""
        self.ser.close()

    async def _handle_connection(self):
        self.open = True

    async def _handle_communication(self):
        pass
