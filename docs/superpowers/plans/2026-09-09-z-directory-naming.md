# Z 类目录命名实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将模板和资源目录改为 Z 前缀，并保持现行引用与 Obsidian 设置有效。

**Architecture:** 使用 Git 重命名两个目录；在非 `docs/superpowers/` Markdown 文件中替换目录引用；更新 Obsidian 的模板和附件配置。

**Tech Stack:** Git、Python 3、JSON、Markdown。

- [ ] `git mv 90-Templates Z-模板` 和 `git mv 99-Assets Z-资源`。
- [ ] 在现行 Markdown 中将 `90-Templates` / `99-Assets` 替换为 `Z-模板` / `Z-资源`，保留历史过程记录不变。
- [ ] 将 `.obsidian/templates.json` 的 `folder` 改为 `Z-模板`；将 `.obsidian/app.json` 的 `attachmentFolderPath` 改为 `Z-资源`，不暂存后者的用户既有改动；更新 workspace 中的模板路径。
- [ ] 检查相关 Markdown 相对链接存在、JSON 有效，且提交不含用户已有 `.gitignore` / `.obsidian` 改动。
