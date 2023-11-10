import nox


@nox.session
def tests(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    session.install(".", "pytest", "build")
    session.run("pytest", "spin", *session.posargs)
    session.run("bash", ".github/workflows/test.sh", external=True)
