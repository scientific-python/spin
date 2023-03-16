# Changelog

## [v0.1rc0](https://github.com/scientific-python/spin/tree/v0.1rc0) (2023-3-16)

[Full Changelog](https://github.com/scientific-python/spin/compare/v0.1...v0.1rc0)

**Closed issues:**

- Make releases that projects can pin to [\#53](https://github.com/scientific-python/spin/issues/53)

**Merged pull requests:**

- Test on more Python versions [\#64](https://github.com/scientific-python/spin/pull/64) ([jarrodmillman](https://github.com/jarrodmillman))
- Rename package [\#63](https://github.com/scientific-python/spin/pull/63) ([jarrodmillman](https://github.com/jarrodmillman))
- Update release process [\#61](https://github.com/scientific-python/spin/pull/61) ([jarrodmillman](https://github.com/jarrodmillman))

## [v0.1](https://github.com/scientific-python/spin/tree/v0.1) (2023-3-10)

[Full Changelog](https://github.com/scientific-python/spin/compare/v0.1a1...v0.1)

**Closed issues:**

- python dev.py python no longer works [\#58](https://github.com/scientific-python/spin/issues/58)
- Is `--reconfigure` necessary on each invocation of `meson setup`? [\#54](https://github.com/scientific-python/spin/issues/54)
- Run build command before tests [\#50](https://github.com/scientific-python/spin/issues/50)
- Installing spin [\#46](https://github.com/scientific-python/spin/issues/46)
- Additional windows problems [\#38](https://github.com/scientific-python/spin/issues/38)
- windows builds cannot be tested [\#32](https://github.com/scientific-python/spin/issues/32)
- Aesthetic improvements [\#21](https://github.com/scientific-python/spin/issues/21)
- Add emoji and color to command line printing [\#20](https://github.com/scientific-python/spin/issues/20)
- Describe history of dev.py in README [\#19](https://github.com/scientific-python/spin/issues/19)
- Passing test arguments for a project \(e.g. numpy\) [\#13](https://github.com/scientific-python/spin/issues/13)
- `spin build` should install to a new directory, rather than the build dir [\#12](https://github.com/scientific-python/spin/issues/12)
- Refactor testing [\#10](https://github.com/scientific-python/spin/issues/10)

**Merged pull requests:**

- Update pre-commit [\#60](https://github.com/scientific-python/spin/pull/60) ([jarrodmillman](https://github.com/jarrodmillman))
- Only configure/reconfigure as necessary [\#59](https://github.com/scientific-python/spin/pull/59) ([stefanv](https://github.com/stefanv))
- pytest: replace existing process [\#57](https://github.com/scientific-python/spin/pull/57) ([stefanv](https://github.com/stefanv))
- Add docstrings [\#56](https://github.com/scientific-python/spin/pull/56) ([stefanv](https://github.com/stefanv))
- Meson building is now tested on example_pkg, so can remove on spin itself [\#55](https://github.com/scientific-python/spin/pull/55) ([stefanv](https://github.com/stefanv))
- Group meson commands in preparation for other build systems [\#52](https://github.com/scientific-python/spin/pull/52) ([stefanv](https://github.com/stefanv))
- Run `build` before `test` command [\#51](https://github.com/scientific-python/spin/pull/51) ([stefanv](https://github.com/stefanv))
- Add installation instructions [\#49](https://github.com/scientific-python/spin/pull/49) ([stefanv](https://github.com/stefanv))
- Add ability to build sdist [\#48](https://github.com/scientific-python/spin/pull/48) ([stefanv](https://github.com/stefanv))
- Rename build cmd to make room for other build backends [\#47](https://github.com/scientific-python/spin/pull/47) ([stefanv](https://github.com/stefanv))
- Fix Windows builds: use `meson compile` instead of `ninja` [\#43](https://github.com/scientific-python/spin/pull/43) ([stefanv](https://github.com/stefanv))
- DOC: add some hints to build, test [\#42](https://github.com/scientific-python/spin/pull/42) ([mattip](https://github.com/mattip))
- Remove Strawberry GCC compiler in Windows CI [\#41](https://github.com/scientific-python/spin/pull/41) ([stefanv](https://github.com/stefanv))
- Fix Powershell build [\#39](https://github.com/scientific-python/spin/pull/39) ([stefanv](https://github.com/stefanv))
- Update precommits [\#37](https://github.com/scientific-python/spin/pull/37) ([jarrodmillman](https://github.com/jarrodmillman))
- Prefer site-packages paths with Python version [\#35](https://github.com/scientific-python/spin/pull/35) ([stefanv](https://github.com/stefanv))
- Fix support for python 3.7 [\#34](https://github.com/scientific-python/spin/pull/34) ([eli-schwartz](https://github.com/eli-schwartz))
- Revert "Match current Python version for site-packages \(\#29\)" [\#33](https://github.com/scientific-python/spin/pull/33) ([jarrodmillman](https://github.com/jarrodmillman))
- Run `pytest` as `python -m pytest` [\#30](https://github.com/scientific-python/spin/pull/30) ([stefanv](https://github.com/stefanv))
- Match current Python version when searching for site-packages [\#29](https://github.com/scientific-python/spin/pull/29) ([stefanv](https://github.com/stefanv))
- Do not rely on `project` section of `pyproject.toml` [\#27](https://github.com/scientific-python/spin/pull/27) ([stefanv](https://github.com/stefanv))
- Refactor testing to use an example package, instead of spin itself [\#25](https://github.com/scientific-python/spin/pull/25) ([stefanv](https://github.com/stefanv))
- Update README [\#24](https://github.com/scientific-python/spin/pull/24) ([stefanv](https://github.com/stefanv))
- Add simple color formatter [\#23](https://github.com/scientific-python/spin/pull/23) ([stefanv](https://github.com/stefanv))
- Add command sections [\#22](https://github.com/scientific-python/spin/pull/22) ([stefanv](https://github.com/stefanv))
- Install only changed files [\#18](https://github.com/scientific-python/spin/pull/18) ([stefanv](https://github.com/stefanv))
- Apply cwd argument of run also to execvp [\#17](https://github.com/scientific-python/spin/pull/17) ([stefanv](https://github.com/stefanv))
- Add --clean flag to build command [\#16](https://github.com/scientific-python/spin/pull/16) ([stefanv](https://github.com/stefanv))
- Better errors on missing cmds/broken module/missing module [\#15](https://github.com/scientific-python/spin/pull/15) ([stefanv](https://github.com/stefanv))
- Separate build dir and install dir [\#14](https://github.com/scientific-python/spin/pull/14) ([stefanv](https://github.com/stefanv))
- Use `meson setup` instead of `meson`. The latter is deprecated. [\#11](https://github.com/scientific-python/spin/pull/11) ([rgommers](https://github.com/rgommers))
- Add basic testing [\#9](https://github.com/scientific-python/spin/pull/9) ([stefanv](https://github.com/stefanv))
- Fix PYTHONPATH issue when invoking shell [\#8](https://github.com/scientific-python/spin/pull/8) ([stefanv](https://github.com/stefanv))
- Add module description [\#7](https://github.com/scientific-python/spin/pull/7) ([stefanv](https://github.com/stefanv))
- Add flags to control build output verbosity [\#6](https://github.com/scientific-python/spin/pull/6) ([stefanv](https://github.com/stefanv))
- Flush build cmd, so it gets printed before output [\#5](https://github.com/scientific-python/spin/pull/5) ([stefanv](https://github.com/stefanv))
- Add rationale behind spin [\#4](https://github.com/scientific-python/spin/pull/4) ([stefanv](https://github.com/stefanv))
- Don't use flit [\#3](https://github.com/scientific-python/spin/pull/3) ([jarrodmillman](https://github.com/jarrodmillman))

## [v0.1a1](https://github.com/scientific-python/spin/tree/v0.1a1) (2022-10-14)

[Full Changelog](https://github.com/scientific-python/spin/compare/v0.0...v0.1a1)

**Merged pull requests:**

- Document release process [\#2](https://github.com/scientific-python/spin/pull/2) ([jarrodmillman](https://github.com/jarrodmillman))
- Add pre-commit hooks and CI linter [\#1](https://github.com/scientific-python/spin/pull/1) ([jarrodmillman](https://github.com/jarrodmillman))

\* _This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)_
