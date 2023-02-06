"""Nox sessions."""

import os
import tempfile
from typing import Any

import nox

nox.options.sessions = "lint", "safety", "mypy", "tests"
locations = "src", "tests", "noxfile.py", "docs/conf.py"
package = "tutorial_hypermodern_python_winand"


def install_with_constraints(session: nox.Session, *args: str, **kwargs: Any) -> None:
    """Install packages taking into account version constraints in Poetry."""
    # NamedTemporaryFile Permission denied https://stackoverflow.com/a/54768241
    requirements = tempfile.NamedTemporaryFile(delete=False)
    try:
        session.run(
            "poetry",
            "export",
            "--with=dev",
            "--format=constraints.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)
    finally:
        requirements.close()
        os.unlink(requirements.name)


@nox.session(python=["3.9", "3.8"])
def lint(session: nox.Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
    )
    session.run("flake8", *args)


@nox.session(python=["3.9", "3.8"])
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", "--without=dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock"
    )
    session.run("pytest", *args)


@nox.session(python="3.9")
def black(session: nox.Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python="3.9")
def safety(session: nox.Session) -> None:
    """Scan dependencies for insecure packages."""
    # NamedTemporaryFile Permission denied https://stackoverflow.com/a/54768241
    requirements = tempfile.NamedTemporaryFile(delete=False)
    try:
        session.run(
            "poetry",
            "export",
            "--with=dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        install_with_constraints(session, "safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")
    finally:
        requirements.close()
        os.unlink(requirements.name)


@nox.session(python=["3.9", "3.8"])
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    install_with_constraints(session, "mypy", "click")
    session.run("mypy", "--install-types", "--non-interactive", *args)


@nox.session(python=["3.9", "3.8"])
def pyright(session: nox.Session) -> None:
    """Run the static type checker pyright."""
    args = session.posargs or locations
    install_with_constraints(session, "pyright")
    session.run("pyright", *args)


@nox.session(python=["3.9", "3.8"])
def typeguard(session: nox.Session) -> None:
    """Runtime type checking using Typeguard."""
    args = session.posargs or ["-m", "not e2e"]
    session.run("poetry", "install", "--only=main", external=True)
    install_with_constraints(session, "pytest", "pytest-mock", "typeguard")
    session.run("pytest", f"--typeguard-packages={package}", *args)


@nox.session(python=["3.9", "3.8"])
def xdoctest(session: nox.Session) -> None:
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("poetry", "install", "--only=main", external=True)
    install_with_constraints(session, "xdoctest")
    session.run("xdoctest", package, *args)


@nox.session(python="3.9")
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    session.run("poetry", "install", "--only=main", external=True)
    install_with_constraints(session, "sphinx", "sphinx-autodoc-typehints")
    session.run("sphinx-build", "-W", "--keep-going", "docs", "docs/_build")


@nox.session(python="3.9")
def coverage(session: nox.Session) -> None:
    """Upload coverage data.

    codecov tool is supposed to be available.
    https://docs.codecov.com/docs/codecov-uploader

    Args:
        session: Nox Session instanse
    """
    install_with_constraints(session, "coverage[toml]")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
