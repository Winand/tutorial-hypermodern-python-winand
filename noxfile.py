import os
import tempfile

import nox

nox.options.sessions = "lint", "safety", "mypy", "tests"
locations = "src", "tests", "noxfile.py"
package = "tutorial_hypermodern_python_winand"


def install_with_constraints(session, *args, **kwargs):
    """
    Install packages taking into account version constraints in Poetry
    """
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
def lint(session: nox.Session):
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-import-order",
    )
    session.run("flake8", *args)


@nox.session(python=["3.9", "3.8"])
def tests(session: nox.Session):
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", "--without=dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock"
    )
    session.run("pytest", *args)


@nox.session(python="3.9")
def black(session):
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python="3.9")
def safety(session):
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
def mypy(session):
    args = session.posargs or locations
    install_with_constraints(session, "mypy", "click")
    session.run("mypy", "--install-types", "--non-interactive", *args)


@nox.session(python=["3.9", "3.8"])
def pyright(session):
    """Run the static type checker."""
    args = session.posargs or locations
    install_with_constraints(session, "pyright")
    session.run("pyright", *args)


@nox.session(python=["3.9", "3.8"])
def typeguard(session):
    args = session.posargs or ["-m", "not e2e"]
    session.run("poetry", "install", "--only=main", external=True)
    install_with_constraints(session, "pytest", "pytest-mock", "typeguard")
    session.run("pytest", f"--typeguard-packages={package}", *args)
