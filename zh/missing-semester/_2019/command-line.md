---
layout: lecture
title: "命令行环境"
presenter: Jose
date: 2019-01-17
order: 1
video:
  aspect: 62.5
  id: i0rf1gpKL1E
---

## 别名与函数

可以想象，反复输入包含大量标志位或冗长选项的长命令是非常令人厌倦的。大多数 **shell（命令行解释器）** 都支持 **别名（alias）**。例如，bash 中的别名结构如下（注意 `=` 两侧不能有空格）：

```bash
alias alias_name="command_to_alias"
```

<!-- We can alias common flags for our commands like `alias ll=ls -ltAh`. Alias can be composed  -->

别名提供了许多便利的功能：

```bash
# 别名可以把合理的默认标志位总结到一起
alias ll="ls -lh"

# 为常用命令大幅减少打字量
alias gc="git commit"

# 别名可以覆盖已有命令
alias mv="mv -i"
alias mkdir="mkdir -p"

# 别名可以组合使用
alias la="ls -A"
alias lla="la -l"

# 在命令前加 \ 可以绕过别名执行
\ls
# 也可以使用 unalias 禁用别名
unalias la

```
<!--
To get rid of an alias you can run `unalias alias_name` or to ignore alias when running a command you can prepend the command with a backward slash `\alias_name`. This is convenient when an alias is overwriting an existing name. -->


然而，在不少场景下，别名会变得很受限，特别是当你试图把多条命令链式组合在一起并让它们共享相同的参数时。另一种选择是 **函数（function）**，它在别名和自定义 shell 脚本之间取得了一个平衡。

下面是一个创建目录并进入该目录的函数示例：

```bash
mcd () {
    mkdir -p $1
    cd $1
}
```

别名和函数默认不会在 shell 会话之间持久保存。要让别名持久生效，你需要将它们写入 shell 的启动脚本文件（如 `.bashrc` 或 `.zshrc`）。我的建议是把它们单独写到一个 `.alias` 文件中，然后在不同的 shell 配置文件中 `source` 这个文件。

<!-- Lastly, if you decide to alias any of these tools with the "improved" version, e.g. `alias bat=cat` it is useful to know that you can tell bash to ignore aliases by doing `\cat` and ignore both aliases and functions by doing `command cat` -->

## shell 与框架

在 shell 与脚本章节中，我们以 `bash` 为例进行讲解，因为它是目前最普遍、几乎所有系统都自带的默认 shell。不过它并非唯一的选择。

例如，`zsh` shell 是 `bash` 的超集，开箱即用地提供了许多便捷功能：

- 更智能的文件名通配（globbing），支持 `**`
- 内联通配符扩展
- 拼写纠正
- 更好的 Tab 补全 / 选择
- 路径展开（输入 `cd /u/lo/b` 会自动展开为 `/usr/local/bin`）

