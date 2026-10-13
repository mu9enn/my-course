---
layout: lecture
title: "代码质量"
description: >
  了解代码格式化、静态检查、测试、持续集成等知识。
thumbnail: /static/assets/thumbnails/2026/lec9.png
date: 2026-01-23
ready: true
video:
  aspect: 56.25
  id: XBiLUNx84CQ
---

开发者在编写高质量代码时，有多种工具和技法可以借助。在本课中，我们将涵盖以下内容：

- [格式化](#格式化)
- [静态检查](#静态检查)
- [测试](#测试)
- [提交前钩子](#提交前钩子)
- [持续集成](#持续集成)
- [命令运行器](#命令运行器)

此外，我们还将以bonus话题介绍[正则表达式](#正则表达式)，这是一项跨领域主题，不仅可用于代码质量相关的场景（例如，运行与某个模式匹配的测试子集），还能在 IDE 等其它领域发挥作用（例如，搜索与替换）。

其中许多工具都与编程语言绑定（例如，面向 Python 的 [Ruff](https://docs.astral.sh/ruff/) lint/格式化器）。但也有某些工具支持多语言（例如 [Prettier](https://prettier.io/) 代码格式化器）。不过这些概念几乎是通用的——你总能在任何编程语言中找到对应的代码格式化器、lint 工具、测试库等。

# 格式化 {: #formatting}

代码自动格式化器（code auto-formatters）会直接改善代码的表面语法。这样一来，你就可以把精力集中到更深入、更具挑战性的问题上，而格式化器则处理一些琐碎的细节，例如字符串使用的是 `'` 还是 `"`、二元运算符两侧是否保留空格（`x + y` 而非 `x+y`）、`import` 语句是否按字母顺序排列、行长度是否超过限制等。代码格式化器的一个主要好处是：它能将代码风格统一到所有参与项目的开发者身上。

有些工具（如 Prettier）是[高度可配置的](https://prettier.io/docs/configuration)——你应该把配置文件也提交到项目的[版本控制](/2026/version-control/)中。另一些工具（如 [Black](https://github.com/psf/black) 和 [gofmt](https://pkg.go.dev/cmd/gofmt)）则限制甚至取消了可配置项，以减少[ bikeshedding（琐事偏好）](https://en.wikipedia.org/wiki/Law_of_triviality)带来的争议。

你可以将 IDE 集成（参见 [开发环境](/2026/development-environment/#code-intelligence-and-language-servers)）与代码格式化器联动，在键入代码时或保存文件时自动格式化。你也可以在项目里添加一个 [EditorConfig](https://editorconfig.org/) 文件，用来向 IDE 传递某些项目级别的设置，例如每种文件类型的缩进大小。

# 静态检查 {: #linting}

Lint 工具（linters）运行[静态分析](https://en.wikipedia.org/wiki/Static_program_analysis)——即在不运行代码的前提下分析代码——来发现代码中的反模式（antipatterns）和潜在问题。这类工具比格式化器走得更深，不再只关注表面语法，而是深入检查逻辑结构。分析的深度因工具而异。

Lint 工具内置了一组规则列表（rules），并通常提供可在项目级别配置的预设（presets）。部分 lint 规则会产生误报（false positives），因此你可以根据文件级别或行级别禁用这些规则。

优秀的 lint 工具会自带帮助文档，说明每条规则的目的：它在检测什么、为什么这样不好、以及更优的代码写法是什么。例如，[Ruff](https://docs.astral.sh/ruff/) 的 [SIM102](https://docs.astral.sh/ruff/rules/collapsible-if/) 规则文档就解释了它如何捕获 Python 代码中不必要的嵌套 `if` 语句。

某些 lint 工具不仅能标记问题，还能自动修复部分问题。

除了语言特定的 lint 工具之外，[semgrep](https://github.com/semgrep/semgrep)——一款"语义 grep"工具——也很有用。它在抽象语法树（AST）层面工作（而非像传统 grep 那样在字符层面），并且支持多种编程语言。你可以用 semgrep 轻松为项目编写自定义 lint 规则。例如，如果你想阻止 Python 中使用危险的 `subprocess.Popen(..., shell=True)`，可以用以下命令找到这类代码模式：

```bash
semgrep -l python -e "subprocess.Popen(..., shell=True, ...)"
```

# 测试 {: #testing}

软件测试是提高你对代码正确性信心的标准方法。你编写代码，然后再编写测试代码来运行这些代码，并在代码未按预期工作时抛出错误。

你可以针对不同粒度的代码块编写测试：针对单个函数的_单元测试_（unit tests）、针对模块或服务之间交互的_集成测试_（integration tests），以及针对端到端场景的_功能测试_（functional tests）。你还可以采用_测试驱动开发_（test-driven development），即在任何实现代码之前先写测试。当发现 bug 时，你可以编写_回归测试_（regression tests），以便将来能立即捕捉到同一功能是否再次出现问题。你还可以编写_属性测试_（property-based tests），这一方法最早由 Haskell 中的 [QuickCheck](https://hackage.haskell.org/package/QuickCheck) 提出，后来在包括 Python 的 [Hypothesis](https://hypothesis.readthedocs.io/) 等众多库中得到了实现。选择哪种测试方法取决于你的项目；通常你会采用某种组合方案。

如果你的程序有外部依赖（例如数据库或 Web API），那么在测试中_模拟（mock）_这些依赖可能比让代码在测试时直接跟第三方依赖交互更合适。

## 代码覆盖率 {: #code-coverage}

代码覆盖率（code coverage）是衡量测试质量的一种指标。代码覆盖率会统计你的哪些代码行在运行测试时被执行了，以确保你覆盖了所有代码路径。代码覆盖率工具可以逐行展示覆盖情况，指导你编写测试。像 [Codecov](https://app.codecov.io) 这样的服务则提供了 Web 界面，用于跟踪和查看项目在历史各阶段的代码覆盖率。

不过，和任何指标一样，代码覆盖率并不完美——不要过度追求覆盖率数字，重点在于编写高质量的测试。

# 提交前钩子 {: #pre-commit-hooks}

Git 提交前 [钩子](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)（pre-commit hooks）配合 [pre-commit](https://pre-commit.com/) 框架，可以在每次 Git 提交之前自动运行用户指定的代码。很多项目使用提交前钩子来在每个提交之前自动运行格式化器和 lint 工具，有时也运行测试，以确保提交的代码符合项目的代码风格且没有某些已知问题。

# 持续集成 {: #continuous-integration}

[持续集成（CI）](https://en.wikipedia.org/wiki/Continuous_integration)服务（如 [GitHub Actions](https://github.com/features/actions)）可以在你每次推送代码时（或在每个 pull request 上，或按预定时间表）自动运行脚本。开发者通常利用 CI 服务来运行各种代码质量工具，包括格式化器、lint 工具和测试。对于编译型语言，你可以确保代码能编译通过；对于静态类型语言，你可以确保类型检查通过。每次推送新提交时运行 CI 可以发现引入到主干代码中的错误；在 pull request 上运行可以发现贡献者的提交问题；定时运行则可以发现外部依赖带来的问题（例如，开发者意外发布了一个破坏性变更，尽管版本号仍[符合语义化版本](/2026/shipping-code/#releases--versioning)）。

由于 CI 脚本是在开发者机器之外独立运行的，你可以很方便地在这里运行长时间作业。例如，你可以利用它来在不同操作系统和编程语言版本上运行_测试矩阵_（test matrix），以确保软件在所有环境下都能正常工作。

通常，CI 中运行的脚本不会直接修改你的代码——它会以"仅检查"（check-only）模式而非"修复"（fix）模式运行工具。例如，代码不符合格式化规范时，自动格式化器会报错。

仓库常在 README 中添加[状态徽章](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge)，显示 CI 状态和其他信息（如代码覆盖率）。例如，下面是 Missing Semester 当前的构建状态。

[![Build Status](https://github.com/missing-semester/missing-semester/actions/workflows/build.yml/badge.svg)](https://github.com/missing-semester/missing-semester/actions/workflows/build.yml) [![Links Status](https://github.com/missing-semester/missing-semester/actions/workflows/links.yml/badge.svg)](https://github.com/missing-semester/missing-semester/actions/workflows/links.yml)

> 我们的 [链接检查器](https://github.com/missing-semester/missing-semester/blob/master/.github/workflows/links.yml)（使用了 [proof-html](https://github.com/anishathalye/proof-html) GitHub Action）经常会失败，通常是因为第三方网站的问题。尽管如此，它帮助我们发现并修复了许多链接失效的情况（有时是因为拼写错误，更多时候是因为网站在移动内容时没有添加重定向，甚至网站本身消失了）。

学习 CI 服务、格式化器、lint 工具和测试库的具体用法，最好的方式就是通过阅读优秀开源项目的代码。在 GitHub 上寻找高质量的开源项目——与你自己在编程语言、领域、规模和项目范围上越相似越好——然后研究它们的 `pyproject.toml`、`.github/workflows/`、`DEVELOPMENT.md` 以及其他相关文件。

## 持续部署 {: #continuous-deployment}

[持续部署](https://en.wikipedia.org/wiki/Continuous_deployment)利用 CI 基础设施来真正_部署_变更。例如，Missing Semester 仓库使用持续部署将内容发布到 GitHub Pages，因此每次我们 `git push` 更新讲义时，网站都会自动构建和部署。你也可以在 CI 中构建其他类型的[产物](/2026/shipping-code/)，如应用程序的二进制文件或服务的 Docker 镜像。

# 命令运行器 {: #command-runners}

命令运行器（command runners）（如 [just](https://github.com/casey/just)）简化了在项目上下文中运行命令的任务。当你逐步为项目搭建起代码质量基础设施时，不希望让开发者记忆诸如 `uv run ruff check --fix` 这样的冗长命令。有了命令运行器，你可以把这样的命令简化为 `just lint`，同时还可以有 `just format`、`just typecheck` 等对应的调用，覆盖开发者可能要为你项目运行的各种工具。

一些语言特定的项目或包管理器内置了对该功能的支持，这意味着你不需要使用语言无关的工具（如 `just`）。例如，[npm](https://nodejs.org/en/learn/getting-started/an-introduction-to-the-npm-package-manager)（Node.js）的 `package.json` 中的 `scripts` 部分，以及 [Hatch](https://hatch.pypa.io/)（Python）的 `pyproject.toml` 中的 `tool.hatch.envs.*.scripts` 部分都支持这一功能。

# 正则表达式 {: #regular-expressions}

_正则表达式_（regular expressions，常缩写为 "regex"）是一种用来表示字符串集合的语言。正则表达式在各种场景下都常用于模式匹配，比如命令行工具和 IDE。例如，[ag](https://github.com/ggreer/the_silver_searcher) 支持在代码库范围内搜索时匹配正则表达式（例如，`ag "import .* as .*"` 会找到 Python 中所有重命名的导入语句）；[go test](https://pkg.go.dev/cmd/go#hdr-Test_packages) 支持 `-run [regexp]` 选项来选择性地运行部分测试。此外，大多数编程语言都内置了正则表达式匹配支持或有第三方库可用，因此你可以用正则表达式来实现模式匹配、验证和解析等功能。

为了帮助你建立直觉，下面是一些正则表达式模式的例子。本课使用的是 [Python 正则表达式语法](https://docs.python.org/3/library/re.html)。正则表达式有很多种方言，尤其在高级功能方面略有差异。你可以使用 [regex101](https://regex101.com/) 等在线正则表达式测试器来开发和调试正则表达式。

- `abc` --- 匹配字面字符串 "abc"。
- `missing|semester` --- 匹配字符串 "missing" 或字符串 "semester"。
- `\d{4}-\d{2}-\d{2}` --- 匹配 YYYY-MM-DD 格式的日期，如 "2026-01-14"。这个表达式除了确保字符串由四位数字、一个连字符、两位数字、一个连字符和两位数字组成之外，并不会校验日期的合法性，因此 "2026-01-99" 也匹配这个正则表达式模式。
- `.+@.+` --- 匹配电子邮件地址，即字符串包含一些文本、然后是一个 "@"、再跟一些文本。这只做了最基本的校验，像 "nonsense@@@email" 这样的字符串也会被匹配。一个不产生误报或漏报的电子邮件匹配正则表达式[确实存在](https://pdw.ex-parrot.com/Mail-RFC822-Address.html)，但不切实际。

## 正则表达式语法 {: #regex-syntax}

你可以在[这份文档](https://docs.python.org/3/library/re.html#regular-expression-syntax)（或网上众多其他资源）中找到正则表达式语法的全面指南。以下是几个基本构件：

- `abc` 匹配字面字符串，当字符没有特殊含义时（本例中为 "abc"）
- `.` 匹配任意单个字符
- `[abc]` 匹配方括号内的单个字符（本例中为 "a"、"b" 或 "c"）
- `[^abc]` 匹配除方括号内字符之外的单个字符（例如 "d"）
- `[a-f]` 匹配方括号内范围指示的单个字符（例如 "c"，但不包括 "q"）
- `a|b` 匹配其中任一模式（例如 "a" 或 "b"）
- `\d` 匹配任意数字字符（例如 "3"）
- `\w` 匹配任意单词字符（例如 "x"）
- `\b` 匹配单词_边界_（例如，在字符串 "missing semester" 中，匹配 "m" 之前、"g" 之后、"s" 之前和 "r" 之后的位置）
- `(...)` 匹配一个模式组
- `...?` 匹配零个或一个模式，如 `words?` 用于匹配 "word" 或 "words"
- `...*` 匹配任意数量的模式，如 `.*` 匹配任意数量的任意字符
- `...+` 匹配一个或多个模式，如 `\d+` 匹配一个或多个数字
- `...{N}` 精确匹配 N 个模式，如 `\d{4}` 匹配四位数字
- `\.` 匹配字面的 "."
- `\\` 匹配字面的 "\\"
- `^` 匹配行首
- `$` 匹配行尾

> 译者补充：正则表达式中 `.` 不匹配换行符（除非使用特定标志），这在文件搜索或日志解析时经常造成困惑。如果需要在多行文本中使用 `.` 匹配任意字符（包括换行符），可以在 Python 的 `re` 模块中传入 `re.DOTALL` 标志。

## 捕获组与引用 {: #capture-groups-and-references}

如果你使用了正则表达式的分组 `(...)`，你可以引用匹配结果中的子部分来进行提取或搜索-替换。例如，要从 YYYY-MM-DD 格式的日期中提取月份，你可以使用以下 Python 代码：

```python
>>> import re
>>> re.match(r"\d{4}-(\d{2})-\d{2}", "2026-01-14").group(1)
'01'
```

在文本编辑器中，你可以在替换模式中使用捕获组引用。不同 IDE 的语法可能有所不同。例如，在 VS Code 中，你可以使用 `$1`、`$2` 等变量来引用捕获组；在 Vim 中，你可以使用 `\1`、`\2` 等来引用。

## 局限性 {: #limitations}

[正则语言](https://en.wikipedia.org/wiki/Regular_language)功能强大但仍有局限——存在某些字符串类别无法用标准正则表达式来表达（例如，[不可能](https://en.wikipedia.org/wiki/Pumping_lemma_for_regular_languages)写出一个匹配集合 `{a^n b^n | n ≥ 0}` 的正则表达式，即 "n 个 'a' 后跟相同数量 'b'" 的字符串集合；更实用地说，像 HTML 这样的语言就不是正则语言）。实际上，现代正则表达式引擎支持前瞻（lookahead）和反向引用（backreferences）等特性，使能力超越了正则语言——它们在实践中的确非常有用。但重要的是要知道，它们表达能力仍有限制。对于更复杂的解析需求，你可能需要求助于更强大的解析器（例如，参见 [pyparsing](https://github.com/pyparsing/pyparsing)，这是一种 [PEG](https://en.wikipedia.org/wiki/Parsing_expression_grammar) 解析器）。

## 如何学习正则表达式 {: #learning-regex}

我们建议你掌握基础（即本课所涵盖的内容），然后在需要时查阅正则表达式参考文档，而不是试图记住整门语言的全部语法。

对话式 AI 工具可以帮助你生成正则表达式。例如，你可以向喜欢的 LLM 发出以下提示：

```
Write a Python-style regex pattern that matches the requested path from log lines from Nginx. Here is an example log line:

169.254.1.1 - - [09/Jan/2026:21:28:51 +0000] "GET /feed.xml HTTP/2.0" 200 2995 "-" "python-requests/2.32.3"
```

# 练习

1. 为你正在参与的项目配置一个格式化器、一个 lint 工具和提交前钩子。如果你遇到大量错误：先运行自动格式化来处理格式问题。对于 lint 错误，尝试使用 [AI 智能体](/2026/agentic-coding/) 来修复所有 lint 错误。确保 AI 智能体能够运行 lint 工具并观察结果，以便它能在一个迭代循环中修复所有问题。仔细检查结果，确保 AI 不会破坏你的代码！
1. 学习一门你熟悉的语言的测试库，并为你正在参与的项目编写一个单元测试。运行代码覆盖率工具，生成 HTML 格式的覆盖率报告，然后观察结果。你能找到哪些行被覆盖了？你的代码覆盖率大概率会很低。尝试手动编写一些测试来提升覆盖率。尝试使用 [AI 智能体](/2026/agentic-coding/) 来改善覆盖率——确保 AI 编码智能体能够运行带有覆盖率的测试并生成逐行覆盖率报告，以便它知道该从哪里入手。AI 生成的测试质量如何？
1. 为你正在参与的项目配置持续集成，在每次推送时运行 CI。让 CI 运行格式化、lint 和测试。故意破坏你的代码（例如，引入一条 lint 违规），确保 CI 能捕获到它。
1. 尝试编写一个[正则表达式模式](#正则表达式)，并使用 `grep` [命令行工具](/2026/course-shell/)在你的代码中查找 `subprocess.Popen(..., shell=True)` 的出现。现在尝试"搞坏"你的正则表达式。[semgrep](#静态检查)仍然能成功匹配到被 grep 调用漏掉的那些危险代码吗？
1. 在你的 IDE 或文本编辑器中练习正则表达式的搜索-替换功能：将[这份讲义](https://raw.githubusercontent.com/missing-semester/missing-semester/refs/heads/master/_2026/code-quality.md)中的 `-` [Markdown 项目符号](https://spec.commonmark.org/0.31.2/#bullet-list-marker)替换为 `*` 项目符号。注意，直接把文件中所有的 "-" 字符替换掉是不正确的，因为文件中有很多 "-" 的用法并不是项目符号。
1. 编写一个正则表达式，从如下形式的 JSON 结构 `{"name": "Alyssa P. Hacker", "college": "MIT"}` 中提取 name（在本例中为 `Alyssa P. Hacker`）。提示：在第一次尝试时，你可能会写出一条最终提取出 `Alyssa P. Hacker", "college": "MIT` 的正则表达式。阅读 [Python 正则表达式文档](https://docs.python.org/3/library/re.html) 中关于贪婪量词（greedy quantifiers）的内容来弄清楚如何修复。
    1. 让正则表达式即使在名称中包含 `"` 字符的情况下也能正常工作（JSON 中的双引号可以用 `\"` 转义）。
    1. 我们**不建议**在实战中使用正则表达式来处理复杂的解析问题。请尝试使用你编程语言的 JSON 解析器来完成这个任务。编写一个命令行程序，从 stdin 接收上述形式的 JSON 结构作为输入，将 name 输出到 stdout。你只需要几行代码即可做到。在 Python 中，除了 `import json` 之外，一行代码就能搞定。