# Bundled fonts

PySteg loads every `.ttf` / `.otf` file in this folder at startup and uses
**Inter** when it is present, falling back to the system UI font otherwise.

To bundle Inter, copy `Inter-Regular.ttf`, `Inter-Medium.ttf` and
`Inter-SemiBold.ttf` from an [rsms/inter release](https://github.com/rsms/inter/releases)
here, together with its `LICENSE.txt` (SIL Open Font License 1.1).
