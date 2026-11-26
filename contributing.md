# Contributing

[中文文档](contributing.zh-cn.md) · [Project Guide](readme.md)

Before working on OmniSuite, check open issues and coordinate overlapping changes. Issues and pull requests accept English or Simplified Chinese.

Use the [bug report outline](.github/issue_template/bug_report.md) to [open a bug report](https://github.com/AMFI-Disable/OmniSuite/issues/new?title=%5BBUG%5D%20).

## Verification

Install the development dependencies listed in the README. Exercise the affected entry point using a disposable database, then run the shared package tests and lint checks.

```sh
ruff check .
ruff format --check .
EVIDENCE_VAULT_DB=:memory: pytest --tb=short -q
```

## Preparing A Pull Request

Describe the observable change, link related issues and include test results. Keep commit messages in the form `type: three lowercase words`. Record changes under Unreleased. Release tags use `vMAJOR.MINOR.PATCH` after verification.
