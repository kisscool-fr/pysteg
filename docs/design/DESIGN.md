# PySteg UI redesign

This document explains the redesign of the PySteg main window: what was wrong
with the previous layout, the decisions taken, and how they map to the code.

The mockups live in [`canvas/`](canvas/). They are the source files of a Claude
Design canvas (one `.dc.html` file per screen, laid out by `canvas.json`). They
are kept here as the design reference; they need the Design canvas runtime to
render, so open the canvas itself to look at them.

| Board | Screen |
|-------|--------|
| [`Empty.dc.html`](canvas/Empty.dc.html) | First launch, nothing selected |
| [`Main.dc.html`](canvas/Main.dc.html) | Hide, form complete and ready |
| [`HideWarnings.dc.html`](canvas/HideWarnings.dc.html) | Hide, plain text + message too long for the image |
| [`HideDone.dc.html`](canvas/HideDone.dc.html) | Hide, success (drawn in light colours; the app ships dark only) |
| [`Reveal.dc.html`](canvas/Reveal.dc.html) | Reveal, message decrypted |
| [`RevealError.dc.html`](canvas/RevealError.dc.html) | Reveal, wrong shared secret |

## What was wrong

The previous window (see [`docs/main-window-macos.png`](../main-window-macos.png))
stacked widgets in code order rather than task order:

- **The order was backwards.** Text, then secret, then image. But the image
  decides the technique (LSB for PNG/BMP, EXIF for JPEG/TIFF) and how much
  text fits, so the user only learned at the very end that their message was
  too long or that a JPEG would store it in strippable metadata.
- **Plain-text mode was an unlabelled checkbox** next to the secret field,
  explained only by a tooltip, and turning it on opened a blocking modal.
- **Every error was a 2-second status-bar message**, far from the field that
  caused it and easy to miss. The action button was always enabled.
- **Switching Hide ⇄ Reveal silently cleared every field**, including the
  image, although revealing right after hiding is the natural way to check
  the result.
- **No way to check the secret.** No "show" button and no confirmation when
  hiding: one typo makes the message unrecoverable.
- **Emoji icons** (🔐 🔓) render differently on macOS, Windows and Linux.
- **Fixed 318×557 window**, no drag and drop, no copy button for a revealed
  message.

## Decisions

### 1. Image first

The cover image is step 1. An empty drop zone ("Drop an image here" +
*Browse…*) becomes a file card once an image is chosen: thumbnail, file name,
format, dimensions, size and a technique chip (`LSB` / `EXIF`). JPEG/TIFF add a
one-line note that the data lives in the file's metadata, which re-saving or
uploading often strips.

A **capacity meter** under the card shows how much of the image the message
(after encryption) uses, and turns red when it does not fit.

### 2. Numbered steps, one primary action

