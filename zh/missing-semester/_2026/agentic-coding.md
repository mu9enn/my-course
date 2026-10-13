---
layout: lecture
title: "智能体编程"
description: >
  学习如何有效地使用 AI 编程智能体来执行软件开发任务。
thumbnail: /static/assets/thumbnails/2026/lec7.png
date: 2026-01-21
ready: true
video:
  aspect: 56.25
  id: sTdz6PZoAnw
---

编程智能体（Coding Agents）是与工具相连的对话式 AI 模型，工具包括读写文件、网页搜索以及调用 shell 命令。它们可以运行在 IDE 内，也可以作为独立的命令行或 GUI 工具存在。编程智能体是高度自治且功能强大的工具，能够胜任多种用途。

本节课程建立在 [开发环境与工具](/2026/development-environment/) 讲座中的 AI 辅助开发内容之上。作为快速演示，我们继续使用 [AI 辅助开发](/2026/development-environment/#ai-powered-development) 部分中的示例：

```python
from urllib.request import urlopen

def download_contents(url: str) -> str:
    with urlopen(url) as response:
        return response.read().decode('utf-8')

def extract(content: str) -> list[str]:
    import re
    pattern = r'\[.*?\]\((.*?)\)'
    return re.findall(pattern, content)

print(extract(download_contents("https://raw.githubusercontent.com/missing-semester/missing-semester/refs/heads/master/_2026/development-environment.md")))
```

我们可以用一个编程智能体来尝试完成以下任务：

```
把它改成一个规范的命令行程序，使用 argparse 进行参数解析。添加类型注解，并确保程序能通过类型检查。
```

智能体会读取文件以理解其内容，然后进行一些编辑，最后调用类型检查器来确保类型注解正确。如果它犯了导致类型检查失败的错误，它会自行迭代修正 —— 当然，这是一个很简单的任务，所以不太可能出现这种情况。由于编程智能体所访问的工具可能造成有害影响，默认的"智能体编排器"（agent harness）会在执行工具调用前提示用户确认。

> 如果编程智能体犯了错误 —— 例如，如果你的 `$PATH` 中直接有 `mypy` 可执行文件，但智能体尝试调用 `python -m mypy` —— 你可以给它提供文本反馈，帮助它自我纠正。

编程智能体支持多轮交互，因此你可以通过来回对话的方式与智能体迭代完成工作。如果它走错了方向，你甚至可以打断它。一个有用的思维模型是：把智能体想象成一个实习生的管理者 —— 实习生会做那些繁琐的底层工作，但需要指导，而且偶尔会做错事，需要被纠正。

> 想做一个更直观的演示：尝试让智能体在得到上一轮的产物之后运行生成的脚本。观察输出，然后尝试要求它做出修改（例如，要求它只提取绝对 URL）。

# AI 模型与智能体是如何工作的

完整解释现代 [大语言模型（LLM）](https://en.wikipedia.org/wiki/Large_language_model) 的内部工作机制以及智能体编排器等基础设施超出了本课程的范畴。但是，对其中一些关键思想有一个高层次的理解，有助于你有效地 _使用_ 这项前沿技术并理解其局限性。

LLM 可以被看作是在给定 prompt 字符串（输入）时对 completion 字符串（输出）的概率分布进行建模。LLM 推理（即当你向对话式聊天应用输入一个查询时会发生什么）从该概率分布中进行 _采样_ 。LLM 有一个固定的 _上下文窗口_（context window），即输入和输出字符串的最大长度。

{% comment %}
数学符号描述：LLM 对条件于 prompt $x$ 的 completion $y$ 的概率分布 $\pi_\theta$ 建模，我们对该分布进行采样：$\hat{y} \sim \pi_\theta(\cdot \mid x)$。
{% endcomment %}

对话式聊天和编程智能体等 AI 工具构建在这一基本原语之上。对于多轮交互，聊天应用和智能体会使用"轮次标记"（turn markers），并在每次出现新的用户 prompt 时，将整个对话历史作为 prompt 字符串送入模型，每次用户 prompt 触发一次 LLM 推理。对于具备工具调用能力的智能体，编排器会将某些 LLM 的输出解释为调用工具的请求，并将工具调用的结果作为 prompt 字符串的一部分返回给模型（因此每次发生工具调用/响应时，LLM 推理都会再次运行）。工具调用智能体的核心概念 [可以在 200 行代码中实现](https://www.mihaileric.com/The-Emperor-Has-No-Clothes/)。

## 隐私

大多数 AI 编程工具在标准配置下会将大量你的数据发送到云端。有时编排器在本地运行而 LLM 推理在云端运行，有时甚至软件的大部分都在云端运行（例如，服务提供商可能会有效地获得你整个代码库的副本以及你与 AI 工具的所有交互记录）。

存在一些开源的 AI 编程工具和开源 LLM，它们的效果相当不错（虽然还略逊于专有模型），但在目前，对于大多数用户来说，由于硬件限制，在本地运行前沿的开源 LLM 是不可行的。

# 使用场景

编程智能体可以协助完成多种多样的任务。以下是一些例子：

- **实现新功能**。如同上面的示例，你可以要求编程智能体实现一个功能。在当前阶段，给出一个"好的"规格说明（specification）更像是一门艺术而非科学；你需要让输入对智能体来说描述得足够充分，使其至少朝着你想要的方向前进以便你迭代，但又不能过度描述，否则你就要自己做太多工作了。测试驱动开发（TDD）可能特别有效：编写测试（或使用编程智能体帮你写测试），审查测试以确保它们正确地捕捉了你的需求，然后要求编程智能体实现该功能。模型的持续改进意味着你需要不断更新自己的直觉，以了解模型的能力边界。
    > 我们使用 Claude Code [实现了](https://github.com/missing-semester/missing-semester/pull/345) 这种 Tufte 风格的侧注。
{%- comment %}
无需为此演示，因为讲座引言已经用小演示展示了添加新功能的流程。
{% endcomment %}
- **修复错误**。如果你从编译器、linter、类型检查器或测试中得到了错误信息，你可以要求智能体进行修正，例如使用类似"修复 mypy 中的问题"的提示。编程模型在能让你把它们放在一个反馈循环（feedback loop）中的场景下特别有效 —— 尽量设置好让模型可以直接运行失败的检查，这样它就可以自主迭代。如果这样做不切实际，你可以手动给模型提供反馈。
    > 在 missing-semester 仓库的 [f552b55 提交](https://github.com/missing-semester/missing-semester/commit/f552b5523462b22b8893a8404d2110c4e59613dd) 中，我们用 "Review the agentic coding lecture for typos and grammatical issues" 向 Claude Code 发出提示，随后要求它修复发现的问题，这些问题在 [f1e1c41 提交](https://github.com/missing-semester/missing-semester/commit/f1e1c417adba6b4149f7eef91ff5624de40dc637) 中被提交。
{%- comment %}
演示一个编程智能体修复 https://github.com/anishathalye/dotbot/commit/cef40c902ef0f52f484153413142b5154bbc5e99 中的 bug。

编写失败的测试以演示 bug，然后要求智能体修复。已在分支 demo-bugfix 中准备。

可以用以下命令运行失败的测试：

    hatch test tests/test_cli.py::test_issue_357

可以用以下提示调用编程智能体：

    有一个 bug，我写了一个失败的测试，你可以用 `hatch test tests/test_cli.py::test_issue_357` 复现。修复它。

让它提交更改。
{% endcomment %}
- **重构**。你可以使用编程智能体以多种方式进行代码重构，从简单的任务（如重命名一个方法 —— 这类重构也由 [代码智能](/2026/development-environment/#code-intelligence-and-language-servers) 支持）到更复杂的任务（如将功能拆分到独立的模块中）。
    > 我们使用 Claude Code [将](https://github.com/missing-semester/missing-semester/pull/344) 智能体编程拆分为一个独立的讲座。
{%- comment %}
在 Missing Semester 仓库中演示用法，指出智能体确实犯过一些错误。
{% endcomment %}
- **代码审查**。你可以要求编程智能体进行代码审查。你可以给它们基本的指导，例如"审查我最新但未提交的更改"。如果你想审查一个 pull request，且你的编程智能体支持网页抓取，或者你安装了 [GitHub CLI](https://cli.github.com/) 等命令行工具，你甚至可以直接要求智能体 "Review the pull request {link}"，让它自行处理后续工作。
{%- comment %}
在 Porcupine 仓库中，用以下提示调用智能体：

    Review this PR: https://github.com/anishathalye/porcupine/pull/39
{% endcomment %}
- **代码理解**。你可以向编程智能体提出关于代码库的问题，这在帮助新成员上手（onboarding）时特别有用。
{%- comment %}
在 missing-semester 仓库中尝试的一些提示：

    How do I run this site locally?

    How are the social preview cards implemented?
{% endcomment %}
- **当作 shell 使用**。你可以要求编程智能体使用某个特定工具来完成一个任务，因此你可以用自然语言来调用 shell 命令，例如"使用 find 命令查找所有超过 30 天的文件"或"使用 mogrify 将所有 jpg 缩放到原始大小的 50%"。
{%- comment %}
在 Dotbot 仓库中，用以下提示调用智能体：

    Use the ag command to find all Python renaming imports
{% endcomment %}
- **Vibe Coding**。智能体足够强大，以至于你可以在不手写一行代码的情况下实现一些应用程序。
    > 这是一个 [实际项目的例子](https://github.com/cleanlab/office-presence-dashboard)，其中一位讲师通过 vibe coding 完成了该项目。
{%- comment %}
在 missing-semester 仓库中，用以下提示调用智能体：

    Make this site look retro.
{% endcomment %}

# 高级智能体

这里我们简要概述编程智能体的一些更高级的使用模式和能力。

- **可复用的提示（Reusable prompts）**。创建可复用的提示或模板。例如，你可以写一个详细的提示来以特定方式执行代码审查，并将其保存为可复用提示。
    > 智能体工具的发展很快。在某些工具中，"可复用提示"作为一个独立的功能已被弃用。例如，在 Codex 和 Claude Code 中，它们被 [合并](https://developers.openai.com/codex/custom-prompts) 为 [skills](https://code.claude.com/docs/en/skills)。
- **并行智能体**。编程智能体可能运行缓慢：你可以给智能体发出提示，然后它可以在一个问题上工作几十分钟。你可以同时运行多个智能体副本，要么执行相同的任务（LLM 是随机性的，所以多次运行相同任务并取最佳结果是有帮助的），要么执行不同的任务（例如，同时实现两个不重叠的功能）。为了避免不同智能体的更改相互干扰，你可以使用 [git worktrees](https://git-scm.com/docs/git-worktree)，我们在 [版本控制](/2026/version-control/) 讲座中对此做过介绍。
- **MCP**。MCP（_Model Context Protocol_，模型上下文协议）是一个开放协议，可用于将编程智能体与工具连接起来。例如，这个 [Notion MCP 服务器](https://github.com/makenotion/notion-mcp-server) 可以让你的智能体读写 Notion 文档，从而实现类似"读取 {Notion 文档} 中链接的规格说明，在 Notion 中起草一个实现计划作为新页面，然后实现原型"的用法。要发现 MCP 服务器，可以使用 [Pulse](https://www.pulsemcp.com/servers) 和 [Glama](https://glama.ai/mcp/servers) 等目录。
- **上下文管理**。正如 [上面](#how-ai-models-and-agents-work) 所指出的，支撑编程智能体的 LLM 具有有限的 _上下文窗口_。有效地使用编程智能体需要合理地使用上下文。你需要确保智能体能够获取所需的信息，同时避免不必要的上下文信息，以防止上下文窗口溢出或模型性能下降（上下文增大时这种情况往往会发生，即使没有溢出上下文窗口）。智能体编排器会自动提供并一定程度上管理上下文，但大量的控制权仍留给了用户。
    - **清除上下文窗口**。最基本的控制方式是，编程智能体支持清除上下文窗口（开始新对话），对于无关的查询你应该这样做。
    - **回退对话**。一些编程智能体支持撤销对话历史中的步骤。当"撤销"比发送一条后续消息将智能体引向不同方向更合适时，这种方式可以更有效地管理上下文。
{%- comment %}
做一个快速演示。
{% endcomment %}
    - **压缩（Compaction）**。为了支持无界长度的对话，编程智能体支持上下文 _压缩_：如果对话历史过长，它们会自动调用一个 LLM 来总结对话的前缀部分，并用摘要替换对话历史。一些智能体会将控制权的用户交互开放给用户，以便在需要时手动触发压缩。
{%- comment %}
在 Claude Code 中展示 `/compact` 命令，展示完整的压缩摘要。
{% endcomment %}
    - **llms.txt**。`/llms.txt` 文件是一个提议中的 [标准](https://llmstxt.org/) 位置，存放一份专为 LLM 在推理时使用的文档。产品（如 [cursor.com/llms.txt](https://cursor.com/llms.txt)）、软件库（如 [ai.pydantic.dev/llms.txt](https://ai.pydantic.dev/llms.txt)）和 API（如 [apify.com/llms.txt](https://apify.com/llms.txt)）可能会有 `llms.txt` 文件，这些文件对开发工作很有帮助。这类文档的 _信息密度_（每个 token 承载的信息量）更高，因此比要求编程智能体去抓取并阅读一个 HTML 页面更节省上下文。当编程智能体没有关于你想要使用的某个依赖项的内置知识时（例如，因为该依赖项的发布时间晚于 LLM 的知识截止），外部文档就很有用。
{%- comment %}
在一个空仓库中（桌面或其他自包含位置，已执行 `git init`）做左右对比：

    Write a single-file Python program example in demo.py using semlib to sort "Ilya Sutskever", "Soumith Chintala", and "Donald Knuth" in terms of their fame as AI researchers.

    Write a single-file Python program example in demo.py using semlib to sort "Ilya Sutskever", "Soumith Chintala", and "Donald Knuth" in terms of their fame as AI researchers. See https://semlib.anish.io/llms.txt. Follow links to Markdown versions of any pages linked in llms.txt files.

    不知道为什么智能体不会默认这样做。你可能需要把最后一句写进 CLAUDE.md 文件中。
{% endcomment %}
    - **AGENTS.md**。大多数编程智能体支持 [AGENTS.md](https://agents.md/) 或类似的配置（例如，Claude Code 会查找 `CLAUDE.md`），作为智能体的"README"。当智能体启动时，它会预先填充 `AGENTS.md` 的完整内容作为上下文。你可以利用它来提供跨会话通用的建议（例如，指示它在修改代码后始终运行类型检查器，说明如何运行单元测试，或提供智能体可以浏览的第三方文档链接）。一些编程智能体可以自动生成这个文件（例如，Claude Code 中的 `/init` 命令）。[这里](https://github.com/pydantic/pydantic-ai/blob/main/CLAUDE.md) 是 `AGENTS.md` 的一个实际例子。
{%- comment %}
Dotbot 示例，CLAUDE.md 包含 @DEVELOPMENT.md，并指示在对任何 Python 代码进行任何更改后始终运行类型检查器和代码格式化程序。

示例提示，在 master 分支上：

    Remove the "--version" command-line flag.

这是一个快速的操作，适合用于演示。
{% endcomment %}
    - **Skills**。`AGENTS.md` 的内容会以其全部内容加载到智能体的上下文窗口中。_Skills_ 在智能体上下文的加载上增加了一层间接性，以避免上下文膨胀：你可以向智能体提供一份 skills 列表及其描述，然后智能体可以根据需要"打开"某个 skill（将其加载到上下文窗口中）。
    - **子智能体（Subagents）**。一些编程智能体允许你定义 _子智能体_ —— 针对特定工作流的专用智能体。顶层编程智能体可以调用子智能体来完成特定任务，这使得顶层智能体和子智能体都能更有效地管理上下文。顶层智能体的上下文不会被子智能体看到的所有内容填充，子智能体也可以只获取其任务所需的上下文。一个例子是，一些编程智能体将网页研究实现为一个子智能体：顶层智能体会向子智能体提出问题，子智能体运行网页搜索、检索单个网页、进行分析，然后将答案提供给顶层智能体。这样，顶层智能体的上下文不会被所有检索到的网页的完整内容填充，子智能体的上下文中也不会包含顶层智能体的其余对话历史。

对于许多需要编写提示的高级功能（如 skills 或子智能体），你可以使用 LLM 来帮你入门。一些编程智能体甚至内置了对此的支持。例如，Claude Code 可以根据简短提示生成一个子智能体（调用 `/agents` 并创建新智能体）。尝试用以下提示创建一个子智能体：

```
A Python code checking agent that uses `mypy` and `ruff` to type-check, lint, and format *check* any files that have been modified from the last git commit.
```

然后，你可以使用顶层智能体通过类似"使用代码检查子智能体"的消息来显式调用该子智能体。你也可以尝试让顶层智能体在适当的时候自动调用该子智能体，例如，在修改任何 Python 文件之后。

# 需要注意的事项

AI 工具可能会犯错。它们构建在 LLM 之上，而 LLM 仅仅是概率性的 next-token 预测模型。它们并不像人类那样"智能"。请审查 AI 输出以确保正确性和安全缺陷。有时验证代码的正确性比你自己编写代码更难 —— 对于关键代码，考虑手写。AI 可能会陷入死胡同并试图"哄骗"你；注意调试螺旋（debugging spirals）。不要把 AI 当作拐杖，要警惕过度依赖或对技术理解肤浅的情况。AI 仍然无法胜任大量编程任务。计算思维能力仍然宝贵。

# 推荐的软件

许多 IDE / AI 编程扩展都包含编程智能体（参见 [开发环境讲座](/2026/development-environment/) 中的推荐）。其他流行的编程智能体包括 Anthropic 的 [Claude Code](https://www.claude.com/product/claude-code)、OpenAI 的 [Codex](https://openai.com/codex/)，以及开源智能体如 [opencode](https://github.com/anomalyco/opencode)。

# 练习

1. 通过同一个编程任务的四次实践，比较手写编程、使用 AI 自动补全、内联聊天和智能体的体验。最适合的场景是对你正在做的项目的一个小型新功能。如果你需要更多想法，可以考虑完成 GitHub 上开源项目中的"good first issue"类任务，或 [Advent of Code](https://adventofcode.com/) 或 [LeetCode](https://leetcode.com/) 的题目。
1. 使用 AI 编程智能体来浏览一个你不熟悉的代码库。最好在你想调试或为你真正关心项目的添加新功能时进行。如果你想不到这样的项目，可以尝试用 AI 智能体来理解 [opencode](https://github.com/anomalyco/opencode) 智能体中的安全相关功能是如何工作的。
1. 从零开始 vibe code 一个小应用。不要手写任何一行代码。
1. 为你选择的编程智能体创建并测试 `AGENTS.md`（或你选择的智能体对应的类似文件，如 `CLAUDE.md`）、一个 skill（例如，[Claude Code 中的 skill](https://code.claude.com/docs/en/skills) 或 [Codex 中的 skill](https://developers.openai.com/codex/skills/)），以及一个子智能体（例如，[Claude Code 中的子智能体](https://code.claude.com/docs/en/sub-agents)）。思考在什么场景下你会选择使用其中某一种而不是其他。注意，你选择的编程智能体可能不支持某些功能；你可以跳过它们，或者尝试支持这些功能的其他编程智能体。
1. 使用编程智能体来完成与 [代码质量讲座](/2026/code-quality/) 中 Markdown 项目符号正则表达式练习相同的目标。它是否通过直接编辑文件来完成这些任务？智能体直接编辑文件以完成此类任务有哪些缺点和局限性？找出一种提示智能体的方法，让它不通过直接编辑文件来完成任务。提示：要求智能体使用 [第一个讲座](/2026/course-shell/) 中提到的命令行工具之一。
1. 大多数编程智能体都支持一种"yolo 模式"（例如，在 Claude Code 中为 `--dangerously-skip-permissions`）。直接使用该模式是不安全的，但在隔离环境（如虚拟机或容器）中运行编程智能体然后启用自主操作也许是可接受的。在你的机器上设置这个环境。[Claude Code devcontainers](https://code.claude.com/docs/en/devcontainer) 或 [Docker Sandboxes / Claude Code](https://docs.docker.com/ai/sandboxes/agents/claude-code/) 等文档可能会派上用场。设置方法不止一种。
