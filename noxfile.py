import os
import tempfile

import nox

nox.options.sessions = "lint", "safety", "tests"
locations = "src", "tests", "noxfile.py"


@nox.session(python=["3.9", "3.8"])
def lint(session: nox.Session):
    args = session.posargs or locations
    session.install("flake8", "flake8-bandit", "flake8-black",
                    "flake8-bugbear", "flake8-import-order")
    session.run("flake8", *args)


@nox.session(python=["3.9", "3.8"])
def tests(session: nox.Session):
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session(python="3.9")
def black(session):
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@nox.session(python="3.9")
def safety(session):
    # NamedTemporaryFile Permission denied https://stackoverflow.com/a/54768241
    requirements = tempfile.NamedTemporaryFile(delete=False)
    try:
        session.run(
            "poetry", "export",
            "--with=dev", "--format=requirements.txt", "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install("safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")
    finally:
        requirements.close()
        os.unlink(requirements.name)
