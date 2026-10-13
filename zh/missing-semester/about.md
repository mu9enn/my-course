---
layout: lecture
title: "我们为什么要开设这门课"
---

在传统计算机科学（CS）教育中，你很可能会上很多课，学到 CS 领域的各种高阶主题——从操作系统到编程语言，再到机器学习。但在许多院校中，有一个至关重要的主题很少被纳入教学，往往被留给学生自己去摸索：计算生态素养（computing ecosystem literacy）。

多年来，我们曾在 MIT 协助教授多门课程，一遍又一遍地看到，许多学生对他们可用的工具知之甚少。计算机的初衷是自动化手动任务，然而学生却常常亲自执行重复性操作，或者未能充分利用版本控制和文本编辑器这样强大的工具。最好的情况下，这只会导致低效和时间浪费；最坏的情况下，则会引发数据丢失，或导致某些任务根本无法完成。

这些主题并未包含在大学课程体系中：学生从未被教导如何使用这些工具，或者至少没有被教导如何 _高效地_ 使用它们，因而把时间和精力浪费在 _本应简单_ 的任务上。标准的计算机科学课程缺少了关于计算生态的关键内容，而这些内容本可以让学生的学习和生活变得轻松得多。

# 你 CS 教育中缺失的那个学期

为了弥补这一不足，我们开设了一门涵盖所有我们认为对成为一名高效计算机科学家和程序员至关重要的主题的课程。这门课注重实用和动手实践，对各类工具和技术进行手把手介绍，你可以立刻将它们应用在自己将遇到的各种场景中。本次课程的最新一版对教材做了大幅度修订，将于 2026 年 1 月在 MIT 的"独立活动期"（Independent Activities Period, IAP）开讲——这是为期一个月的学期，其中包含由学生主导的短课程。虽然讲座本身仅对 MIT 社区开放，但我们会向公众提供全部讲义材料和课程录像。

如果你觉得自己可能会感兴趣，下面是一些课程所覆盖内容的具体示例：

## 命令 shell

如何使用别名（aliases）、脚本和构建系统来自动化常见的和重复性任务。不再需要从一个文本文档中逐条复制粘贴命令。不再需要"挨个运行这 15 条命令"。不再因为"你忘了跑这个"或"你忘了传这个参数"而懊恼。

例如，快速搜索命令历史记录可以帮你省下大量时间。下面的示例展示了几个与在 shell 历史中查找 `convert` 命令相关的技巧。

<video autoplay="autoplay" loop="loop" controls muted playsinline  oncontextmenu="return false;"  preload="auto"  class="demo">
  <source src="/static/media/demos/history.mp4" type="video/mp4">
</video>

## 版本控制

如何 _正确地_ 使用版本控制，并利用它来帮你脱离困境、与他人协作、快速定位和隔离问题变更。不再需要 `rm -rf; git clone` 来恢复项目。不再有合并冲突（好吧，至少会少一些）。不再出现一大片注释掉的代码。不再为"到底是什么改坏了我的代码"而发愁。不再担心"天哪，我们是不是把能跑通的代码删掉了？！" 我们还会教你如何通过 Pull Request 为别人的项目做出贡献！

在下面的示例中，我们使用 `git bisect` 来定位导致单元测试失败的提交，然后使用 `git revert` 修复它。

<video autoplay="autoplay" loop="loop" controls muted playsinline  oncontextmenu="return false;"  preload="auto"  class="demo">
  <source src="/static/media/demos/git.mp4" type="video/mp4">
</video>

## 文本编辑

如何高效地在命令行中编辑文件（无论是本地还是远程），并利用编辑器的进阶功能。不再需要在文件之间来回复制粘贴。不再有机械式的重复编辑。

Vim 宏（macros）是它最出色的功能之一。下面的示例中，我们通过嵌套 Vim 宏快速把一个 HTML 表格转换为 CSV 格式。

<video autoplay="autoplay" loop="loop" controls muted playsinline  oncontextmenu="return false;"  preload="auto"  class="demo">
  <source src="/static/media/demos/vim.mp4" type="video/mp4">
</video>

## 远程机器

如何使用 SSH 密钥和终端复用器（terminal multiplexing）在与远程机器协作时保持清醒的头脑。不再需要打开多个终端窗口，只是为了同时运行两个命令。不再每次连接时都要输入密码。不再因为你断网了或者需要重启笔记本而丢失一切。

下面的示例中，我们使用 `tmux` 在远程服务器上保持会话持续运行，并使用 `mosh` 来支持网络漫游和断线重连。

<video autoplay="autoplay" loop="loop" controls muted playsinline  oncontextmenu="return false;"  preload="auto"  class="demo">
  <source src="/static/media/demos/ssh.mp4" type="video/mp4">
</video>

## 查找文件

如何快速找到你正在查找的文件。不再需要在项目文件中不停地点击，直到找到你需要的代码。

下面的示例中，我们使用 `fd` 快速搜索文件，使用 `rg` 搜索代码片段。我们还通过 `fasd` 快速 `cd` 和 `vim` 打开近期/频繁使用的文件或文件夹。

<video autoplay="autoplay" loop="loop" controls muted playsinline  oncontextmenu="return false;"  preload="auto"  class="demo">
  <source src="/static/media/demos/find.mp4" type="video/mp4">
</video>

## 数据处理

如何直接在命令行中快速且轻松地对数据和文件进行修改、查看、解析、绘图和计算。不再需要把日志文件中的数据复制粘贴出来。不再需要手工计算数据中的统计量。不再用电子表格来作图。

## 代码质量与持续集成

如何使用自动格式化、代码检查（linting）、测试和代码覆盖率工具来提升代码质量。告别丑陋的代码。告别回归问题。告别那种"在你电脑上跑得好好的，在别人电脑上却崩了"的代码。

## 代码之外

如何编写出色的文档、与开源维护者清晰沟通、提交有可操作性的 Issue，以及提交能被合并的 Pull Request。不再有因为不会使用你的软件而困惑的用户。不再有维护者的已读不回。

# 总结

上述内容以及更多主题将在 9 次课程讲座中逐一展开，每次讲座都配有练习，帮助你进一步熟悉这些工具。如果你等不到 2026 年 1 月，也可以先看看[之前版本的课程](/2020/)，其中涵盖了许多相同主题。

希望一月见到你，无论是线上还是线下！

Happy hacking,

[Anish](https://anish.io/), [Jon](https://thesquareplanet.com/), 和 [Jose](https://josejg.com/)