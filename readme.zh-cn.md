# OmniSuite

[English](readme.md) · [贡献指南](contributing.zh-cn.md) · [更新日志](changelog.md) · [安全政策](security.md)

[![Website: Live](https://img.shields.io/badge/Website-Live-FBC02D.svg?style=flat-square)](https://amfi-disable.github.io/OmniSuite/)
[![Platform: macOS & Linux](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-blue.svg?style=flat-square&logo=linux)](https://linux.org)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python)](https://python.org)
[![Status: Active](https://img.shields.io/badge/Status-Active-success.svg?style=flat-square)](https://github.com/AMFI-Disable/OmniSuite)
[![Release: v1.0.0](https://img.shields.io/badge/Release-v1.0.0-blue.svg?style=flat-square&logo=github)](https://github.com/AMFI-Disable/OmniSuite/releases)
[![CI](https://github.com/AMFI-Disable/OmniSuite/actions/workflows/ci.yml/badge.svg)](https://github.com/AMFI-Disable/OmniSuite/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](license)
[![Privacy: Local Storage](https://img.shields.io/badge/Privacy-100%25%20Local%20SQLite-purple.svg?style=flat-square)](#可选的本机-ai)

## 星标历史

<a href="https://www.star-history.com/?type=date&repos=amfi-disable%2Fomnisuite">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=amfi-disable%2Fomnisuite&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=amfi-disable%2Fomnisuite&type=date&legend=top-left" />
    <img alt="AMFI-Disable/OmniSuite Star History Chart" src="https://api.star-history.com/chart?repos=amfi-disable%2Fomnisuite&type=date&legend=top-left" />
  </picture>
</a>

## 安装与启动

OmniSuite 是用于辩论研究和文稿编排的终端工作台，支持 Python 3.10 及以上版本。建议在虚拟环境中从源码安装：

```bash
git clone https://github.com/AMFI-Disable/OmniSuite.git
cd OmniSuite
python3 -m venv .venv
source .venv/bin/activate
pip install -e . -e src/omnishared -e src/omnidebate -e src/omniformat
omnisuite --app debate
```

用 `omnisuite --app format` 打开排版工作台。如需在新终端中用 `omnidebate` 和 `omniformat` 启动，可在源码目录运行 `python3 ./omnisuite --install-aliases`，该操作会向 `~/.zshrc` 和 `~/.bashrc` 写入快捷命令。

## 研究与排版

- **OmniDebate** 将证据卡存入 SQLite，支持 FTS5 全文检索、布尔查询和模糊匹配。可按轮次跟踪论点、展开论证树、使用比赛计时器，以及通过间隔复习和朗读练习巩固素材。
- **分析与导出** 包括论点影响、冲突与关联等维度的评估，研究进度与辩题统计，以及 Word、Markdown、HTML、CSV 和 JSON 等导出格式。
- **OmniFormat** 使用共享的证据库整理文稿，支持 Verbatim 和 CaseXC 格式。

## 可选的本机 AI

Ollama 可以在本机使用模型，为证据卡生成摘要、推演反驳、分析影响链、发现证据缺口，或草拟提纲与质询问题。先启动 Ollama 服务（已运行时可跳过），再在另一个终端下载模型：

```bash
ollama serve
```

```bash
ollama pull llama3
```

证据卡、论点和文稿元数据保存在本机 SQLite 数据库中。

## 界面与赛制

按 `F5` 打开设置，可选择 Cyber Dark、Light、Nord 或 Solarized 主题。支持 Public Forum、Lincoln-Douglas、Policy、英国议会制、世界中学生辩论赛制、亚洲议会制、加拿大国家赛制、欧洲议会制和 Karl Popper 赛制。按赛制使用计时器，可在回合内跟踪发言和质询。

## Docker 与测试

```bash
docker compose up -d
docker compose run --rm omnisuite --app debate
```

在上述开发环境中运行：

```bash
pip install ruff pytest pytest-asyncio
pytest --tb=short -q
ruff check .
ruff format --check .
```

## 许可

本项目采用 [MIT 许可证](license)。
