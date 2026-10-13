---
layout: lecture
title: "开发环境与工具"
description: >
  了解 IDE、Vim、语言服务器和 AI 驱动的开发工具。
thumbnail: /static/assets/thumbnails/2026/lec3.png
date: 2026-01-14
ready: true
video:
  aspect: 56.25
  id: QnM1nVzrkx8
---

_开发环境_（Development Environment）是一组用于开发软件的工具体系。开发环境的核心是文本编辑功能，以及与之配套的特性，如语法高亮、类型检查、代码格式化、自动补全等。_集成开发环境_（Integrated Development Environments, IDE）——例如 [VS Code][vs-code]——将上述所有功能整合到一个应用程序中。基于终端的开发工作流则将 [tmux](https://github.com/tmux/tmux)（终端复用器）、[Vim](https://www.vim.org/)（文本编辑器）、[Zsh](https://www.zsh.org/)（shell）等工具与语言专属的命令行工具（如 [Ruff](https://docs.astral.sh/ruff/)——一个 Python linter 和代码格式化器，以及 [Mypy](https://mypy-lang.org/)——一个 Python 类型检查器）结合起来使用。

IDE 和基于终端的工作流各有优劣。例如，图形化 IDE 通常更容易上手，今天的 IDE 也普遍具备更好的开箱即用的 AI 集成（如 AI 自动补全）；另一方面，基于终端的工作流更加轻量，并且在没有图形界面或无法安装软件的环境中，它们可能是你唯一的选择。建议你至少对两者都有基本了解，并精通其中至少一种。如果你还没有偏好的 IDE，我们建议从 [VS Code][vs-code] 开始。

在本讲中，我们将涵盖以下内容：

- [文本编辑与 Vim](#文本编辑与-vim)
- [代码智能与语言服务器](#代码智能与语言服务器)
- [AI 驱动的开发](#ai-驱动的开发)
- [扩展与其他 IDE 功能](#扩展与其他-ide-功能)

[vs-code]: https://code.visualstudio.com/

# 文本编辑与 Vim

编写程序时，你大部分时间花在导航代码、阅读代码片段和进行编辑上，而不是编写长篇大论或从头到尾读取文件。[Vim] 是一款为这种任务分布而优化的文本编辑器。

**Vim 的理念。** Vim 的美妙之处在于：它的接口本身就是一门编程语言，专门用于导航和编辑文本。按键（带有助记名称）就是命令，而这些命令是可以组合的。Vim 避免了鼠标的使用，因为鼠标太慢了；它甚至避免了方向键的使用，因为方向键需要移动手的位置太多。结果就是：一款感觉如同脑机接口、能跟上你思维速度的编辑器。

**其他软件中的 Vim 支持。** 你不必直接使用 [Vim] 也能从其核心理念中受益。许多涉及文本编辑的程序都支持 "Vim 模式"，无论是内置功能还是通过插件实现。例如，VS Code 有 [VSCodeVim](https://marketplace.visualstudio.com/items?itemName=vscodevim.vim) 插件，Zsh 有 [内置的](https://zsh.sourceforge.io/Guide/zshguide04.html) Vim 模拟支持，甚至 Claude Code 也有 [内置的](https://code.claude.com/docs/en/interactive-mode#vim-editor-mode) Vim 编辑器模式支持。你使用的任何涉及文本编辑的工具，基本上都以某种方式支持 Vim 模式。

## 多模式编辑

Vim 是一款_多模式编辑器_（Modal Editor）：它针对不同类型的任务拥有不同的操作模式。

- **普通模式**（Normal）：用于在文件中导航和进行编辑
- **插入模式**（Insert）：用于插入文本
- **替换模式**（Replace）：用于替换文本
- **可视模式**（Visual，包括普通、行、块）：用于选择文本块
- **命令行模式**（Command-line）：用于执行命令

不同操作模式下，按键的含义各不相同。例如，字母 `x` 在插入模式下只会输入一个字符 "x"，但在普通模式下，它会删除光标所在的字符，而在可视模式下，它会删除当前选区。

在默认配置下，Vim 会在左下角显示当前模式。初始/默认模式是普通模式。你通常会在普通模式和插入模式之间来回切换。

你可以通过按下 `<ESC>`（Esc 键）从任意模式切换回普通模式。从普通模式出发，用 `i` 进入插入模式，用 `R` 进入替换模式，用 `v` 进入可视模式，用 `V` 进入可视行模式，用 `<C-v>`（Ctrl-V，有时也写作 `^V`）进入可视块模式，用 `:` 进入命令行模式。

使用 Vim 时你会频繁使用 `<ESC>` 键：可以考虑将 Caps Lock 映射为 Escape（[macOS 设置方法](https://vim.fandom.com/wiki/Map_caps_lock_to_escape_in_macOS)），或者用一个简单的按键序列来创建 `<ESC>` 的[替代映射](https://vim.fandom.com/wiki/Avoid_the_escape_key#Mappings)。

## 基础：插入文本

从普通模式出发，按下 `i` 即可进入插入模式。此时，Vim 的行为就像其他任何文本编辑器一样，直到你按下 `<ESC>` 返回普通模式。这一操作加上上文介绍的基础知识，就足以开始用 Vim 编辑文件了（不过如果你大部分编辑工作都在插入模式下完成，效率就不会特别高）。

## Vim 的接口是一门编程语言

Vim 的接口是一门编程语言。按键（带有助记名称）就是命令，而这些命令_可以组合_。这实现了高效的移动和编辑操作，一旦这些命令成为肌肉记忆，就像学会了键盘布局后打字变得非常高效一样。

### 移动

你应当把大部分时间花在普通模式上，使用移动命令来导航文件。Vim 中的移动操作也被称为"名词"（nouns），因为它们指的是文本的某个片段。

- 基础移动：`hjkl`（左、下、上、右）
- 单词：`w`（下一个词）、`b`（词的开头）、`e`（词的结尾）
- 行：`0`（行首）、`^`（第一个非空白字符）、`$`（行尾）
- 屏幕：`H`（屏幕顶部）、`M`（屏幕中间）、`L`（屏幕底部）
- 滚动：`Ctrl-u`（向上）、`Ctrl-d`（向下）
- 文件：`gg`（文件开头）、`G`（文件结尾）
- 行号：`:{number}<CR>` 或 `{number}G`（跳转到第 {number} 行）
    - `<CR>` 指回车键
- 杂项：`%`（匹配的项，如括号或大括号）
- 查找：`f{character}`、`t{character}`、`F{character}`、`T{character}`
    - 在当前行向前/向后查找/定位到 {character}
    - `,` / `;` 用于在匹配结果之间跳转
- 搜索：`/{regex}`、`n` / `N` 用于在搜索结果之间跳转

### 选择

可视模式：

- 可视模式：`v`
- 可视行模式：`V`
- 可视块模式：`Ctrl-v`

可以使用移动键来进行选择。

### 编辑

你过去用鼠标做的事情，现在可以用组合编辑命令和移动命令的键盘操作来完成。这里就是 Vim 的接口开始看起来像一门编程语言的地方。Vim 的编辑命令也被称为"动词"（verbs），因为动词作用于名词。

- `i` 进入插入模式
    - 但对于操作/删除文本，仅靠退格键是不够的
- `o` / `O` 在下方 / 上方插入新行
- `d{motion}` 删除 {motion}
    - 例如 `dw` 是删除一个词，`d$` 是删除到行尾，`d0` 是删除到行首
- `c{motion}` 改变 {motion}
    - 例如 `cw` 是改变一个词
    - 类似于 `d{motion}` 后跟 `i`
- `x` 删除字符（等价于 `dl`）
- `s` 替换字符（等价于 `cl`）
- 可视模式 + 操作
    - 选中文本后，`d` 删除或 `c` 改变
- `u` 撤销，`<C-r>` 重做
- `y` 复制 / "拉取"（yank）（其他一些命令如 `d` 也会复制）
- `p` 粘贴
- 更多功能等着你去探索：例如，`~` 翻转字符大小写，`J` 将行连接在一起

### 计数

你可以将"名词"和"动词"与计数结合，重复执行某个动作指定次数。

- `3w` 向前移动 3 个词
- `5j` 向下移动 5 行
- `7dw` 删除 7 个词

### 修饰符

你可以使用修饰符来改变名词的含义。一些修饰符包括 `i`（表示"内部"或"里面"）和 `a`（表示"周围"）。

- `ci(` 改变当前括号对内部的内容
- `ci[` 改变当前方括号对内部的内容
- `da'` 删除一个单引号字符串，包括外部的单引号

## 综合运用

下面是一个有 bug 的 [fizz buzz](https://en.wikipedia.org/wiki/Fizz_buzz) 实现：

```python
def fizz_buzz(limit):
    for i in range(limit):
        if i % 3 == 0:
            print("fizz", end="")
        if i % 5 == 0:
            print("fizz", end="")
        if i % 3 and i % 5:
            print(i, end="")
        print()

def main():
    fizz_buzz(20)
```

我们使用以下命令序列来修复这些问题（从普通模式开始）：

- main 从未被调用
    - `G` 跳转到文件末尾
    - `o` 在下方**开**启一个新行
    - 输入 `if __name__ == "__main__": main()`
        - 如果你的编辑器有 Python 语言支持，它在插入模式下可能会为你做一些自动缩进
    - `<ESC>` 返回普通模式
- 从 0 开始而非 1
    - 输入 `/` 然后输入 `range` 再按 `<CR>` 来搜索 "range"
    - `ww` 向前移动两个**w**ord（你也可以用 `2w`，但在实际使用中，对于小计数而言，重复按键比使用计数功能更为常见）
    - `i` 切换到**i**nsert 模式，并添加 `1,`
    - `<ESC>` 返回普通模式
    - `e` 跳转到下一个词的**e**nd
    - `a` 开始**a**ppending 文本，并添加 `+ 1`
    - `<ESC>` 返回普通模式
- 对 5 的倍数打印 "fizz"
    - `:6<CR>` 跳转到第 6 行
    - `ci"` 在 '**"**' 内部**c**hange **i**nside，改为 `"buzz"`
    - `<ESC>` 返回普通模式

## 学习 Vim

学习 Vim 的最好方法是掌握基础（上文已涵盖的内容），然后在所有支持它的软件中启用 Vim 模式，在实际使用中练习。不要有使用鼠标或方向键的冲动；在某些编辑器中，你可以解除方向键的绑定来强迫自己养成良好的习惯。

### 额外资源

- 本课程上一轮迭代中的 [Vim 讲义](/2020/editors/) —— 我们已经在那里更深入地覆盖过 Vim
- `vimtutor` 是随 Vim 安装附带的教程 —— 如果 Vim 已安装，你应该能从 shell 中运行 `vimtutor`
- [Vim Adventures](https://vim-adventures.com/) 是一款用于学习 Vim 的游戏
- [Vim Tips Wiki](https://vim.fandom.com/wiki/Vim_Tips_Wiki)
- [Vim Advent Calendar](https://vimways.org/2019/) 提供了各种 Vim 技巧
- [VimGolf](https://www.vimgolf.com/) 是[代码高尔夫](https://en.wikipedia.org/wiki/Code_golf)，不过编程语言是 Vim 的用户界面
- [Vi/Vim Stack Exchange](https://vi.stackexchange.com/)
- [Vim Screencasts](http://vimcasts.org/)
- [Practical Vim](https://pragprog.com/titles/dnvim2/)（书）

[Vim]: https://www.vim.org/

# 代码智能与语言服务器

IDE 通常会通过连接到实现 [语言服务器协议](https://microsoft.github.io/language-server-protocol/) 的_语言服务器_（Language Server）来提供需要代码语义理解的 IDE 扩展，从而实现语言专属的支持。例如，[VS Code 的 Python 扩展](https://marketplace.visualstudio.com/items?itemName=ms-python.python)依赖 [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)，[VS Code 的 Go 扩展](https://marketplace.visualstudio.com/items?itemName=golang.go) 则依赖官方的 [gopls](https://go.dev/gopls/)。通过安装你常用语言的扩展和语言服务器，你可以在 IDE 中启用许多语言专属功能，例如：

- **代码补全**。更好的自动补全和自动建议，例如在输入 `object.` 后能够看到对象的字段和方法。
- **内联文档**。悬停时查看文档和自动建议。
- **跳转至定义**。从使用处跳转到定义处，例如从字段引用 `object.field` 跳转到字段的定义。
- **查找引用**。与上述操作相反，找到引用了特定项（如字段或类型）的所有位置。
- **导入帮助**。组织导入、删除未使用的导入、标记缺失的导入。
- **代码质量**。这些工具可以独立使用，但语言服务器也通常提供此类功能。代码格式化可以自动缩进和格式化代码，类型检查器和 linter 可以逐行查找代码中的错误。我们将在 [关于代码质量的讲义](/2026/code-quality/) 中更深入地讨论这类功能。

## 配置语言服务器

对于某些语言，你所需要做的就是安装扩展和语言服务器，一切即可开箱即用。而对于其他语言，为了从语言服务器中获得最大收益，你需要向 IDE 展示你的开发环境。例如，将 VS Code 指向你的 [Python 环境](https://code.visualstudio.com/docs/python/environments) 可以让语言服务器识别你已安装的包。环境相关内容在我们的 [打包与分发代码的讲义](/2026/shipping-code/) 中有更深入的讨论。

根据语言的不同，你可能还需要为语言服务器配置一些设置。例如，在使用 VS Code 的 Python 支持时，你可以为不使用 Python 可选类型注解的项目禁用静态类型检查。

# AI 驱动的开发

自 2021 年中 GitHub 基于 OpenAI 的 [Codex 模型](https://openai.com/index/openai-codex/)推出了 [GitHub Copilot][github-copilot] 以来，[LLM](https://en.wikipedia.org/wiki/Large_language_model)（大型语言模型）已经在软件工程中被广泛采用。目前主要有三种主要形态：自动补全、行内对话和编码智能体。

[github-copilot]: https://github.com/features/copilot/ai-code-editor

## 自动补全

AI 驱动的自动补全与你 IDE 中的传统自动补全具有相同的使用形式——在输入过程中于光标位置建议补全内容。有时，它被当作一个"开箱即用"的被动功能使用。除此之外，AI 自动补全通常会利用代码注释来进行 [prompt 引导](https://en.wikipedia.org/wiki/Prompt_engineering)。

例如，让我们写一个脚本来下载这些讲义的内容并提取所有链接。我们可以先写下：

```python
import requests

def download_contents(url: str) -> str:
```

模型将自动补全函数体：

```python
    response = requests.get(url)
    return response.text
```

我们可以用注释进一步引导补全。例如，如果我们开始编写一个提取所有 Markdown 链接的函数，但它没有特别描述性的名称：

```python
def extract(contents: str) -> list[str]:
```

模型会补全为类似这样的内容：

```python
    lines = contents.splitlines()
    return [line for line in lines if line.strip()]
```

我们可以通过代码注释来引导补全：

```python
def extract(content: str) -> list[str]:
    # extract all Markdown links from the content
```

这一次，模型给出了更好的补全：

```python
    import re
    pattern = r'\[.*?\]\((.*?)\)'
    return re.findall(pattern, content)
```

这里我们看到了这类 AI 编码工具的一个缺点：它只能在光标处提供补全。在这种情况下，更好的做法是将 `import re` 放在模块级别而不是函数内部。

上面的例子用了一个命名不佳的函数来演示如何用注释引导代码补全；在实际使用中，你应当编写命名更具描述性的函数（如 `extract_links`），并撰写 docstring（有了 docstring 之后，模型应能生成与上述补全类似的输出）。

为了演示的目的，我们可以完成整个脚本：

```python
print(extract(download_contents("https://raw.githubusercontent.com/missing-semester/missing-semester/refs/heads/master/_2026/development-environment.md")))
```

## 行内对话

行内对话（Inline chat）允许你选中一个行或代码块，然后直接向 AI 模型发出提示以提出编辑建议。在这种交互模式中，模型可以修改现有代码（这与自动补全不同，后者只会在光标之后补全代码）。

继续上面的例子，假设我们决定不使用第三方 `requests` 库。我们可以选中相关的三行代码，调用行内对话，并输入类似：

```
use built-in libraries instead
```

模型会提出如下修改：

```python
from urllib.request import urlopen

def download_contents(url: str) -> str:
    with urlopen(url) as response:
        return response.read().decode('utf-8')
```

## 编码智能体

编码智能体在 [Agentic Coding](/2026/agentic-coding/) 讲义中有深入讨论。

## 推荐的软件

一些流行的 AI IDE 包括：配合 [GitHub Copilot][github-copilot] 扩展使用的 [VS Code][vs-code]，以及 [Cursor](https://cursor.com/)。GitHub Copilot 目前[对学生免费](https://github.com/education/students)，对教师和有影响力的开源项目维护者也可免费使用。这是一个快速演进的领域，许多领先产品提供的功能大致相当。

# 扩展与其他 IDE 功能

IDE 是强大的工具，_扩展_（Extensions）让它们更加强大。我们无法在一讲中覆盖所有功能，但下面是一些热门扩展的指引。我们鼓励你自行探索这一领域——网上有许多热门 IDE 扩展的列表，例如 [Vim Awesome](https://vimawesome.com/)（Vim 插件）和 [按受欢迎程度排序的 VS Code 扩展](https://marketplace.visualstudio.com/search?target=VSCode&category=All%20categories&sortBy=Installs)。

- [开发容器](https://containers.dev/)：由主流 IDE 支持（例如 [VS Code 已支持](https://code.visualstudio.com/docs/devcontainers/containers)），开发容器允许你使用容器来运行开发工具。这在可移植性或隔离方面可能很有帮助。[打包与分发代码的讲义](/2026/shipping-code/) 中有更深入的容器内容。
- 远程开发：使用 SSH 在远程机器上进行开发（例如，使用 [VS Code 的 Remote SSH 插件](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)）。例如，如果你想在一台云端的强 GPU 机器上开发和运行代码，这种方式就非常方便。
- 协作编辑：以 Google Docs 的方式协作编辑同一文件（例如，使用 [VS Code 的 Live Share 插件](https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare)）。

# 练习

1. 在你使用的所有支持它的软件（如编辑器和 shell）中启用 Vim 模式，并在接下来的一个月里用 Vim 模式完成所有文本编辑工作。每当觉得哪里效率不高，或者想到"应该有更好的方法"时，尝试去搜索一下——很可能真的有更好的方法。
1. 完成 [VimGolf](https://www.vimgolf.com/) 上的一个挑战。
1. 为你正在使用的项目配置一个 IDE 扩展和语言服务器。确保所有预期功能（例如，对库依赖的跳转至定义）都能正常工作。如果你没有可以使用的代码来做这个练习，可以选用 GitHub 上的某个开源项目（如 [这个](https://github.com/spf13/cobra)）。
1. 浏览一份 IDE 扩展列表，安装一个对你有用的扩展。