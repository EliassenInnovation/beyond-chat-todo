# Security policy

## Reporting a vulnerability

Please report a suspected vulnerability privately. Do not open a public issue or pull request.

Use GitHub's private vulnerability reporting: open the repository's **Security** tab and choose
**Report a vulnerability**
([direct link](https://github.com/EliassenInnovation/beyond-chat-todo/security/advisories/new)).
Only the maintainers can see the report.

Please include what you found, the files or commands involved, the steps to reproduce it, and
what you think an attacker could do with it. Do not include real credentials, personal data
or live customer information; redact them.

We will acknowledge the report, tell you whether we consider it a vulnerability, and keep you
informed while we fix it. If you want credit, say how you would like to be named once a fix
is published.

## Supported versions

This is a teaching sample with no releases. Only the latest commit on `main` is supported.

## Scope

In scope: the sample's own code and tooling in this repository, such as leaked or logged
credentials, unsafe handling of files or input, an agent action that bypasses the
application's permission or approval checks, or tests and tools that send data somewhere
unintended.

Out of scope: hardening for your own application. The guide's practices address agent
behavior and do not make an application secure; authentication, authorization, encryption and
transport security need separate design and review under your organization's security policies.
The sample is a local, single-user application and is not a production architecture. Reports
about third-party packages should go to those projects.

Never commit your `.env` file, API keys, `todos.json` or run records from `runs/`; Git ignores them by default.
