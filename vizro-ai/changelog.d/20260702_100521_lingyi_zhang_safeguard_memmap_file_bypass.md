<!--
A new scriv changelog fragment.

Uncomment the section that is right (remove the HTML comment wrapper).
-->

<!--
### Highlights ✨

- A bullet item for the Highlights ✨ category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Removed

- A bullet item for the Removed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Added

- A bullet item for the Added category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Changed

- A bullet item for the Changed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Deprecated

- A bullet item for the Deprecated category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->

### Fixed

- Closed a dynamic-code safeguard bypass where whitelisted-package methods that reach the filesystem (`numpy.memmap`, `numpy.fromfile`, `numpy.save`) could be used for arbitrary file read/write. Thanks to b3rt1ng ([@b3rt1ng](https://github.com/b3rt1ng)) for the responsible disclosure. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))
- Surfaced the code-execution safeguard's best-effort nature at the API: executing generated chart code now emits a `VizroAICodeExecutionWarning`, and the relevant public docstrings carry an explicit security note. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))
