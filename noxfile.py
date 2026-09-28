"""Development sessions."""

import shutil
from pathlib import Path

import nox

nox.options.default_venv_backend = "uv"
nox.options.sessions = ["tests", "typecheck"]

HERE = Path(__file__).parent


def _clean_build_artifacts() -> None:
    """Remove build state that leaks between pure and compiled builds."""
    for path in (HERE / "build", HERE / "dist", HERE / "wheelhouse"):
        shutil.rmtree(path, ignore_errors=True)
    for so in HERE.joinpath("src").rglob("*.so"):
        so.unlink()


@nox.session
def tests(s: nox.Session) -> None:
    """Run the suite against the pure-Python source tree."""
    s.run_install("uv", "sync", "--active", "--group", "test", external=True)
    s.run("pytest", "tests", "src", "--cov=boundinstance", *s.posargs)


@nox.session
def typecheck(s: nox.Session) -> None:
    """Run mypy and pyright."""
    s.run_install("uv", "sync", "--active", "--group", "lint", "--group", "test", external=True)
    s.run("mypy", "src", "tests")
    s.run("pyright", "src", "tests")


@nox.session
def wheel_pure(s: nox.Session) -> None:
    """Build the pure-Python wheel."""
    _clean_build_artifacts()
    s.run_install("uv", "sync", "--active", "--group", "build", external=True)
    s.run("python", "-m", "build", "--wheel", "--sdist")


@nox.session
def wheel_compiled(s: nox.Session) -> None:
    """Build the mypyc-compiled wheel and run the suite against it."""
    _clean_build_artifacts()
    s.run_install(
        "uv", "sync", "--active", "--group", "build", "--group", "test", external=True
    )
    s.run("python", "-m", "build", "--wheel", env={"HATCH_BUILD_HOOKS_ENABLE": "1"})
    wheel = next((HERE / "dist").glob("*.whl"))
    s.install(str(wheel))
    s.run("python", "-c", "import boundinstance; assert boundinstance.COMPILED")
    s.run(
        "pytest",
        "tests",
        "-m",
        "not incompatible_with_mypyc",
        env={"BOUNDINSTANCE_EXPECT_COMPILED": "1"},
    )


@nox.session
def benchmark(s: nox.Session) -> None:
    """Run the CodSpeed benchmarks."""
    s.run_install("uv", "sync", "--active", "--group", "bench", external=True)
    s.run("pytest", "tests/benchmark", "--codspeed")
