# Third-party notices

The root MIT license remains unchanged. It covers the project's theme configurations and original contributions, subject to the third-party licenses below.

## Streamlit demo examples

The eleven Python modules in each of the ten original theme directories are adapted from Streamlit's [Anthropic-inspired theming example](https://github.com/streamlit/docs/tree/main/python/concept-source/theming-overview-anthropic-light-inspried). Copyright Streamlit Inc.; licensed under the Apache License, Version 2.0. The complete upstream license is included in [licenses/Apache-2.0.txt](licenses/Apache-2.0.txt).

The repository's original attribution remains in README.md and LICENSE. The original theme configurations and bundled fonts are this project's additions to the example. No example source was changed during the Studio baseline audit. Upstream `streamlit/docs` at commit `85301cc403f564127ad66097b3e66156a21268c0` contains no root NOTICE file.

## Fonts

All 62 bundled font files identify the SIL Open Font License, Version 1.1 in their metadata. Original font binaries and their accompanying notices remain untouched in the ten theme directories. Verified upstream OFL texts for all fourteen families are additionally included under [licenses/fonts](licenses/fonts/). [FONT_NOTICES.md](licenses/FONT_NOTICES.md) preserves copyright metadata from the actual bundled binaries, including versions whose dates differ from older accompanying notices.

For future Studio packages, include the applicable OFL texts, the bundled fonts' copyright notices, and the original notices. Do not treat the root MIT license as the font license. No font modification or relicensing is intended.
