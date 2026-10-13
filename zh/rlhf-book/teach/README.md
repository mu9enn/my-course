# 教学幻灯片

RLHF Book 的教学幻灯片，使用 [colloquium](https://github.com/natolambert/colloquium) 构建。

Colloquium 目前仍在积极开发中——随着内容演进，幻灯片工具链也会持续改进。

## 讲座集

- **`course/`** — 基于本书发布的入门课程，包含讲座（lecture）、问答（Q&A）和讨论（conversation）幻灯片集（[课程页面](https://rlhfbook.com/course)）
- **`SALA-2026/`** — 2026 年 3 月在 SALA 会议上发表的演示文稿

## 安装

从仓库根目录执行以下命令（通过 `teach` extra 从 GitHub 拉取 `colloquium`）：

```bash
uv sync --extra teach
```

`teach` extra 特意跟踪 GitHub 源码，因为 `colloquium` 本身更新很快。直接运行幻灯片相关命令时，请使用 `uv run --extra teach ...`，这样即使在全新环境中也能正确使用 `colloquium`。

或者，使用本地克隆进行开发：

```bash
uv pip install -e /path/to/colloquium
```

## 构建

从仓库根目录执行：

```bash
make teach
```

也可以仅构建单份讲座幻灯片：

```bash
uv run --extra teach colloquium build teach/course/lec1-chap1-3.md -o build/html/teach/course/lec1-chap1-3/
```

输出会写入 `build/html/teach/`。

## 实时预览

对于课程讲座，请将生成的 HTML 保留在 `teach/course/` 中，以使 `assets/...` 图片链接正确解析：

```bash
uv run --extra teach python -c "from colloquium.serve import serve; serve('teach/course/lec5-chap7.md', port=8081, output_dir='teach/course')"
```

然后访问 `http://localhost:8081/lec5-chap7.html`。

对于包含本地素材的独立演示文稿，请从对应演示文稿目录运行：

```bash
cd teach/SALA-2026
uv run --extra teach colloquium serve talk.md
```

在分享预览链接之前，请至少确认一个预期的图片 URL 能正常返回 `200 image/...`。

## 演示素材

每个演示文稿将其图片保存在本地的 `assets/` 目录中（例如 `teach/SALA-2026/assets/`）。在幻灯片中通过相对路径引用：

```markdown
![description](assets/image.png)
```