此外，许多 shell 还可以通过 **框架（frameworks）** 进一步提升体验。一些流行的通用框架包括 [prezto](https://github.com/sorin-ionescu/prezto) 和 [oh-my-zsh](https://github.com/robbyrussell/oh-my-zsh)；还有一些专注于特定功能的轻量级框架，例如 [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting) 或 [zsh-history-substring-search](https://github.com/zsh-users/zsh-history-substring-search)。像 [fish](https://fishshell.com/) 这样的 shell 则在默认情况下就内置了大量此类友好特性。这些功能包括：

- 右侧提示符（right prompt）
- 命令语法高亮
- 历史子串搜索
- 基于 manpage 的标志位补全
- 更智能的自动补全
- 提示符主题

使用这些框架时需要注意一点：如果它们运行的代码没有经过良好优化，或者代码量过大，你的 shell 启动可能会变慢。你可以随时对它进行性能分析（profiling），然后禁用那些你不常用或认为速度更重要的功能。

## 终端模拟器与复用器

自定义你的 shell 之后，也值得花些时间研究一下你选择的 **终端模拟器（terminal emulator）** 及其设置。市面上有很多终端模拟器（这里有一份 [对比](https://anarc.at/blog/2018-04-12-terminal-emulators-1/)）。

既然你可能会在终端里花费数百到数千小时，花时间去调整它的设置是非常值得的。你可能希望在终端中修改的方面包括：

- 字体选择
- 配色方案
- 键盘快捷键
- 标签页 / 窗格（pane）支持
- 滚动历史（scrollback）配置
- 性能表现（一些较新的终端如 [Alacritty](https://github.com/jwilm/alacritty) 支持 GPU 加速）

这里也值得提及一下 **终端复用器（terminal multiplexer）**，比如 [tmux](https://github.com/tmux/tmux)。`tmux` 允许你在同一个窗口中将多个 shell 会话分屏和分标签展示。它还支持附加和分离（attach/detach）——当你在一台远程服务器上工作时，这是非常常用的场景：你可以让 shell 在后台持续运行，而无需担心退出登录时终止当前进程（默认情况下，退出登录会终止你所有的进程）。借助 `tmux`，你可以随时进入或退出复杂的终端布局。与终端模拟器类似，`tmux` 也支持通过编辑 `~/.tmux.conf` 文件进行深度定制。


## 命令行工具

大多数 UNIX 类操作系统自带的命令行工具已经足够完成你 99% 的日常任务。

在接下来的几个小节中，我会介绍一些替代工具，它们用于完成非常常见的 shell 操作，使用起来更方便。这些工具中，有些为命令增加了新的、改进后的功能；另一些则专注于提供更简洁、更直观的界面，以及更合理的默认行为。

### `fasd` 与 `cd`

即使有改进后的路径展开和 Tab 自动补全，频繁切换目录仍然显得单调乏味。[Fasd](https://github.com/clvv/fasd)（或 [autojump](https://github.com/wting/autojump)）通过跟踪你近期和频繁访问过的文件夹，并支持模糊匹配（fuzzy matching）来解决这个问题。

因此，如果我曾经访问过路径 `/home/user/awesome_project/code`，那么运行 `z code` 就会 `cd` 到那个目录。如果我拥有多个名为 `code` 的文件夹，可以通过运行 `z awe code` 来消除歧义——这个模糊匹配结果会更接近。与 autojump 不同，fasd 还提供了其他命令，不只是执行 `cd`，而是直接扩展出频繁和/或近期出现过的文件或文件夹。


### `bat` 与 `cat`

虽然 `cat` 能完美地完成它的工作，但 [bat](https://github.com/sharkdp/bat) 通过提供语法高亮、分页显示、行号以及 git 集成对其进行了增强。


### `exa`/`ranger` 与 `ls`

`ls` 是个很棒的命令，但部分默认行为可能会让人恼火，比如以原始字节数显示文件大小。[exa](https://github.com/ogham/exa) 提供了更好的默认值。

如果你需要浏览大量目录和/或预览大量文件，[ranger](https://github.com/ranger/ranger) 会比 `cd` 和 `cat` 高效得多——它提供了优秀的交互式界面。它高度可定制，经过正确配置后，甚至可以在终端中 [预览图片](https://github.com/ranger/ranger/wiki/Image-Previews)。

### `fd` 与 `find`

[fd](https://github.com/sharkdp/fd) 是 `find` 的一个简洁、快速且用户友好的替代方案。`find` 的默认行为（比如你必须使用 `--name` 标志位，而你想这样做的时候占了 99% 的情况）让它日常使用起来不够顺手。它还能感知 `git`，默认跳过 `.gitignore` 和 `.git` 文件夹中的文件，并默认提供漂亮的颜色编码。

### `rg/fzf` 与 `grep`

`grep` 是一个很棒的工具，但如果你想一次性对大量文件进行 grep，则有更好的工具可供选择。[ack](https://github.com/beyondgrep/ack3)、[ag](https://github.com/ggreer/the_silver_searcher) 和 [rg](https://github.com/BurntSushi/ripgrep) 会递归搜索你当前目录中的正则表达式模式，同时尊重你的 `.gitignore` 规则。它们的用法大致相似，但我偏爱 `rg`，因为它搜索整个家目录的速度非常快。

同样，反复执行 `CMD | grep PATTERN` 的情况也很常见。[fzf](https://github.com/junegunn/fzf) 是一个命令行模糊查找器，能让你交互式地过滤几乎任何命令的输出。

### `rsync` 与 `cp/scp`

虽然在大多数场景下 `mv` 和 `scp` 已经足够了，但在复制/移动大量文件、超大文件，或部分数据已经存在于目标位置时，`rsync` 会带来显著提升。`rsync` 会跳过已经传输过的文件，配合 `--partial` 标志位，它还可以从之前中断的地方恢复传输。

### `trash` 与 `rm`

`rm` 是一个危险的命令，因为一旦你删除了一个文件，就没有回头路了。然而，现代操作系统在文件管理器中删除文件时并非如此——它们只是将文件移到回收站，定期清理回收站。

由于各个操作系统管理回收站的方式不同，CLI 领域并没有一个统一的工具。在 macOS 上有 [trash](https://hasseg.org/trash/)，在 Linux 上有 [trash-cli](https://github.com/andreafrancia/trash-cli/) 等。

### `mosh` 与 `ssh`

`ssh` 是一个非常方便的工具，但如果你有慢速网络，延迟会变得令人烦躁，而且一旦连接中断你就需要重新连接。[mosh](https://mosh.org/) 是一个方便的替代工具，它支持漫游、容忍间歇性连接，并提供智能的本地回显（local echo）。

### `tldr` 与 `man`

大多数情况下，你可以通过 `man` 以及 `-h`/`--help` 标志位来了解一个命令的功能及其可用选项。然而，有些时候这些文档内容非常详细，查阅起来可能令人望而生畏。

[tldr](https://github.com/tldr-pages/tldr) 是一个社区驱动的文档系统，可以从命令行访问，提供几条简单的示例，展示命令的作用以及最常用的参数选项。


### `aunpack` 与 `tar/unzip/unrar`

正如 [这篇 xkcd 漫画](https://xkcd.com/1168/) 所指出的，记住 `tar` 的各种参数选项可不是一件容易的事；而且有时你还需要完全不同的工具来处理特定格式的文件，比如用 `unrar` 来处理 `.rar` 文件。

[atool](https://www.nongnu.org/atool/) 包提供了 `aunpack` 命令，它会自动判断正确的参数选项，并且总是把解压后的文件放入一个新建的文件夹中。


## 练习

1. 运行 `cat .bash_history | sort | uniq -c | sort -rn | head -n 10`（zsh 用户则为 `cat .zhistory | sort | uniq -c | sort -rn | head -n 10`），查看你使用最多的前 10 条命令，然后考虑为它们编写更短的别名。
1. 选择一个终端模拟器，了解如何更改以下属性：
    - 字体选择
    - 配色方案。标准配色方案有多少种颜色？为什么？
    - 滚动历史（scrollback）大小

1. 安装 `fasd` 或类似的软件，并编写一个 bash/zsh 函数 `v`，该函数对传入的参数进行模糊匹配，并在你的编辑器中打开第一个匹配结果。然后对它进行改造，使其在存在多个匹配时，让你可以使用 `fzf` 进行选择。
1. 由于 `fzf` 在进行模糊搜索时非常方便，而 shell 历史命令本身也非常适合模糊搜索，试着研究如何将 `fzf` 绑定到 `^R`。你可以在 [这里](https://github.com/junegunn/fzf/wiki/Configuring-shell-key-bindings) 找到一些相关信息。
1. `ack` 的 `--bar` 选项有什么作用？