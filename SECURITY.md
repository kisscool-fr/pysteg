# Security Policy

PySteg handles secrets: shared passphrases, optional encryption, and hidden payloads in images. If you find a vulnerability that could expose or weaken that protection, please report it privately.

## Supported versions

Security fixes are applied to the latest release on `main`. Older tagged releases may not receive backports unless the issue is severe.

| Version | Supported |
|---------|-----------|
| Latest (`main` / current release) | Yes |
| Older releases | Best effort |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Use **[GitHub private vulnerability reporting](https://github.com/kisscool-fr/pysteg/security/advisories/new)**. Reports are delivered privately to maintainers, and follow-up can happen entirely within GitHub — no public email address is required from either side.

Include as much detail as you can:

- A clear description of the issue and its impact
- Steps to reproduce, or a proof of concept if available
- Affected version(s)
- Any suggested fix, if you have one

You should receive an initial response within **7 days**. We will work with you to understand the report, confirm the issue, and coordinate a fix and disclosure timeline.

## Scope

**In scope**

- Weaknesses in AES-256-GCM usage, Argon2id key derivation, nonce/IV handling, or payload encoding
- Bugs that leak secrets, passphrases, or hidden message content through the UI, logs, temp files, or error messages
- Steganography handling that corrupts, truncates, or unexpectedly exposes payloads
- Dependency vulnerabilities with a demonstrated impact on PySteg

**Out of scope**

- General hardening ideas without a concrete exploit path
- Attacks that require full control of the host machine or physical access to an unlocked session
- Limitations inherent to steganography (for example, statistical detection of LSB embedding in images)
- Issues in third-party libraries already tracked upstream, unless they affect PySteg in a demonstrable way

## Security considerations

PySteg is a desktop utility, not a high-assurance cryptographic product. Keep these limitations in mind:

- **Steganography is not encryption.** Hidden data may be detectable by dedicated analysis, especially in plain-text mode.
- **Plain text mode** stores the message without encryption. Use it only for testing or low-risk payloads.
- **Passphrase strength matters.** Short or predictable secrets weaken Argon2id-protected payloads.
- **Cover images may be modified.** Re-saving, compressing, or editing a carrier image can destroy embedded data.

Thank you for helping keep PySteg safer for everyone.
