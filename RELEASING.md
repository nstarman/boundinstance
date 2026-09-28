# Release Process for `boundinstance`

`boundinstance` is a single package, versioned entirely from git tags via
[hatch-vcs](https://github.com/ofek/hatch-vcs) — there is **no version string
to bump** in `pyproject.toml` or anywhere else. Tagging the release commit
`vX.Y.Z` is the whole version bump.

Releases are automated via GitHub Actions (`.github/workflows/publish.yml`):
publishing a GitHub Release builds the sdist and the full mypyc-compiled
wheel matrix, then uploads first to TestPyPI and, only if that succeeds, to
PyPI. Both uploads use [trusted publishing](https://docs.pypi.org/trusted-publishers/)
(OIDC) — there are no API tokens to manage.

---

## Prerequisites: trusted publishers (one-time setup)

**Both trusted publishers must be registered before the first tag.** The
`publish` job needs `test-publish` to succeed first, so a missing **TestPyPI**
publisher blocks the real PyPI release just as effectively as a missing PyPI
one — and by the time that failure surfaces, the tag (and the GitHub Release)
is already public. A PyPI version number can never be reused, so getting this
wrong after tagging is not something a re-run can fix.

The two GitHub deployment environments (`testpypi` and `pypi`) already exist
on this repository — create them once with:

```bash
gh api -X PUT repos/nstarman/boundinstance/environments/testpypi -F wait_timer=0
gh api -X PUT repos/nstarman/boundinstance/environments/pypi -F wait_timer=0
gh api repos/nstarman/boundinstance/environments --jq '.environments[].name'
# Expected: pypi, testpypi
```

Registering the trusted publisher itself has to be done by hand, signed in as
the project owner, at each index. Use these exact values:

| Field | Value |
| --- | --- |
| PyPI Project Name | `boundinstance` |
| Owner | `nstarman` |
| Repository name | `boundinstance` |
| Workflow name | `publish.yml` |
| Environment name | `testpypi` (TestPyPI) / `pypi` (PyPI) |

Add a pending publisher in **both** places:

- TestPyPI: <https://test.pypi.org/manage/account/publishing/> — environment `testpypi`
- PyPI: <https://pypi.org/manage/account/publishing/> — environment `pypi`

Verify both are registered before pushing any tag.

---

## Before you tag

```bash
git status               # clean
git pull origin main
uv run nox -s tests
uv run nox -s typecheck
uv run nox -s wheel_compiled   # builds the mypyc wheel, runs the suite against it
```

`wheel_compiled` is the closest local approximation of what CI's release
matrix does — it's worth running before every tag, since a mypyc compile
failure on your platform is a strong signal the release build will fail too.

## Releasing

```bash
git tag vX.Y.Z -m "Release X.Y.Z"
git push origin vX.Y.Z
```

Then create a GitHub Release from that tag (Releases → Draft a new release →
choose the tag → Publish release). Publishing the Release is what triggers
`publish.yml` — pushing the tag alone does not.

The workflow:

1. Builds the sdist and, in parallel, the full cibuildwheel matrix (cp312–cp314 × Linux/macOS/Windows).
2. Uploads everything to TestPyPI (`skip-existing: true`, so a version already there, or a TestPyPI hiccup, doesn't fail the job).
3. Only if that job succeeds, uploads the same artifacts to PyPI.

Monitor it at <https://github.com/nstarman/boundinstance/actions>.

## Testing the workflow without publishing

`workflow_dispatch` on `publish.yml` takes a `publish` boolean input
(default `false`). Dispatching it with `publish=false` builds the sdist and
every wheel but skips both publish jobs — a good way to confirm the build
matrix still works without touching either index:

```bash
gh workflow run publish.yml -f publish=false
gh run watch
```

Note: `workflow_dispatch` only dispatches workflows present on the
repository's **default branch**, so this only works once `publish.yml` has
been merged to `main`.

## Troubleshooting

**Tag pushed but nothing happened.** `publish.yml` triggers on `release:
published`, not on the tag push itself — create the GitHub Release from the
tag.

**`test-publish` failed and `publish` was skipped.** That's the gate working
as intended — a real TestPyPI failure (not a "already exists" collision,
which `skip-existing: true` absorbs) should block the PyPI upload. Fix the
underlying issue and re-run the workflow from the same tag/release.

**Wrong version published.** `hatch-vcs` derives the version from `git
describe --tags`; check `git tag -l` and `hatch version` (or `uv run hatch
version`) locally against what you expect before tagging.

**Version shows as `0.0.0` or a `+dXXXXXXXX` dirty suffix locally.** You're
either not on a tagged commit, haven't fetched tags (`git fetch --tags`), or
have uncommitted changes. This is expected between releases and is not a
release blocker — CI always builds from a clean checkout of the tag.
