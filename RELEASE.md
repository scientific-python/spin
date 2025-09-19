# Release process for `spin`

## Introduction

Example `version number`

- 1.8.dev0 # development version of 1.8 (release candidate 1)
- 1.8rc1 # 1.8 release candidate 1
- 1.8rc2.dev0 # development version of 1.8 release candidate 2
- 1.8 # 1.8 release
- 1.9.dev0 # development version of 1.9 (release candidate 1)

## Process

- Set release variables:

      export VERSION=<version number>
      export PREVIOUS=<previous version number>
      export ORG="scientific-python"
      export REPO="spin"
      export LOG="CHANGELOG.md"

- Autogenerate release notes:

      changelist ${ORG}/${REPO} v${PREVIOUS} main --version ${VERSION} --out ${VERSION}.md

- Put the output of the above command at the top of `CHANGELOG.md`:

      cat ${VERSION}.md | cat - ${LOG} > temp && mv temp ${LOG}

- Update `version` in `spin/__init__.py`.

- Commit changes:

      git add spin/__init__.py CHANGELOG.md
      git commit -m "Designate ${VERSION} release"

- Tag the release in git:

      git tag -a -s v${VERSION} -m "signed ${VERSION} tag"

  If you do not have a gpg key, use -u instead; it is important for
  Debian packaging that the tags are annotated

- Push the new meta-data to github:

      git push --tags origin main

  where `origin` is the name of the `github.com:scientific-python/spin`
  repository

- Review the github tags page:

      https://github.com/scientific-python/spin/tags

  and create a release. Paste the content of "${VERSION}.md" into the
  release notes, apart from the title line starting with `#`.

- Update `version` in `spin/__init__.py` to `0.Xrc0.dev0`.

- Commit changes:

      git add spin/__init__.py
      git commit -m 'Bump version'
      git push origin main
