"""Test the copley driver responds with correct data."""
from unittest import mock

import pytest

from copley import command_line
from copley.mock import TapDensity

ADDRESS = '192.168.10.18:23'


@pytest.fixture
def driver():
    """Confirm the overhead stirrer correctly initializes."""
    return TapDensity(ADDRESS)


@mock.patch('copley.TapDensity', TapDensity)
def test_driver_cli(capsys):
    """Confirm the commandline interface works."""
    command_line([ADDRESS])
    captured = capsys.readouterr()
    assert "bulk_density" in captured.out
    assert "tapped_density" in captured.out
    assert "null" not in captured.out

@mock.patch('copley.TapDensity', TapDensity)
def test_driver_cli_noresponse(capsys):
    """Confirm the commandline interface works."""
    command_line(["NO_RESPONSE"])
    captured = capsys.readouterr()
    assert "on" in captured.out
    assert "tapped_density" not in captured.out
