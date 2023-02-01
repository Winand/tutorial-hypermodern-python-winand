"""
Fixtures placed in a conftest.py file are discovered automatically,and test
modules at the same directory level can use them without explicit import.
https://docs.pytest.org/en/latest/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files
"""

from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_requests_get(mocker: MockerFixture) -> Mock:
    mock = mocker.patch("requests.get")
    mock.return_value.__enter__.return_value.json.return_value = {
        "title": "Lorem Ipsum",
        "extract": "Lorem ipsum dolor sit amet",
    }
    return mock


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
