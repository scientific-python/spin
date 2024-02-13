import nox


@nox.session
def test(session: nox.Session) -> None:
    session.install(".", "pytest", "build", "meson-python", "ninja")
    session.run("pytest", "spin", *session.posargs)
