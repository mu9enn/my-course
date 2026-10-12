# 汉化 Agent

一个文档文件对应一个独立 Claude Code 会话。统一使用 `Qwen3.6-35B-A3B-FP8`。
模型通过 Read / Edit 读取英文、制作完整中文教学版本，再在同一会话自查。脚本只做逐文件调度和断点记录，不解析模型输出，也不拆分文档。

## 运行

```bash
git clone --recurse-submodules https://github.com/mu9enn/my-course.git
cd my-course
cp agent/secrets.example.json agent/secrets.local.json
# 填入自己的 PJLab API Key；确保已经安装 Claude Code
python3 agent/translate.py init
python3 agent/translate.py run --book rlhf-book --all
python3 agent/translate.py status
```

本地已有原文和中文工作目录时，`init` 不覆盖内容；只有缺少工作副本时才复制。
默认 Claude Code 路径为 `~/.local/bin/claude`，其他安装路径修改 `config.json`。
Python 3 标准库即可，无第三方 Python 依赖。CLI 配置与本机全局 Claude / cc-switch 配置隔离。

## 需要维护的内容

- [PROMPT.md](PROMPT.md)：教学风格、完整性和操作边界，是核心。
- [TERMS.md](TERMS.md)：共用术语和课程术语。
- [config.json](config.json)：模型、文档范围、超时和输出上限。
- [sources.lock.json](sources.lock.json)：上游提交版本，与 submodule 一致。
- `secrets.local.json`：本机密钥，不提交。
- `progress.json` 和 `logs/`：本机运行状态与文本日志，不提交。

```bash
# 指定文件；glob 需加引号
python3 agent/translate.py run --book rlhf-book --file 'book/chapters/05-reward-models.md'
# 下一批 5 篇
python3 agent/translate.py run --book rlhf-book --limit 5
# 明确重做并覆盖
python3 agent/translate.py run --book rlhf-book --file 'book/chapters/05-reward-models.md' --force
```

每篇会话内部可以多次调用模型和工具。批次按顺序执行，不自动重试；有运行锁防止重复启动。
中断后重跑会跳过已经完成的文档；失败后留下部分内容时，先查看日志，再指定 `--force` 重做。
在新的克隆中，已不同于原文的文件会被保护而跳过；需要重做时也使用 `--force`。
当前 CLI 的 Edit 同时支持创建和修改文件；新文件用空 old_string 和完整 new_string 写入。
当前版本没有 Write 工具。少数讲解聊天模板的文档包含模型控制 token，直接重新生成代码可能导致输出截断；这些文件在 config.json 的 edit_in_place 中列出，沿用完整原稿，只让模型在同一个会话修改代码块外的文字，不让模型重新输出这些代码。普通文档则直接生成完整中文新文件。旧目标会在本地日志目录备份，不提交。
单篇超时 900 秒，最大输出 32000 tokens。过长文档是否完整，仍需人工确认。

“完成”只表示 Claude 正常退出并写入了不同于原文的内容，不代表已经独立审核或验证所有技术结论。
原始仓库只读参考。示例代码仅作为教学内容读取，不运行训练、安装或课程中的命令。
修改 prompt 后，先挑一篇试跑并人工看样稿，再批量执行。

## 无人值守批次

```bash
mkdir -p agent/logs
nohup bash agent/run.sh > agent/logs/batch.log 2>&1 &
```

生成结束后自动更新公开进度并提交、推送到当前 origin/main。部分失败也会如实记录，不会宣称全部完成。`--finish-current` 仅等待已在运行的批次，然后更新进度和推送，不重复启动模型。运行日志和旧目标备份都留在本机。
安全读取范围基于已固定的英文提交；更新 submodule 时需同步检查这些本篇 prompt 的行号。
