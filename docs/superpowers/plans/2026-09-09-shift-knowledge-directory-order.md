# 知识库目录序号后移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 A–P 知识库目录改为 E–T，保留 Z 类目录。

**Architecture:** 先用临时目录避免命名冲突，再移动至最终目录，接着在现行 Markdown 链接目标中替换目录组件。

- [ ] 将 `A`–`P` 依次临时改名并移至 `E`–`T`。
- [ ] 更新非 `docs/superpowers/` Markdown 和本地 Obsidian 工作区中的 A–P 路径。
- [ ] 验证 E–T 目录及知识库内相对链接，审查差异并提交；不暂存既有用户配置改动。
