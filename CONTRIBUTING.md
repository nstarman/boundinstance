# Contributing to `boundinstance`

## Reporting Issues

When opening an issue to report a problem, please try to provide:

- a minimal code example that reproduces the issue
- and details of the operating system and the dependency versions you are using.

## Contributing Code and Documentation

So you are interested in contributing to `boundinstance`? Excellent! We love contributions! `boundinstance` is open source, built on open source, and we'd love to have you hang out in our community.

## How to Contribute, Best Practices

Most contributions to `boundinstance` are done via [pull requests](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) from GitHub users' forks of the [`boundinstance` repository](https://github.com/nstarman/boundinstance). If you are new to this style of development, check out Astropy's [development workflow](https://docs.astropy.org/en/latest/development/quickstart.html).

Once you open a pull request (which should be opened against the `main` branch, not against any of the other branches), please make sure to include the following:

- **Code**: the code you are adding.

- **Tests**: these are usually tests to ensure code that previously failed now works (regression tests), or tests that cover as much as possible of the new functionality to make sure it does not break in the future and also returns consistent results on all platforms (since we run these tests on many platforms/configurations). This project gates CI on 100% coverage (`tool.coverage.report.fail_under` in `pyproject.toml`), so new code needs tests that exercise it.

- **Documentation**: if you are adding new functionality, be sure to include a description in the docstrings and, where relevant, the documentation site.

- **Performance improvements**: if you are making changes that impact `boundinstance` performance, consider adding a benchmark under `tests/benchmark` (`nox -s benchmark`, CodSpeed-backed).

## Getting Started

```bash
git clone https://github.com/your-username-here/boundinstance.git
cd boundinstance
uv sync --group dev
uv run pre-commit install
```

Run the test suite:

```bash
uv run nox -s tests
```

Run the type checkers (mypy + pyright):

```bash
uv run nox -s typecheck
```

`boundinstance` also ships mypyc-compiled wheels; to build one locally and run the suite against it:

```bash
uv run nox -s wheel_compiled
```

## Working on the Documentation

The documentation site is built with [zensical](https://zensical.org). Preview your changes locally:

```bash
uv run zensical serve
```

Then open `localhost:8000` in a web browser to see your changes live.

## Checklist for Contributed Code

Before being merged, a pull request for a new feature will be reviewed to see if it meets the following requirements. If you are unsure about how to meet all of these requirements, please submit the PR and ask for help and/or guidance. A `boundinstance` maintainer will collaborate with you to make sure that the pull request meets the requirements for inclusion in the package:

**Relevance:**

- Is the submission relevant to `boundinstance`?
- Does the code perform as expected?
- If applicable, are references included to the origin source for the algorithm?
- Has the code been tested against previously existing implementations?

**Code Quality:**

- Are the coding guidelines followed?
- Is the code compatible with the supported versions of Python?
- Are there dependencies other than the run-time dependencies listed in `pyproject.toml`?

**Testing:**

- Are the testing guidelines followed?
- Are the inputs to the functions sufficiently tested?
- Are there tests for any exceptions raised?
- Are there tests for the expected performance?
- Are the sources for the tests documented?
- Does `uv run nox -s tests` run without failures?
- Does `uv run nox -s typecheck` run without failures?

**Documentation:**

- Is there a docstring in the function describing:
  - What the code does?
  - The format of the inputs of the function?
  - The format of the outputs of the function?
  - References to the original algorithms?
  - Any exceptions which are raised?
  - An example of running the code?
- Is there any information needed to be added to the docs to describe the function?
- Does the documentation build without errors or warnings (`uv run zensical serve`)?

## Commit Messages

Commits follow [Conventional Commits](https://www.conventionalcommits.org) with [gitmoji](https://gitmoji.dev), enforced by [commitizen](https://commitizen-tools.github.io/commitizen/) (`cz-conventional-gitmoji`) as a pre-commit hook: `<emoji> <type>: <description>`. See the git log for examples.
