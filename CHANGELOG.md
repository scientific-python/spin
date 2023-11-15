# spin 0.8

We're happy to announce the release of spin 0.8!

## Enhancements

- Also support build sanity check on <3.11 ([#124](https://github.com/scientific-python/spin/pull/124)).
- Support .spin.toml/spin.toml as an alternate configuration files ([#129](https://github.com/scientific-python/spin/pull/129)).
- Add --version ([#134](https://github.com/scientific-python/spin/pull/134)).
- Add alias for help ([#135](https://github.com/scientific-python/spin/pull/135)).
- Add LLDB (debug) command ([#137](https://github.com/scientific-python/spin/pull/137)).
- Add pip install with editable mode ([#139](https://github.com/scientific-python/spin/pull/139)).

## Bug Fixes

- Fix unclosed file warning on debug python ([#127](https://github.com/scientific-python/spin/pull/127)).

## Documentation

- Drop mention of old devpy name ([#121](https://github.com/scientific-python/spin/pull/121)).
- [DOC] Add install to readme ([#142](https://github.com/scientific-python/spin/pull/142)).

## Maintenance

- Drop support for Python 3.7 ([#122](https://github.com/scientific-python/spin/pull/122)).
- Use trusted publisher ([#126](https://github.com/scientific-python/spin/pull/126)).
- Bump actions/checkout from 3 to 4 ([#130](https://github.com/scientific-python/spin/pull/130)).
- Bump pre-commit from 3.4.0 to 3.5.0 ([#132](https://github.com/scientific-python/spin/pull/132)).
- Bump changelist from 0.3 to 0.4 ([#131](https://github.com/scientific-python/spin/pull/131)).
- Add nox for running tests in an isolated environment ([#140](https://github.com/scientific-python/spin/pull/140)).

## Other

- Add note on missing emojis to README ([#136](https://github.com/scientific-python/spin/pull/136)).

## Contributors

5 authors added to this release (alphabetically):

- Adam Li ([@adam2392](https://github.com/adam2392))
- Jarrod Millman ([@jarrodmillman](https://github.com/jarrodmillman))
- Lisandro Dalcin ([@dalcinl](https://github.com/dalcinl))
- Nathan Goldbaum ([@ngoldbaum](https://github.com/ngoldbaum))
- Stefan van der Walt ([@stefanv](https://github.com/stefanv))

5 reviewers added to this release (alphabetically):

- Adam Li ([@adam2392](https://github.com/adam2392))
- Brigitta Sipőcz ([@bsipocz](https://github.com/bsipocz))
- Jarrod Millman ([@jarrodmillman](https://github.com/jarrodmillman))
- Lisandro Dalcin ([@dalcinl](https://github.com/dalcinl))
- Stefan van der Walt ([@stefanv](https://github.com/stefanv))

_These lists are automatically generated, and may not be complete or may contain duplicates._

# spin 0.7

We're happy to announce the release of spin 0.7!

## Bug Fixes

- Exit on failed build ([#118](https://github.com/scientific-python/spin/pull/118)).

## Maintenance

- Update ruff ([#119](https://github.com/scientific-python/spin/pull/119)).
- Update changelist ([#120](https://github.com/scientific-python/spin/pull/120)).

## Contributors

2 authors added to this release (alphabetically):

- Jarrod Millman ([@jarrodmillman](https://github.com/jarrodmillman))
- Stefan van der Walt ([@stefanv](https://github.com/stefanv))

1 reviewers added to this release (alphabetically):

- Jarrod Millman ([@jarrodmillman](https://github.com/jarrodmillman))

_These lists are automatically generated, and may not be complete or may contain duplicates._

# spin 0.6

We're happy to announce the release of spin 0.6!

## Enhancements

- ENH: Added coverage option for `test` command
  ([#100](https://github.com/scientific-python/spin/pull/100)).
- Build as part of run cmd
  ([#103](https://github.com/scientific-python/spin/pull/103)).
- Port improvements to test cmd from numpy
  ([#101](https://github.com/scientific-python/spin/pull/101)).
- Add gdb command from numpy
  ([#102](https://github.com/scientific-python/spin/pull/102)).
- Throughout, invoke build before commands
  ([#107](https://github.com/scientific-python/spin/pull/107)).
- Allow disabling Sphinx Gallery plots
  ([#111](https://github.com/scientific-python/spin/pull/111)).
- Make verbose build also show compiler calls
  ([#117](https://github.com/scientific-python/spin/pull/117)).

## Bug Fixes

- Return single path from \_get_site_packages
  ([#114](https://github.com/scientific-python/spin/pull/114)).

## Maintenance

- Bump pre-commit from 3.3.3 to 3.4.0
  ([#104](https://github.com/scientific-python/spin/pull/104)).
- Bump actions/checkout from 3 to 4
  ([#105](https://github.com/scientific-python/spin/pull/105)).
- Update pre-commit revisions
  ([#106](https://github.com/scientific-python/spin/pull/106)).
- Update classifiers
  ([#108](https://github.com/scientific-python/spin/pull/108)).
- Ensure `spin run` echoes only command output to stdout
  ([#109](https://github.com/scientific-python/spin/pull/109)).
- Update supported Python versions
  ([#110](https://github.com/scientific-python/spin/pull/110)).
- Update label check
  ([#112](https://github.com/scientific-python/spin/pull/112)).

## Documentation

- Document alternative way of getting debug build
  ([#115](https://github.com/scientific-python/spin/pull/115)).

## Contributors

4 authors added to this release (alphabetically):
[@dependabot[bot]](https://github.com/apps/dependabot),
Ganesh Kathiresan ([@ganesh-k13](https://github.com/ganesh-k13)),
Jarrod Millman ([@jarrodmillman](https://github.com/jarrodmillman)),
Stefan van der Walt ([@stefanv](https://github.com/stefanv)),

3 reviewers added to this release (alphabetically):
Brigitta Sipőcz ([@bsipocz](https://github.com/bsipocz)),
Jarrod Millman ([@jarrodmillman](https://github.com/jarrodmillman)),
Stefan van der Walt ([@stefanv](https://github.com/stefanv)),

_These lists are automatically generated, and may not be complete or may contain duplicates._

## spin 0.5

We're happy to announce the release of spin 0.5!

### Enhancements

- Allow custom Meson CLI path
  ([#97](https://github.com/scientific-python/spin/pull/97)).

### Bug Fixes

- Correctly highlight parameter names with underscores
  ([#84](https://github.com/scientific-python/spin/pull/84)).

### Maintenance

- Use label-check and attach-next-milestone-action
  ([#85](https://github.com/scientific-python/spin/pull/85)).
- Use changelist
  ([#86](https://github.com/scientific-python/spin/pull/86)).
- Use dependabot
  ([#88](https://github.com/scientific-python/spin/pull/88)).
- Bump pre-commit from 3.3 to 3.3.3
  ([#89](https://github.com/scientific-python/spin/pull/89)).
- DEP: migrate from toml package to tomllib
  ([#93](https://github.com/scientific-python/spin/pull/93)).
- Bump scientific-python/attach-next-milestone-action from f94a5235518d4d34911c41e19d780b8e79d42238 to bc07be829f693829263e57d5e8489f4e57d3d420
  ([#96](https://github.com/scientific-python/spin/pull/96)).
- Update pre-commit revisions
  ([#99](https://github.com/scientific-python/spin/pull/99)).

### Documentation

- Improve release process
  ([#87](https://github.com/scientific-python/spin/pull/87)).
- Add readme to pyproject
  ([#91](https://github.com/scientific-python/spin/pull/91)).
- Suggest setting meson buildtype for a debug build
  ([#92](https://github.com/scientific-python/spin/pull/92)).
- Document command wrapping
  ([#94](https://github.com/scientific-python/spin/pull/94)).

### Contributors

5 authors added to this release (alphabetically):
[@dependabot[bot]](https://github.com/apps/dependabot),
Clément Robert ([@neutrinoceros](https://github.com/neutrinoceros)),
Jarrod Millman ([@jarrodmillman](https://github.com/jarrodmillman)),
Nathan Goldbaum ([@ngoldbaum](https://github.com/ngoldbaum)),
Stefan van der Walt ([@stefanv](https://github.com/stefanv)),

2 reviewers added to this release (alphabetically):
Jarrod Millman ([@jarrodmillman](https://github.com/jarrodmillman)),
Stefan van der Walt ([@stefanv](https://github.com/stefanv)),

_These lists are automatically generated, and may not be complete or may contain duplicates._

## [v0.4](https://github.com/scientific-python/spin/tree/v0.4) (2023-7-1)

[Full Changelog](https://github.com/scientific-python/spin/compare/v0.3...v0.4)

**Closed issues:**

- `spin test` usage in numpy is broken [\#74](https://github.com/scientific-python/spin/issues/74)
- How can I override the `build` command? [\#72](https://github.com/scientific-python/spin/issues/72)
- Run a command in the shell without invoking the shell [\#69](https://github.com/scientific-python/spin/issues/69)
- DEV: Can `pydevtool.cli` be used to create a unified context? [\#45](https://github.com/scientific-python/spin/issues/45)

**Merged pull requests:**

- Fix rendering of `test` docs [\#83](https://github.com/scientific-python/spin/pull/83) ([stefanv](https://github.com/stefanv))
- Add @WarrenWeckesser's test primer as docstring [\#82](https://github.com/scientific-python/spin/pull/82) ([stefanv](https://github.com/stefanv))
- Use ruff [\#81](https://github.com/scientific-python/spin/pull/81) ([jarrodmillman](https://github.com/jarrodmillman))
- Docs cmd ci [\#80](https://github.com/scientific-python/spin/pull/80) ([stefanv](https://github.com/stefanv))
- Add docs to CI tests [\#79](https://github.com/scientific-python/spin/pull/79) ([stefanv](https://github.com/stefanv))
- Add command to build Sphinx docs [\#78](https://github.com/scientific-python/spin/pull/78) ([stefanv](https://github.com/stefanv))
- Import importlib.util explicitly [\#76](https://github.com/scientific-python/spin/pull/76) ([stefanv](https://github.com/stefanv))
- As a build check, import the library before running tests [\#75](https://github.com/scientific-python/spin/pull/75) ([stefanv](https://github.com/stefanv))
- Test on Python 3.12.0-beta.2 [\#73](https://github.com/scientific-python/spin/pull/73) ([jarrodmillman](https://github.com/jarrodmillman))
- Add meson.run command [\#70](https://github.com/scientific-python/spin/pull/70) ([stefanv](https://github.com/stefanv))

## [v0.3](https://github.com/scientific-python/spin/tree/v0.3) (2023-3-23)

[Full Changelog](https://github.com/scientific-python/spin/compare/v0.2...v0.3)

**Merged pull requests:**

- Update pre-commit [\#68](https://github.com/scientific-python/spin/pull/68) ([jarrodmillman](https://github.com/jarrodmillman))
- Cleanup from rename [\#67](https://github.com/scientific-python/spin/pull/67) ([jarrodmillman](https://github.com/jarrodmillman))
- Launch `spin` via a setuptools script/entrypoint [\#66](https://github.com/scientific-python/spin/pull/66) ([stefanv](https://github.com/stefanv))

## [v0.2](https://github.com/scientific-python/spin/tree/v0.2) (2023-3-17)

[Full Changelog](https://github.com/scientific-python/spin/compare/v0.1...v0.2)

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
