# Security Policy

## Supported Versions

This project is currently maintained from the `main` branch. Security fixes are
shipped to the latest released version and to the active Docker deployment flow.

| Version | Supported |
| ------- | --------- |
| Latest release / `main` | Yes |
| Older releases | No |

## Reporting a Vulnerability

Please do not report security issues through public GitHub issues.

Report a vulnerability using GitHub Security Advisories for this repository:

https://github.com/princeofscale/telegram-marketplace-bot/security/advisories/new

If the advisory form is unavailable, contact the maintainer privately through the
support contact listed in the project configuration.

When reporting a vulnerability, include:

- A clear description of the issue.
- Steps to reproduce it.
- The affected component, endpoint, command, or bot flow.
- The potential impact.
- Any relevant logs, screenshots, or proof-of-concept details.

## Response Expectations

We aim to acknowledge valid reports within 72 hours. After triage, we will
either accept the report, ask for more information, or explain why it is not
considered a security vulnerability.

Accepted vulnerabilities are fixed privately first, then released with an
appropriate changelog or advisory once a safe fix is available.

## Scope

Security reports are especially useful for issues involving:

- Telegram bot authentication or admin access control.
- Payment, wallet, balance, order, or delivery logic.
- Provider API tokens, secret handling, and environment configuration.
- Database access, migrations, backups, or user data exposure.
- Docker, CI/CD, GitHub Actions, or deployment misconfiguration.

Out-of-scope reports include:

- Social engineering.
- Denial-of-service without a practical exploit path.
- Reports that require access to leaked credentials without showing a project
  vulnerability.
- Automated scanner output without a reproducible security impact.

## Secret Handling

Never include real bot tokens, provider tokens, payment credentials, database
passwords, or production `.env` values in reports, issues, pull requests, or
logs. If a secret was exposed, revoke and rotate it immediately.
