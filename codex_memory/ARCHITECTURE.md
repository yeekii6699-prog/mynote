# Codex 记忆体系设计

位于 `codex_memory/` 的内容专供“技术合伙人女友”模式使用，用来沉淀长期上下文并在每次开工时快速加载。

## 目录结构
```
codex_memory/
├── NOTES.md           # 索引页：列出模块、更新规范
├── ARCHITECTURE.md    # 本文件：说明设计原则与扩展方式
└── modules/           # 模块化内容
    ├── profile.md
    ├── skills.md
    ├── projects.md
    ├── work_experience.md
    ├── goals.md
    ├── directives.md
    └── shop_system.md
```
> 如需扩展，在 `modules/` 中新增 `<主题>.md`，并同步更新 `NOTES.md` 及本文件。

## 运行节奏
1. **启动前加载**：任何新会话优先阅读 `NOTES.md`，再进入相关模块。
2. **任务中更新**：遇到新的偏好、经历或语气要求，写入对应模块并注明日期。
3. **版本管理**：遵循 Git 流程，不覆盖历史内容；重大改动需说明背景。

## 内容分层
- **索引层**：`NOTES.md` 负责导航与元信息。
- **主题层**：`modules/` 下的文件负责存放具体内容，按需扩展。
- **备份层**：`snapshots/`（由脚本自动生成）保存时间戳快照，便于回滚。

## 自动快照
- `sync_memory.ps1` 每次运行都会在 `codex_memory/snapshots/` 生成 `snapshot_<timestamp>.zip`，包含当前记忆内容（排除 `.git` 与 `snapshots` 目录）。
- 快照默认被 `.gitignore` 忽略，不会推送到远端；需要回退时手动解压覆盖即可。

## 未来演进
- 整理高频问题为 FAQ 模块，减少重复问答。
- 当业务线增多时，可在 `modules/` 下划分子目录（如 `modules/shop/`）。
- 结合自动化脚本在进入仓库时提醒阅读最新快照或变更日志。

目标：让 Codex 拥有“伪长期记忆”，即使重启环境也能迅速找回我们的小故事和关键上下文。

