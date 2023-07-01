# Release process for `spin`

## Introduction

Example `version`

- 1.8.dev0 # development version of 1.8 (release candidate 1)
- 1.8rc1 # 1.8 release candidate 1
- 1.8rc2.dev0 # development version of 1.8 release candidate 2
- 1.8 # 1.8 release
- 1.9.dev0 # development version of 1.9 (release candidate 1)

## Process

- Update and review `CHANGELOG.md`:

      changelist scientific-python/spin  <v0.0> main --version <0.1> >> CHANGELOG.md

  where <v0.0> is the last release and <0.1> is the new one.

- Update `version` in `pyproject.toml`.

- Commit changes:

      git add pyproject.toml CHANGELOG.md
      git commit -m 'Designate <version> release'

- Add the version number (e.g., `1.2.0`) as a tag in git:

      git tag -s [-u <key-id>] v<version> -m 'signed <version> tag'

  If you do not have a gpg key, use -u instead; it is important for
  Debian packaging that the tags are annotated

- Push the new meta-data to github:

      git push --tags origin main

  where `origin` is the name of the `github.com:scientific-python/spin`
  repository

- Review the github release page:

      https://github.com/scientific-python/spin/releases

- Publish on PyPi:

      git clean -fxd
      pip install -U build twine wheel
      python -m build --sdist --wheel
      twine upload -s dist/*

- Update `version` in `pyproject.toml`.

- Commit changes:

      git add pyproject.toml
      git commit -m 'Bump version'
      git push origin main
