---
layout: lecture
title: "问答"
description: >
  回答学生关于操作系统、Shell 脚本、工具推荐等主题的问题。
thumbnail: /static/assets/thumbnails/2020/lec11.png
date: 2020-01-30
ready: true
video:
  aspect: 56.25
  id: Wz50FvGG6xU
special: true
---

在最后一讲中，我们回答了同学们提交的问题：

- [学习进程、虚拟内存、中断、内存管理等操作系统相关知识有什么推荐？](#learning-processes-virtual-memory-interrupts-memory-management-etc)
- [哪些工具最值得优先学习？](#prioritize-learning-first)
- [什么时候该用 Python，什么时候用 Bash 脚本，什么时候用其他语言？](#when-do-i-use-python-versus-bash)
- [`source script.sh` 和 `./script.sh` 有什么区别？](#source-vs-scriptsh)
- [各种包和工具存放在哪里？引用它们是怎么工作的？`/bin` 或 `/lib` 到底是什么？](#what-are-the-places-where-various-packages-and-tools-are-stored)
- [我应该用 `apt-get install` 装 python-whatever，还是用 `pip install` 装那个包？](#apt-get-vs-pip)
- [提升代码性能最容易也最有效的性能分析（profiling）工具有哪些？](#profiling-tools)
- [你们都用哪些浏览器插件？](#browser-plugins)
- [还有哪些有用的数据整理工具？](#data-wrangling-tools)
- [Docker 和虚拟机有什么差别？](#docker-vs-vm)
- [各操作系统有什么优缺点？我们该如何选择（比如选择最适合自己用途的 Linux 发行版）？](#choosing-os)
- [Vim 还是 Emacs？](#vim-vs-emacs)
- [机器学习应用有什么技巧或窍门？](#ml-tips)
- [还有更多 Vim 技巧吗？](#more-vim-tips)
- [什么是双因素认证（2FA）？为什么我应该使用它？](#what-is-2fa)
- [对浏览器之间的差异有什么看法？](#browser-differences)

## 学习进程、虚拟内存、中断、内存管理等操作系统相关知识有什么推荐？ {: #learning-processes-virtual-memory-interrupts-memory-management-etc}

首先，你实际上是否需要非常熟悉所有这些主题，其实并不明确，因为它们都是非常底层的主题。当你开始编写更多底层代码（比如实现或修改内核）时，这些知识才会发挥作用。除此之外，大多数主题并不会与你相关；例外是进程和信号（在之前的讲座中有简要介绍过）。

一些学习本主题的好资源：

- [MIT 的 6.828 课程](https://pdos.csail.mit.edu/6.828/) — 操作系统工程研究生课程。课程资料对外公开。
- Modern Operating Systems（第 4 版）— Andrew S. Tanenbaum 著，对前面提到的许多概念有很好的概述。
- The Design and Implementation of the FreeBSD Operating System — 关于 FreeBSD 操作系统的优秀资料（注意，这不是 Linux）。
- 其他指南，比如 [Writing an OS in Rust](https://os.phil-opp.com/)，人们用各种语言逐步实现一个内核，主要面向教学目的。


## 哪些工具最值得优先学习？ {: #prioritize-learning-first}

有些值得优先关注的主题：

- 学会更多地使用键盘、少用鼠标。这可以通过键盘快捷键、更换界面等方式实现。
- 好好掌握编辑器。作为一名程序员，你大部分时间都在编辑文件，所以掌握这项技能绝对物超所值。
- 学会自动化和（或）简化工作流中重复性的任务，因为这样节省的时间将是巨大的……
- 学习像 Git 这样的版本控制工具，以及如何在现代软件项目中将它与 GitHub 配合协作。

## 什么时候该用 Python，什么时候用 Bash 脚本，什么时候用其他语言？ {: #when-do-i-use-python-versus-bash}

一般而言，Bash 脚本适用于简短、简单的单次脚本，你只是想按顺序执行一组命令时使用。Bash 存在一些缺陷，使得它在处理更大的程序或脚本时很不好用：

- Bash 对于简单用例很容易写对，但对于所有可能的输入要想写对就很难。比如，脚本参数中的空格就会导致无数 Bash 脚本 bug。
- Bash 不利于代码复用，因此你很难复用之前写过的程序的组件。更广泛地说，Bash 中没有软件库的概念。
- Bash 依赖许多魔法字符串（magic strings），比如 `$?` 或 `$@` 来引用特定值，而其它语言则会显式地引用，例如 `exitCode` 或 `sys.args`。

因此，对于更大、更复杂的脚本，我们推荐使用更成熟的脚本语言，比如 Python 或 Ruby。你可以在网上找到无数别人已经编写好的库，用来解决这些语言中的常见问题。如果你在某种语言中找到了实现你所关注功能的库，通常最好的做法就是直接使用该语言。

## `source script.sh` 和 `./script.sh` 有什么区别？ {: #source-vs-scriptsh}

在两种情况下，`script.sh` 都会被读取并在一个 bash 会话中执行，区别在于**哪个会话**在运行这些命令。

对于 `source`，命令会在你**当前**的 bash 会话中执行，因此任何对当前环境的修改——比如改变目录或定义函数——一旦 `source` 命令执行完毕，都会在当前会话中保留下来。

当以 `./script.sh` 的方式独立运行脚本时，你当前的 bash 会话会启动 bash 的一个新实例，由该新实例来运行 `script.sh` 中的命令。因此，如果 `script.sh` 改变了目录，那么新的 bash 实例确实会改变目录，但一旦它退出并把控制权交还给父 bash 会话，父会话仍然停留在原来的位置。

同理，如果 `script.sh` 定义了一个你希望在终端中使用的函数，你需要 `source` 它，这样函数才会定义在你当前的 bash 会话中。否则，如果你直接运行脚本，实际处理该函数定义的将是新创建的 bash 进程，而不是你当前的 shell。

## 各种包和工具存放在哪里？引用它们是怎么工作的？`/bin` 或 `/lib` 到底是什么？ {: #what-are-the-places-where-various-packages-and-tools-are-stored}

关于你在终端中执行的程序，它们都存放在你的 `PATH` 环境变量所列出的目录中。你可以使用 `which` 命令（或 `type` 命令）来检查你的 shell 在何处找到了某个特定的程序。

一般来说，某些特定类型的文件住在哪里有一些约定。以下是我们讨论过的一些目录，更完整的列表请查看 [文件系统层次标准（Filesystem Hierarchy Standard）](https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard)。

- `/bin` — 必备命令（essential command）的二进制文件
- `/sbin` — 必备系统二进制文件，通常以 root 身份运行
- `/dev` — 设备文件，通常是硬件接口的特殊文件
- `/etc` — 主机特定的、系统范围的配置文件
- `/home` — 系统中用户的家目录
- `/lib` — 系统程序常用的库文件
- `/opt` — 可选的应用软件
- `/sys` — 包含系统信息和配置（详见 [第一讲](/2020/course-shell/)）
- `/tmp` — 临时文件（也有 `/var/tmp`）。通常在重启时被清除。
- `/usr/` — 只读的用户数据
  + `/usr/bin` — 非必备命令的二进制文件
  + `/usr/sbin` — 非必备系统二进制文件，通常以 root 身份运行
  + `/usr/local/bin` — 用户编译程序的二进制文件
- `/var` — 可变文件，比如日志或缓存

## 我应该用 `apt-get install` 装 python-whatever，还是用 `pip install` 装那个包？ {: #apt-get-vs-pip}

这个问题没有统一的答案。它关联到一个更一般的问题：你该用系统的包管理器，还是用语言特定的包管理器来安装软件。以下几点供参考：

- 常用包通常两者都有，但不那么流行或更近期的包可能在你系统的包管理器中不可用。这种情况下使用语言特定的工具是更好的选择。
- 同理，语言特定的包管理器通常拥有比系统包管理器更新版本的软件包。
- 使用系统包管理器时，库将被安装到系统全局。这意味着如果你出于开发需要不同版本的库，系统包管理器可能无法满足。对于这种情况，大多数编程语言都提供了某种形式的隔离或虚拟环境（isolated / virtual environment），让你可以安装不同版本的库而不会发生冲突。对于 Python，有 virtualenv；对于 Ruby，有 RVM。
- 根据操作系统和硬件架构的不同，这些包可能附带二进制文件，也可能需要编译。例如，在树莓派等 ARM 计算机上，如果系统包管理器提供的是二进制文件而语言特定的包管理器需要编译，那么使用系统包管理器会更好。这高度依赖于你的具体设置。

你应当尝试使用其中一种方案，而不是两种都用，因为这可能导致难以调试的冲突。我们的建议是：尽可能使用语言特定的包管理器，并使用隔离环境（比如 Python 的 virtualenv）来避免污染全局环境。

## 提升代码性能最容易也最有效的性能分析（profiling）工具有哪些？ {: #profiling-tools}

最容易上手且相当有用的性能分析工具是 [计时输出法（print timing）](/2020/debugging-profiling/#timing)。你只需手动计算代码不同部分之间所花费的时间。通过反复这样做，你可以对代码进行二分查找，定位耗时最长的代码段。

对于更高级的工具，Valgrind 的 [Callgrind](https://valgrind.org/docs/manual/cl-manual.html) 可以运行你的程序，测量每一件事耗时多少以及所有的调用栈（call stacks），即哪个函数调用了哪个其他函数。然后它会生成一份带标注的程序源代码版本，标出每一行所花的时间。然而，它会让你的程序慢一个数量级，并且不支持线程。对于其他情况，[`perf`](https://www.brendangregg.com/perf.html) 工具和语言特定的采样分析器（sampling profilers）可以快速输出有用的数据。[火焰图（Flamegraphs）](https://www.brendangregg.com/flamegraphs.html) 是对这类采样分析器输出的优秀可视化工具。你还应该尝试针对你所使用的编程语言或任务使用专门的工具。例如，在 Web 开发中，Chrome 和 Firefox 内置的开发工具（dev tools）拥有非常出色的分析器。

有时，代码的慢是因为你的系统在等待某个事件，比如磁盘读取或网络数据包。在这些情况下，检查一下关于理论速度的粗略硬件计算与实际读数是否偏差过大是值得一做的。还有一些专门的工具来分析系统调用（system call）的等待时间。其中包含像 [eBPF](https://www.brendangregg.com/blog/2019-01-01/learn-ebpf-tracing.html) 这样的工具，可以对用户程序进行内核追踪（kernel tracing）。特别是 [`bpftrace`](https://github.com/iovisor/bpftrace)，如果你需要做这种低层级的分析，非常值得了解。


## 你们都用哪些浏览器插件？ {: #browser-plugins}

以下是一些我们最喜欢的插件，大多与安全性和可用性相关：

- [uBlock Origin](https://github.com/gorhill/uBlock) — 一个[多模式（wide-spectrum）](https://github.com/gorhill/uBlock/wiki/Blocking-mode) 拦截器，它不只是拦截广告，还会拦截页面上可能尝试的所有第三方通信。这也包括内联脚本和各类资源加载。如果你愿意花时间配置让它正常工作，可以尝试 [中等模式（medium mode）](https://github.com/gorhill/uBlock/wiki/Blocking-mode:-medium-mode) 甚至 [高级模式（hard mode）](https://github.com/gorhill/uBlock/wiki/Blocking-mode:-hard-mode)。这些模式会让你访问的某些网站无法工作，直到你调整了足够多的设置，但同时也将显著提升你的在线安全。如果不想折腾，[简易模式（easy mode）](https://github.com/gorhill/uBlock/wiki/Blocking-mode:-easy-mode) 已经是一个很好的默认设置，可以拦截大多数广告和跟踪。你也可以自定义规则，决定要拦截哪些网站对象。
- [Stylus](https://github.com/openstyles/stylus/) — Stylish 的一个分支（不要用 Stylish，它曾被曝光会[窃取用户的浏览历史](https://www.theregister.co.uk/2018/07/05/browsers_pull_stylish_but_invasive_browser_extension/)），允许你为网站加载自定义 CSS 样式表。通过 Stylus，你可以轻松自定义和修改网站的外观，比如移除侧边栏、更改背景色，甚至调整文字大小或字体。这对于让你经常访问的网站更易读非常有用。此外，Stylus 可以查找其他用户编写并发布在 [userstyles.org](https://userstyles.org/) 上的样式。比如大多数常见网站都有一到多个暗色主题的样式表。
- 整页截图 — [Firefox 内置](https://screenshots.firefox.com/) 以及 [Chrome 扩展](https://chrome.google.com/webstore/detail/full-page-screen-capture/fdpohaocaechififmbbbbbknoalclacl?hl=en)。可以截取整张网页的截图，通常比打印更适合做参考。
- [Multi Account Containers（多账户容器）](https://addons.mozilla.org/en-US/firefox/addon/multi-account-containers/) — 允许你将 cookie 分离到不同的"容器"中，让你以不同的身份浏览网页，并（或）确保网站之间无法相互共享信息。
- 密码管理器集成 — 大多数密码管理器都有浏览器扩展，使得向网站输入凭证不仅更方便，也更加安全。与简单复制粘贴用户名和密码相比，这些工具会首先检查网站域名是否与条目中列出的域名匹配，从而防止伪装成热门网站的钓鱼攻击。
- [Vimium](https://github.com/philc/vimium) — 一款浏览器扩展，在 Vim 编辑器的精神指引下，为网页提供基于键盘的导航和控制。

## 还有哪些有用的数据整理工具？ {: #data-wrangling-tools}

我们在数据整理讲座中没有足够时间覆盖的一些数据整理工具包括 `jq` 或 `pup`，它们分别是为 JSON 和 HTML 数据设计的专用解析器。Perl 编程语言也是更复杂的数据整理流水线的另一个好工具。还有一个技巧是使用 `column -t` 命令，可以将空白字符分隔的文本（不一定对齐）转换为列对齐的文本。

更广泛地说，vim 和 Python 是两个更另类的数据整理工具。对于某些复杂的多行转换，vim 的宏（macros）可以是一个非常有价值的工具。你可以记录一系列操作并按需重复执行，比如在编辑器的 [讲座笔记](/2020/editors/#macros)（以及去年 [视频](/2019/editors/)）中，有一个仅使用 vim 宏将 XML 格式文件转换为 JSON 的例子。

对于表格数据（通常以 CSV 呈现），[pandas](https://pandas.pydata.org/) Python 库是一个很棒的工具。它不仅让你能够相当轻松地定义诸如 group by、join 或 filter 这样的复杂操作，而且也非常便于对数据的不同属性进行绘图。它还支持导出为多种表格格式，包括 XLS、HTML 或 LaTeX。作为替代，R 编程语言（有人认为是个 [烂](https://arrgh.tim-smith.us/)语言）拥有大量在数据上计算统计信息的功能，可以很实用地作为流水线（pipeline）的最后一步。[ggplot2](https://ggplot2.tidyverse.org/) 是 R 中一个非常出色的绘图库。

## Docker 和虚拟机有什么差别？ {: #docker-vs-vm}

Docker 基于一个更通用的概念——容器（containers）。容器和虚拟机（Virtual Machine, VM）之间的主要区别在于：虚拟机将执行整个操作系统栈，包括内核，即使内核与宿主机（host）的内核相同也不会有区别。与虚拟机不同，容器不需要再运行一个额外的内核实例，而是与宿主机共享同一个内核。在 Linux 中，这一机制称为 LXC，它使用了一系列隔离机制来启动一个程序——这个程序以为自己运行在独立的硬件上，但实际上它与宿主机共享硬件和内核。因此，容器的开销比完整的虚拟机更低。

反过来说，容器的隔离性较弱，并且仅当宿主机运行相同的内核时才能工作。例如，如果你在你的 macOS 上运行 Docker，Docker 需要启动一个 Linux 虚拟机来获取初始的 Linux 内核，因此开销仍然比较大。最后，Docker 是容器的一个具体实现，它针对软件部署进行了量身定制。正因如此，它有一些独特之处：例如，Docker 容器默认在重启之间不会持久化任何形式的存储。

## 各操作系统有什么优缺点？我们该如何选择（比如选择最适合自己用途的 Linux 发行版）？ {: #choosing-os}

关于 Linux 发行版，尽管发行版数量众多，对于大多数用途，它们的表现基本一致。大多数 Linux 和 UNIX 的特性及内部机制可以在任何发行版上学到。

发行版之间一个根本性的区别是它们如何处理软件包更新。一些发行版，比如 Arch Linux，采用滚动更新（rolling update）策略——软件始终处于最前沿，但时不时会出现问题。另一方面，一些发行版如 Debian、CentOS 或 Ubuntu LTS 版本在仓库中发布更新时则保守得多，因此通常更稳定，代价是牺牲了较新的功能。

对于桌面和服务器的易使用和稳定性体验，我们推荐使用 Debian 或 Ubuntu。

Mac OS 在 Windows 和 Linux 之间提供了一个不错的中间点，拥有精致的界面。不过，Mac OS 基于 BSD 而非 Linux，因此系统中的一些部分和命令有所不同。另一个值得了解的替代方案是 FreeBSD。尽管某些程序无法在 FreeBSD 上运行，但 BSD 生态系统的碎片化程度远低于 Linux，文档也更好。

除非你是为了开发 Windows 应用，或者需要某些无法替代的功能（比如良好的游戏驱动支持），否则我们不推荐 Windows。

对于双系统引导（dual boot），我们认为最靠谱的实施方案是 macOS 的 Boot Camp。任何其他组合长期来看都可能出现问题，尤其是如果还结合了磁盘加密等功能。

## Vim 还是 Emacs？ {: #vim-vs-emacs}

我们三人都以 vim 为主要编辑器，但 Emacs 也是不错的选择，值得两者都尝试一下，看哪个更适合你。Emacs 不遵循 vim 的模式编辑（modal editing），但可以通过 Evil（[Evil](https://github.com/emacs-evil/evil)）或 [Doom Emacs](https://github.com/hlissner/doom-emacs) 等 Emacs 插件来启用 vim 式的模式编辑。

使用 Emacs 的一个优势是：扩展可以使用 Lisp 语言来实现——这是一种比 vimscript（Vim 的默认脚本语言）更出色的脚本语言。

## 机器学习应用有什么技巧或窍门？ {: #ml-tips}

这门课的一些理念可以直接应用到机器学习（ML）应用中。与许多科学学科一样，在 ML 中你通常需要执行一系列实验，然后检查哪些方案有效、哪些无效。

你可以使用 shell 工具来快速搜索这些实验，并以合理的方式聚合结果。比如，你可以子集选择特定时间范围内的实验，或者使用了某个特定数据集的实验。通过使用一个简单的 JSON 文件记录实验的所有相关参数，借助本课程中介绍的工具，这项工作会变得非常简单。

最后，如果你没有使用某种集群来提交 GPU 任务，那么你应该研究一下如何自动化这个过程，因为这会是一个相当耗时的任务，而且还会消耗你的精力。

## 还有更多 Vim 技巧吗？ {: #more-vim-tips}

再来几个技巧：

- 插件（Plugins） — 花些时间探索插件生态。有很多很棒的插件可以弥补 vim 的一些不足，或者新增与现有 vim 工作流良好配合的功能。对此，[VimAwesome](https://vimawesome.com/) 和其他程序员的 dotfiles 是很好的资源。
- 标记（Marks） — 在 vim 中，你可以通过 `m<X>`（X 为某个字母）设置一个标记。之后可以通过 `'<X>` 回到该标记位置。这可以让你快速跳转到文件内（甚至跨文件）的特定位置。
- 导航 — `Ctrl+O` 和 `Ctrl+I` 分别让你在你最近访问过的位置之间向后和向前移动。
- 撤销树（Undo Tree） — vim 有一个相当巧妙的变更追踪机制。与其他编辑器不同，vim 存储的是一个变更树，因此即使你撤销后又做了一个不同的变更，你仍然可以通过遍历撤销树回到原始状态。一些插件，比如 [gundo.vim](https://github.com/sjl/gundo.vim) 和 [undotree](https://github.com/mbbill/undotree)，可以以图形化的方式展示这棵撤销树。
- 按时间撤销 — `:earlier` 和 `:later` 命令允许你使用时间引用（而不是逐个撤销）来浏览文件。
- [持久化撤销（Persistent undo）](https://vim.fandom.com/wiki/Using_undo_branches#Persistent_undo) 是 vim 一个令人惊叹的内置功能，但默认是禁用的。它可以在 vim 的不同实例之间持久化撤销历史。在 `.vimrc` 中设置 `undofile` 和 `undodir` 后，vim 会按文件存储变更历史。
- Leader 键 — Leader 键是一个特殊的键，通常留给用户自行配置以用于自定义命令。使用方式通常是按下并释放这个键（通常是空格键），然后再按另一个键来执行某个命令。许多插件利用这个键来添加自己的功能，比如 UndoTree 插件使用 `<Leader> U` 来打开撤销树。
- 高级文本对象（Advanced Text Objects） — 搜索等文本对象也可以与 vim 命令组合使用。例如 `d/<pattern>` 会删除到该模式下一次出现的匹配位置，而 `cgn` 会更改最后一次搜索字符串的下一次出现。

## 什么是双因素认证（2FA）？为什么我应该使用它？ {: #what-is-2fa}

双因素认证（Two Factor Authentication, 2FA）在密码之上为你的账户增加了一层额外的保护。登录时，你不仅需要知道密码，还需要"证明"你能访问某个硬件设备。最简单的方式是在手机上接收短信验证码，不过短信双因素认证存在[已知问题](https://www.kaspersky.com/blog/2fa-practical-guide/24219/)。我们更推荐的一种更好的替代方案是使用 [U2F](https://en.wikipedia.org/wiki/Universal_2nd_Factor) 解决方案，比如 [YubiKey](https://www.yubico.com/)。

## 对浏览器之间的差异有什么看法？ {: #browser-differences}

2020 年当前的浏览器格局是：大多数浏览器都像 Chrome，因为它们使用相同的引擎（Blink）。这意味着 Microsoft Edge（同样基于 Blink）和 Safari（基于与 Blink 相似的引擎 WebKit）不过是 Chrome 的更差版本。Chrome 在性能和可用性方面都是一款相当不错的浏览器。如果你想找替代品，我们的推荐是 Firefox。它在几乎所有方面都可以与 Chrome 相提并论，而且在隐私保护方面表现出色。

另一款名为 [Flow](https://www.ekioh.com/flow-browser/) 的浏览器尚未准备好供用户使用，但它正在实现一个新的渲染引擎，有望比当前引擎更快。