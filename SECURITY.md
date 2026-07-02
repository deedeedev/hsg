# Security Policy

## Supported versions

Only the latest release is supported with security updates.

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email the maintainer directly at `davide@example.com` (replace with
real address). Include:

- A description of the vulnerability
- Steps to reproduce
- The affected version (`hsg --version` or git commit hash)
- Your assessment of the impact

You will receive an acknowledgement within 72 hours. If the vulnerability is
confirmed, a fix will be prioritised and a GitHub Security Advisory published.

## Scope

- The `hsg` Python package and its CLI.
- The bundled corpora in `assets/` are **out of scope** — they are
  third-party data files; report issues to their respective upstream
  maintainers.
- The `scripts/` directory is **out of scope** — standalone utilities not
  installed with the package.
