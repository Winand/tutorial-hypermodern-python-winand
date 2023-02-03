"""Test cases for the `console` module."""

from unittest.mock import Mock

from click.testing import CliRunner
import pytest
from pytest_mock import MockerFixture
import requests

from tutorial_hypermodern_python_winand import console


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for CliRunner (Click) which allows to run CLI commands."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner, mock_requests_get: Mock) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(console.main)
    assert result.exit_code == 0


def test_main_prints_title(runner: CliRunner, mock_requests_get: Mock) -> None:
    """It prints page title."""
    result = runner.invoke(console.main)
    assert "Lorem Ipsum" in result.output


def test_main_invokes_requests_get(runner: CliRunner, mock_requests_get: Mock) -> None:
    """It calls requests.get."""
    runner.invoke(console.main)
    assert mock_requests_get.called


def test_main_uses_en_wikipedia_org(runner: CliRunner, mock_requests_get: Mock) -> None:
    """It sends request to en.wikipedia.org by default."""
    runner.invoke(console.main)
    args, _ = mock_requests_get.call_args
    assert "en.wikipedia.org" in args[0]


def test_main_fails_on_request_error(
    runner: CliRunner, mock_requests_get: Mock
) -> None:
    """It exits with a status code of 1 if request fails."""
    mock_requests_get.side_effect = Exception("Boom")
    result = runner.invoke(console.main)
    assert result.exit_code == 1


def test_main_prints_message_on_request_error(
    runner: CliRunner, mock_requests_get: Mock
) -> None:
    """It prints `Error` if request fails."""
    mock_requests_get.side_effect = requests.RequestException
    result = runner.invoke(console.main)
    assert "Error" in result.output


@pytest.fixture
def mock_wikipedia_random_page(mocker: MockerFixture) -> Mock:
    """Fixture for mocking wikipedia.random_page method."""
    return mocker.patch("tutorial_hypermodern_python_winand.wikipedia.random_page")


def test_main_uses_specified_language(
    runner: CliRunner, mock_wikipedia_random_page: Mock
) -> None:
    """It uses Wikipedia version specified in --language argument."""
    runner.invoke(console.main, ["--language=pl"])
    mock_wikipedia_random_page.assert_called_with(language="pl")


@pytest.mark.e2e
def test_main_succeeds_in_production_env(runner: CliRunner) -> None:
    """End-to-end: it exits with 0 code after successful request."""
    result = runner.invoke(console.main)
    assert result.exit_code == 0
