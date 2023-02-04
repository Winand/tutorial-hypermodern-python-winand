"""pytest configuration and common fixtures.

Fixtures placed in a conftest.py file are discovered automatically,and test
modules at the same directory level can use them without explicit import.
https://docs.pytest.org/en/latest/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files
"""

from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_requests_get(mocker: MockerFixture) -> Mock:
    """Fixture for mocking requests.get method."""
    mock = mocker.patch("requests.get")
    mock.return_value.__enter__.return_value.json.return_value = {
        "title": "Lorem Ipsum",
        "extract": "Lorem ipsum dolor sit amet",
    }
    return mock


def pytest_addoption(parser: pytest.Parser) -> None:
    """Console option to run tests with `e2e` mark.

    See also https://stackoverflow.com/a/33181491

    Args:
        parser: Parser for command line arguments and ini-file values.
    """
    parser.addoption(
        "--with-e2e",
        action="store_true",
        dest="with_e2e",
        default=False,
        help="Enable end-to-end tests",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Pytest configuration hook."""
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
    if not config.option.markexpr and not config.option.with_e2e:
        config.option.markexpr = "not e2e"
    elif config.option.markexpr and config.option.with_e2e:
        raise ValueError("--with-e2e is not supported with -m")
