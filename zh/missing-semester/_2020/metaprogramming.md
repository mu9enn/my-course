---
layout: lecture
title: "元编程"
description: >
  了解构建系统、依赖管理、测试和持续集成。
thumbnail: /static/assets/thumbnails/2020/lec8.png
details: 构建系统、依赖管理、测试、持续集成
date: 2020-01-27
ready: true
video:
  aspect: 56.25
  id: _Ms1Z4xfqv4
---

所谓"元编程"（Metaprogramming），其实是我们能想到的最合适的统称——它涵盖的那些事情，更多是关于 _过程_（_process_），而非关于写代码或提高编程效率本身。在本讲中，我们将研究用于构建和测试代码的系统，以及用于管理依赖的工具。你可能觉得这些东西对学生日常学习来说重要性有限，但只要你通过实习或步入"现实世界"与更大的代码库产生交集，你就会无处不在地遇到它们。需要说明的是，"元编程"也可以指 [操作程序的程序](https://en.wikipedia.org/wiki/Metaprogramming)，但本讲使用的定义并不完全等同于那个含义。

# 构建系统

如果你用 LaTeX 写论文，你需要运行哪些命令来生成最终文档？那些用来运行基准测试、绘制图表并把图表插入论文的命令又是什么呢？或者，编译你正在修的课程的示例代码并运行其中的测试呢？

对于大多数项目（无论是否包含代码），都存在一个"构建过程"（_build process_）——你从输入产出输出所需的一系列操作。这个过程往往包含许多步骤，也有许多分支。运行这个来生成某个图表，运行那个来生成结果，再运行其他东西来产出最终论文。就像我们在这门课中反复见到的那样，你不是第一个被这种繁琐过程困扰的人，而且幸运的是，已经有许多工具可以帮助你！

这些工具通常被称为"构建系统"（_build systems_），而且种类繁多。用哪一种取决于手头的任务、你偏好的编程语言以及项目规模。不过它们的核心理念都非常相似：你定义若干 _依赖_（_dependencies_）、若干 _目标_（_targets_），以及从一个到另一个的 _规则_（_rules_）。你告诉构建系统你想要哪个目标，它的职责就是找到该目标的所有传递依赖，然后依次应用规则生成中间目标，直至最终产出目标。理想情况下，构建系统会在依赖未发生变化且结果可从上次构建中获取时，避免不必要地重新执行规则。

`make` 是最常见的构建系统之一，你几乎能在任何基于 UNIX 的机器上找到它。它也有自己的瑕疵，但对于简单到中等规模的项目已经足够好用。当你运行 `make` 时，它会在当前目录查找一个名为 `Makefile` 的文件。所有目标、依赖和规则都在该文件中定义。下面来看一个示例：

```make
paper.pdf: paper.tex plot-data.png
	pdflatex paper.tex

plot-%.png: %.dat plot.py
	./plot.py -i $*.dat -o $@
```

该文件中的每条指令都是一个规则，说明如何使用右侧的依赖生成左侧的目标。换个说法，右侧列出的事物是依赖，左侧是目标。缩进块是一系列用于从这些依赖生成目标的程序。在 `make` 中，第一条指令还定义了默认目标。如果你不带参数运行 `make`，它构建的就是这个目标。另外，你也可以运行类似 `make plot-data.png` 的命令，此时它会改为构建 `plot-data.png` 这个目标。

规则中的 `%` 是一个"模式"（_pattern_），会在左右两侧匹配同一个字符串。例如，如果请求的目标是 `plot-foo.png`，`make` 就会查找依赖 `foo.dat` 和 `plot.py`。现在我们来看看，如果在一个空的源文件目录中运行 `make`，会发生什么。

```console
$ make
make: *** No rule to make target 'paper.tex', needed by 'paper.pdf'.  Stop.
```

`make` 在友好地告诉我们：为了构建 `paper.pdf`，它需要 `paper.tex`，但它没有关于如何生成这个文件的规则。那我们试着来创建它！

```console
$ touch paper.tex
$ make
make: *** No rule to make target 'plot-data.png', needed by 'paper.pdf'.  Stop.
```

有点意思了——确实存在生成 `plot-data.png` 的规则，但那是模式规则。由于源文件不存在（`data.dat`），`make` 只是说它无法生成这个文件。那我们试着创建所有文件：

```console
$ cat paper.tex
\documentclass{article}
\usepackage{graphicx}
\begin{document}
\includegraphics[scale=0.65]{plot-data.png}
\end{document}
$ cat plot.py
#!/usr/bin/env python
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=argparse.FileType('r'))
parser.add_argument('-o')
args = parser.parse_args()

data = np.loadtxt(args.i)
plt.plot(data[:, 0], data[:, 1])
plt.savefig(args.o)
$ cat data.dat
1 1
2 2
3 3
4 4
5 8
```

现在如果运行 `make` 会怎样？

```console
$ make
./plot.py -i data.dat -o plot-data.png
pdflatex paper.tex
... lots of output ...
```

看，它生成了 PDF！如果再次运行 `make` 呢？

```console
$ make
make: 'paper.pdf' is up to date.
```

它什么也没做！为什么？因为它没必要做。它检查了所有已构建的目标相对于其列出的依赖仍然是最新的。我们可以通过修改 `paper.tex` 然后重新运行 `make` 来验证这一点：

```console
$ vim paper.tex
$ make
pdflatex paper.tex
...
```

注意 `make` _没有_ 重新运行 `plot.py`，因为没有这个必要——`plot-data.png` 的任何依赖都没有改变！

> 译者补充：在 Makefile 中，`$@` 表示规则左侧的目标名称，`$*` 表示模式 `%` 匹配到的字符串。所以上面示例中，当目标为 `plot-foo.png` 时，`$@` = `plot-foo.png`，`$*` = `foo`，整条规则展开为 `./plot.py -i foo.dat -o plot-foo.png`。

# 依赖管理

在更宏观的层面，你的软件项目很可能包含 _本身也是项目_ 的依赖。你可能依赖于已安装的程序（如 `python`）、系统包（如 `openssl`）或编程语言内的库（如 `matplotlib`）。如今，大多数依赖都可以通过一个 _仓库_（_repository_）获取，它将大量此类依赖集中托管在一个地方，并提供方便的安装机制。一些例子包括通过 `apt` 工具访问的 Ubuntu 系统包仓库、RubyGems（用于 Ruby 库）、PyPI（用于 Python 库），或 Arch User Repository（用于 Arch Linux 用户提交的软件包）。

由于与这些仓库交互的具体机制因仓库和工具而异，本讲不会深入任何一个具体仓库的细节。我们 _将_ 涵盖的是它们共同使用的一些常见术语。其中首要的是 _版本管理_（_versioning_）。大多数其他项目会依赖的那些项目，在每次发布时都会附带一个 _版本号_（_version number_），类似于 `8.1.3` 或 `64.1.20192004`。它们通常（但不总是）是数值形式的。版本号有多种用途，其中最重要的一项是确保软件持续可用。试想这样一个场景：我发布了我库的一个新版本，其中重命名了一个特定函数。如果我在那个更新发布之后有人尝试构建依赖我这个库的软件，构建可能会失败，因为它调用的函数已经不存在了！版本管理的思路是，让一个项目声明它依赖于另一个项目的特定版本或版本范围，从而即使底层库发生了变化，依赖软件也可以通过使用旧版本的库来继续构建。

但这还不够理想！假如我发布了一个安全更新，它 _没有_ 改变我的库的公开接口（"API"），而所有依赖旧版本的项目都应该立即开始使用它，这又该怎么办呢？这就是版本号中不同数字分组存在的意义。每个数字的具体含义因项目而异，但一个相对通用的标准是 [_语义化版本_（_Semantic Versioning_）](https://semver.org/)。语义化版本中，每个版本号的形式为 `主版本号.次版本号.修订号`（major.minor.patch）。规则如下：

 - 如果新发行版 _没有_ 改变 API，增加 _修订号_。
 - 如果你以 _向后兼容_ 的方式 _添加_ 到 API，增加 _次版本号_。
 - 如果你以 _不向后兼容_ 的方式 _更改_ API，增加 _主版本号_。

这已经带来了一些重大优势。现在，如果我的项目依赖你的项目，只要你的项目次版本号不低于我当时开发时使用的版本，使用与你构建时相同主版本号下最新发布版应该是安全的。换句话说，如果我的项目依赖你的库版本 `1.3.7`，那么用 `1.3.8`、`1.6.1` 甚至 `1.3.0` 来构建 _应该_ 没问题。版本 `2.2.4` 恐怕就不行了，因为主版本号增加了。我们可以看到 Python 的版本号中语义化版本的例子。很多人可能都知道 Python 2 和 Python 3 的代码混用起来不太顺利，这就是为什么那是一个 _主_ 版本号的跃升。同样，用 Python 3.5 编写的代码可能在 Python 3.7 上运行良好，但在 3.4 上就不一定了。

在使用依赖管理系统时，你可能还会遇到 _锁文件_（_lock file_）的概念。锁文件只是一个列出了你 _当前_ 依赖的每个依赖的确切版本的文件。通常，你需要显式运行一个更新程序来升级到依赖的新版本。这样做的原因有很多，比如避免不必要的重新编译、拥有可重复的构建，或自动不更新到最新版本（可能已损坏）。这类依赖锁定的一种极端形式是 _依赖内置_（_vendoring_），即你把你所有依赖的代码复制到你自己项目中。这让你对它们的任何变更拥有完全控制权，也可以引入你自己的修改，但也意味着你需要随时间显式地从上游维护者那里拉取任何更新。

# 持续集成系统

随着你处理的项目越来越大，你会发现每次对项目做出改动时，通常还有一些额外的任务需要完成。你可能需要上传文档的新版本、在某个地方上传编译后的版本、将代码发布到 PyPI、运行你的测试套件，以及各种其他事情。也许每次有人向你发送 GitHub 上的 PR（_pull request_），你都希望他们的代码通过风格检查，并运行一些基准测试？当这类需求出现时，就该考虑持续集成了。

持续集成（_Continuous Integration_，简称 CI）是"每当你的代码发生变化时就运行某些东西"的统称，市面上有许多公司提供免费（尤其是对开源项目）的 CI 服务。其中一些大厂商包括 Travis CI、Azure Pipelines 和 GitHub Actions。它们的工作原理大致相同：你在仓库中添加一个文件，描述当仓库发生各种事件时应该发生什么。其中最常见的一种规则是"当有人推送代码时，运行测试套件"。当事件触发时，CI 提供者会启动虚拟机（或多个），在您的"配方"中运行命令，然后通常将结果记录在某处。你可以将它配置为在测试套件不再通过时通知你，或者在测试通过时在仓库中显示一个小徽章。

作为 CI 系统的一个示例，本课的网站是使用 GitHub Pages 搭建的。Pages 是一个 CI 操作，会在每次推送到 `master` 分支时运行 Jekyll 博客软件，并在特定的 GitHub 域名上提供构建后的站点。这使得我们更新网站变得非常简单——我们只需在本地做出更改，用 git 提交，然后推送。CI 会处理其余一切。

## 关于测试的简要说明

大多数大型软件项目都带有"测试套件"（_test suite_）。你可能已经熟悉测试的一般概念，但这里我们快速提及一些你在实践中可能遇到的测试方法和测试术语：

 - 测试套件（Test suite）：所有测试的统称。
 - 单元测试（Unit test）：针对某一特定功能、在隔离环境下进行的"微测试"。
 - 集成测试（Integration test）：运行系统更大一部分的"宏观测试"，用于检查不同功能或组件是否 _能够一起_ 正常工作。
 - 回归测试（Regression test）：实现一个 _之前_ 导致过 bug 的特定模式的测试，以确保该 bug 不再出现。
 - 模拟（Mocking）：用一个假的实现来替换某个函数、模块或类型，从而避免测试无关的功能。例如，你可以"模拟网络"或"模拟磁盘"。

# 练习

 1. 大多数 Makefile 都提供了一个名为 `clean` 的目标。这个目标并非用来生成名为 `clean` 的文件，而是用来清理那些可以被 `make` 重新构建的所有文件。可以把它看作一种"撤销"所有构建步骤的方式。为上面 `paper.pdf` 的 `Makefile` 实现一个 `clean` 目标。你须要使该目标成为[伪目标（_phony_）](https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html)。你可能会发现 [`git ls-files`](https://git-scm.com/docs/git-ls-files) 子命令很有用。下面列出了许多其他非常常见的 make 目标：[链接](https://www.gnu.org/software/make/manual/html_node/Standard-Targets.html#Standard-Targets)。
 2. 查看 [Rust 的构建系统](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html) 中用于为依赖指定版本要求的各种方式。大多数软件包仓库都支持类似的语法。针对每一种（caret、tilde、通配符、比较和多个版本），试着设想一个使用该类型要求的适用场景。
 3. Git 本身就可以充当一个简单的 CI 系统。在任何 git 仓库的 `.git/hooks` 中，你会找到（当前未激活的）文件，在特定事件发生时它们会作为脚本被运行。编写一个 [`pre-commit`](https://git-scm.com/docs/githooks#_pre_commit) 钩子，让它运行 `make paper.pdf`，并在 `make` 命令失败时拒绝提交。这样可以防止任何提交包含一个无法构建的论文版本。
 4. 使用 [GitHub Pages](https://pages.github.com/) 设置一个简单的自动发布页面。给仓库添加一个 [GitHub Action](https://github.com/features/actions)，用于对仓库中所有的 shell 文件运行 `shellcheck`（[一种实现方式](https://github.com/marketplace/actions/shellcheck)）。验证它是否正常工作！
 5. [自己构建](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/building-actions) 一个 GitHub action，用于对仓库中所有 `.md` 文件运行 [`proselint`](https://github.com/amperser/proselint) 或 [`write-good`](https://github.com/btford/write-good)。在仓库中启用它，并通过提交一个包含拼写错误的 pull request 来验证它是否正常工作。

<!-- 译者新增自测题 -->

 6. 假设你在一个 Python 项目中使用了依赖锁定（lock file），某一天你运行了 `pip install --upgrade` 来更新依赖。解释为什么这可能引入构建不可复现的问题，以及如何避免它。
 7. 在一个 Makefile 中，如果两个目标（例如 `all` 和 `clean`）都不对应真实的磁盘文件，为什么还需要将它们的依赖标记为 `.PHONY`？