Hide is four steps: *Cover image → Message → Protection → Save as*. Each step
header carries a number that becomes a check mark when the step is valid, or
an alert mark when it is in error. The primary button is disabled until the
form is valid, and the line under it says what is missing ("Add a cover image
to continue"); when ready it shows the shortcut instead.

Reveal is the same window with the Message and Save-as steps removed and a
result panel added.

### 3. Encryption is an explicit, labelled switch

"Encrypt with a shared secret", on by default, with the algorithm named
underneath (AES-256-GCM · Argon2id). Turning it off shows a persistent amber
warning inside the Protection card instead of a modal. The secret field has a
show/hide toggle and, when hiding, a *Confirm secret* field with a live
"N characters · secrets match" check.

### 4. Errors next to their cause

The status bar is gone. Each problem is shown where it happens: unsupported
image under the image card, message too long under the message, secret too
short or not matching under the secret, wrong secret on reveal under the secret
plus a "Still not working?" panel listing the other likely causes (message not
encrypted, image re-saved by a chat app).

### 5. Clear results

- **Hide** replaces the form with a result page: the output file, *Show in
  folder* (labelled *Show in Finder* / *Show in Explorer* / *Open folder* by
  platform), *Test with Reveal* (switches to Reveal with the new image already
  selected) and *Hide another message*.
- **Reveal** shows the message in a green result panel with *Copy* and
  *Save .txt*.

### 6. Mode switch keeps the image

Hide ⇄ Reveal keeps the selected image and only clears what belongs to the mode
being left (message, secrets, result).

## Visual language

Choices confirmed during review:

- **Dark theme only**, close to the previous Picocrypt-like look. The app stays
  dark whatever the OS colour scheme.
- **A single blue accent** (`#2F6FDB`, white text passes 4.5:1). The mode is
  shown by the segmented control and the button label, not by recolouring the
  window. Green, amber and red are reserved for success, warning and error.
- **Inter, bundled**, so the app looks the same on every OS. The loader picks
  up any `.ttf`/`.otf` in `assets/fonts/` and falls back to the system UI font
  when Inter is not bundled (see *Status* below).

Colour tokens:

| Token | Value | Use |
|-------|-------|-----|
| `window` | `#141518` | window background |
| `panel` | `#1D1F23` | cards |
| `field` | `#25282D` | inputs |
| `raised` | `#2B2F35` | secondary buttons, track |
| `border` | `#3A3E45` | input borders |
| `text` | `#ECEDEE` | body text |
| `muted` | `#A1A5AC` | labels, helper text |
| `accent` | `#2F6FDB` | primary button, switch |
| `success` | `#5FD39A` | checks, revealed panel |
| `warning` | `#F0BE6A` | plain-text warning, EXIF chip |
| `danger` | `#F2907D` | errors, over-capacity |

The layout is compact, in the spirit of Picocrypt: 9 pt text, 10 px window
margins, 8 px card padding, 12 px between sections. Inputs and buttons are
24 px high, the primary action 32 px. Radii are 3 (chips), 5 (inputs and
buttons) and 6 (cards).

## Cross-platform notes

- Qt **Fusion** style everywhere, styled by one stylesheet generated from the
  tokens above, so macOS, Windows and Linux render the same widgets.
- **SVG icons** drawn at runtime with `QSvgRenderer` and tinted per use; the
  outlines follow [Lucide](https://lucide.dev) (ISC licence).
- **Native file dialogs** are kept; drag and drop is added on the image card.
- **Ctrl+Enter** runs the action (Qt maps it to ⌘+Return on macOS).
- The window opens at 340×660, which fits the whole Hide form, and is
  **resizable** down to 320×480; the form scrolls when the window is shorter
  than the content.
- *Show in folder* opens the containing folder through `QDesktopServices`
  (no shell commands), which works on all three platforms.

## Backend changes required by the design

The previous controller could only hide and reveal. The design needs:

- `ActionController.inspect()` → `ImageInfo` (format, technique, dimensions,
  file size, existing EXIF size) without running any steganography, to fill
  the image card and validate the file as soon as it is chosen.
- `app/capacity.py` → how many bytes an image can hold (LSB: three bits per
  prime-indexed pixel, the generator PySteg uses; EXIF: what is left of the
  64 KB APP1 segment) and how many bytes a payload will take, so the meter is
  live without encrypting on every keystroke.
- `payload.estimate_payload()` → a stand-in with the exact length of the real
  encrypted payload, without running Argon2id.
- `InputValidator.validate_confirmation()` → secret and confirmation match.

## Status

Implemented on `feat/improve-design`: everything above.

Not done yet:

- **Inter font files** are not committed; drop `Inter-Regular.ttf`,
  `Inter-Medium.ttf` and `Inter-SemiBold.ttf` (SIL Open Font License, from
  [rsms/inter](https://github.com/rsms/inter/releases)) into `assets/fonts/`
  together with its `LICENSE.txt`.
- Hide/reveal still run on the UI thread (with a busy cursor). A worker thread
  with a progress state would keep large LSB images responsive.
