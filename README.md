# CodeSense AI 🧠🔍
**AI-powered code review assistant** for GitHub pull requests. Combines static analysis (SonarQube) with **LangChain RAG + GPT** to post actionable review comments, spot bugs/security issues, and suggest refactors—right inside your PR.

[![CI](https://img.shields.io/github/actions/workflow/status/your-org/codesense-ai/ci.yml?label=CI)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Made with FastAPI](https://img.shields.io/badge/backend-FastAPI-blue)]()
[![LangChain](https://img.shields.io/badge/AI-LangChain-purple)]()
[![Dockerized](https://img.shields.io/badge/Container-Docker-informational)]()

---

## ✨ Features
- **PR-native reviews**: Adds inline comments + a summary check on every PR.
- **Hybrid analysis**: Merges **SonarQube** findings with **LLM** reasoning to reduce false positives.
- **Project-aware RAG**: Pulls repo docs (e.g., `/docs`, `CONTRIBUTING.md`, coding standards) into context.
- **Security & quality**: Flags secrets, unsafe patterns, N+1 queries, error handling gaps, and missing tests.
- **Dashboard**: React UI to visualize review results, trends, and fix rates.

---

## 🧱 Architecture
- **Frontend**: React (TS). Dashboard for insights, rule toggles, and feedback loop.
- **Backend**: FastAPI + LangChain. Orchestrates RAG, SonarQube, and GitHub.
- **RAG Store**: Postgres (pgvector) or simple embeddings table for repo knowledge.
- **Static Analysis**: SonarQube (local or hosted).
- **CI**: GitHub Actions workflow triggers on `pull_request`.

