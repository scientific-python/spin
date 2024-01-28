import nox


@nox.session
def tests_old_sh(session: nox.Session) -> None:
    """
    [TBD DEPCRECATED]Run the unit and regular tests.
    """
    session.install(".", "pytest", "build")
    session.run("bash", ".github/workflows/test.sh", external=True)

@nox.session
def tests_pytest(session: nox.Session) -> None:
    """
    [TBD DEPCRECATED]Run the unit and regular tests.
    """
    session.install(".", "pytest", "build")
    session.run("pytest", "spin", *session.posargs)
