---
layout: lecture
title: "课程概览 + Shell 入门"
description: >
  了解本课程的学习动机，并开始使用 Shell。
thumbnail: /static/assets/thumbnails/2026/lec1.png
date: 2026-01-12
ready: true
video:
  aspect: 56.25
  id: MSgoeuMqUmU
---

# 我们是谁？

本课程由 [Anish](https://anish.io/)、[Jon](https://thesquareplanet.com/) 和 [Jose](http://josejg.com/) 共同授课。我们都曾是 MIT 的学生，在还是学生时发起了这门 MIT IAP（独立活动期）课程。你可以通过 [missing-semester@mit.edu](mailto:missing-semester@mit.edu) 联系我们。

我们不以教授这门课程获取报酬，也不以任何方式从课程中获利。我们把所有 [课程材料](https://missing.csail.mit.edu/) 和 [讲座录像](https://www.youtube.com/@MissingSemester) 都免费放在网上。如果你想支持我们的工作，最好的方式就是在你身边传播关于这门课程的消息。如果你是某个公司、大学或其他组织，带领大批成员学习了这些内容，请通过邮件发送你的使用体验或推荐给我们，这样我们才能听到相关反馈 :)

# 学习动机

作为计算机科学的从业人员，我们很清楚计算机在辅助完成重复性任务方面非常出色。然而，我们往往忘记了这一点同样适用于我们对计算机的 _使用方式_，而不仅仅是我们希望程序执行的那些计算。当我们处理任何与计算机相关的问题时，手边有大量的工具可以让我们更高效地工作、解决更复杂的问题。但我们中的很多人只使用了这些工具中的一小部分——我们只会凭死记硬背几个"魔法咒语"来应付日常，一旦卡住就盲目地从网上复制粘贴命令。

本课程就是 [针对这一问题](/about/) 做出的尝试。

我们希望你学会充分利用已有的工具、将新工具添加到你的工具箱中，并希望在这个过程中激发你自己去探索（也许甚至是构建）更多工具的热情。我们认为，这正是大多数计算机科学课程中缺失的那一门。

# 课程结构

这门不计学分的课程由九场每场 1 小时的讲座组成，每场围绕 [一个特定主题](/2026/) 展开。这些讲座在很大程度上是相互独立的，但随着学期的推进，我们会假定你已经熟悉了之前讲座的内容。我们在网上提供讲座笔记，但课堂上的某些内容（比如演示环节）可能不会出现在笔记中。与往年一样，我们会录制讲座并将录像发布在 [网上](https://www.youtube.com/@MissingSemester)。

我们试图在短短几场 1 小时的讲座中覆盖大量内容，因此讲座的信息密度相当大。为了让你有时间以自己的节奏熟悉内容，每场讲座都包含一组练习，引导你掌握本课的关键要点。我们不会开设专门的答疑时间，但鼓励你在 [OSSU Discord](https://ossu.dev/#community) 的 `#missing-semester-forum` 频道或发送邮件至 [missing-semester@mit.edu](mailto:missing-semester@mit.edu) 提问。

由于时间有限，我们无法以全面课程可能达到的详细程度覆盖所有工具。在适当的地方，我们会尝试为你指引进一步深入某个工具或主题的额外资源。如果有什么特别引起你兴趣的内容，请不要犹豫，直接联系我们询问更多方向！

最后，如果你对本课程有任何反馈，请通过邮件发送至 [missing-semester@mit.edu](mailto:missing-semester@mit.edu)。

# 主题一：Shell

{% comment %}
lecturer: Jon
{% endcomment %}

## 什么是 Shell？

如今的计算机提供了多种方式来向它们发出指令：花哨的图形用户界面（GUI）、语音界面、AR/VR，以及最近越来越火的 LLM。这些方式对于 80% 的使用场景来说都很不错，但它们在很多方面本质上受到限制——你无法点击一个不存在的按钮，也无法执行尚未被编程的语音指令。要想充分利用计算机提供的所有工具，我们需要走回老路，使用基于文本的界面：Shell。

几乎所有你能接触到的平台都至少有一种 shell，其中很多平台还提供多种 shell 供你选择。它们虽然在细节上可能有所不同，但核心都是大致相同的：它们让你能以半结构化的方式运行程序、给程序提供输入，并检查程序的输出。

要在 shell _提示符_（你输入命令的地方）下操作，你需要先打开一个_终端_（terminal），即 shell 的可视化界面。你的设备可能预装了终端，或者你可以相当轻松地安装一个：

- **Linux：**
  按 `Ctrl + Alt + T`（在大多数发行版上有效）。或者在你的应用程序菜单中搜索"Terminal"。
- **Windows：**
  按 `Win + R`，输入 `cmd` 或 `powershell`，然后按 Enter。或者在"开始"菜单中搜索"Terminal"或"Command Prompt"。
- **macOS：**
  按 `Cmd + Space` 打开 Spotlight，输入"Terminal"，然后按 Enter。或者在"应用程序 → 实用工具 → 终端"中找到它。

在 Linux 和 macOS 上，这通常会打开 Bourne Again SHell，简称"bash"。这是使用最广泛的 shell 之一，它的语法与其他许多 shell 中的语法类似。在 Windows 上，根据你执行的命令，你会看到"batch"或"powershell" shell。这些是 Windows 专有的 shell，不是本课程的重点，尽管我们教授的大部分内容在它们中都有对应的功能。如果你想获得与本课程教学环境一致的体验，建议使用 [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/) 或一个 Linux 虚拟机。

当然还有其他 shell 存在，其中许多在用户体验方面比 bash 有诸多改进（fish 和 zsh 是其中最常用的）。尽管这些 shell 非常流行（所有授课讲师都在使用），但它们远不如 bash 那样无处不在，并且它们与 bash 共用许多相同的概念，因此我们在讲座中不会将它们作为重点。

## 你为什么应该关心它？

shell 不仅通常比"在图形界面上点点点"快得多，还具备你在任何一个图形程序中很难找到的表达能力。正如我们稍后将看到的，shell 让你能够以创造性地_组合_各种程序，从而自动化几乎所有任务。

熟练使用 shell 也对于导航开源软件世界非常有用（很多开源软件的安装说明都需要 shell），为你的软件项目搭建持续集成（如 [代码质量讲座](/2026/code-quality/) 所述），以及在其它程序出错时进行调试。

## 在 shell 中导航

当你启动终端时，你会看到一个类似于这样的_提示符_（prompt）：

```console
missing:~$
```

这是 shell 的主要文本界面。它告诉你：你正在 `missing` 这台机器上，你的"当前工作目录"（current working directory），也就是你当前所在的位置，是 `~`（"home"的缩写）。`$` 告诉你你不是 root 用户（稍后会讲到更多内容）。在这个提示符下，你可以输入一个_命令_，然后由 shell 来解释它。最基础的一条命令就是执行程序：

```console
missing:~$ date
Fri 10 Jan 2020 11:49:31 AM EST
missing:~$
```

在这里，我们执行了 `date` 程序，它（也许并不令人意外地）打印出了当前的日期和时间。然后 shell 会等待我们输入下一条要执行的命令。我们还可以为命令_提供参数_（arguments）：

```console
missing:~$ echo hello
hello
```

在这个例子中，我们告诉 shell 执行 `echo` 程序，并传入参数 `hello`。`echo` 程序只是把它的参数打印出来。shell 通过将命令按空白字符（空格、制表符）分割来解析命令，然后执行由第一个单词指示的程序，并将后续的每个单词作为该程序可以访问的参数传入。如果你要传入的参数中包含空格或其他特殊字符（比如名为"My Photos"的目录），你可以用 `'` 或 `"` 将参数引起来（`"My Photos"`），或者用 `\` 对需要转义的字符进行转义（`My\ Photos`）。

也许你在起步阶段最重要的命令就是 `man`，它是"manual"（手册）的缩写。`man` 程序可以帮你查阅关于系统上任何命令的更多信息。例如，运行 `man date` 会解释 `date` 是什么，以及你可以传递给它的各种参数来改变其行为。此外，对于大多数命令，通常也可以通过传入 `--help` 参数来获取简短的帮助信息。

> 建议安装并使用 [`tldr`](https://tldr.sh/) 作为 `man` 的补充——它会在终端中直接向你展示常见的用法示例。LLM 通常也很擅长解释命令是如何工作的，以及如何调用它们来实现你想要完成的目标。

在 `man` 之后，你需要学习的下一个最重要的命令就是 `cd`，即"change directory"（更改目录）。这个命令实际上内置在 shell 本身中，而不是一个独立的程序（也就是说，`which cd` 会返回"no cd found"）。你给它传入一个路径，它就会把你的当前工作目录切换为那个路径。你也会在 shell 提示符中看到工作目录的反映：

```console
missing:~$ cd /bin
missing:/bin$ cd /
missing:/$ cd ~
missing:~$
```

> 注意：shell 自带自动补全功能，因此你经常可以通过按下 `<TAB>` 来更快地补全路径！

如果没有额外指定参数，很多命令会在当前工作目录上操作。如果你不确定自己当前在哪个位置，可以运行 `pwd` 或打印 `$PWD` 环境变量（使用 `echo $PWD`），两者都会显示当前工作目录。

当前工作目录还有一个便利之处：它让我们可以使用_相对_路径。我们之前看到的所有路径都是_绝对_路径——它们以 `/` 开头，并给出了从文件系统根目录导航到某个位置所需的所有完整目录。而在实际使用中，你更常见的是使用相对路径——之所以称为"相对"，是因为它们是相对于当前工作目录而言的。在一个相对路径（任何 _不是_ 以 `/` 开头的路径）中，第一个路径组件会在当前工作目录中查找，后续组件则按照正常方式遍历。例如：

```console
missing:~$ cd /
missing:/$ cd bin
missing:/bin$
```

在每个目录中还有两个"特殊"组件：`.` 和 `..`。`.` 表示"这个目录本身"，`..` 表示"父目录"。所以：

```console
missing:~$ cd /
missing:/$ cd bin/../bin/../bin/././../bin/..
missing:/$
```

在大多数情况下，你可以在命令的参数中交替使用绝对路径和相对路径，只要在使用相对路径时记住你当前的工作目录是什么即可！

> 建议安装并使用 [`zoxide`](https://github.com/ajeetdsouza/zoxide) 来加速你的 `cd` 操作——`z` 会记住你经常访问的路径，让你用更少的输入量就能访问到它们。

## shell 中有哪些工具？

但 shell 是怎么知道如何找到 `date` 或 `echo` 这样的程序的呢？当 shell 被要求执行一个命令时，它会查阅一个名为 `$PATH` 的_环境变量_（environment variable），该变量列出了 shell 在收到命令时需要搜索程序的目录：

```console
missing:~$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
missing:~$ which echo
/bin/echo
missing:~$ /bin/echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

当我们运行 `echo` 命令时，shell 看到它应该执行 `echo` 这个程序，然后在 `$PATH` 中以 `:` 分隔的目录列表中搜索同名的文件。找到之后，它就会运行该文件（前提是文件_可执行_——稍后会讲到更多内容）。我们可以使用 `which` 程序来查看给定程序名对应执行的是哪个文件。我们也可以绕过 `$PATH` 的搜索，直接传入我们想要执行的文件的_路径_。

这也给了我们一个线索，用于确定_所有_能够在 shell 中执行的程序——列出 `$PATH` 中所有目录的内容即可。我们可以通过将某个目录路径传入 `ls` 程序来做到这一点，`ls` 用于列出文件：

```console
missing:~$ ls /bin
```

> 建议安装并使用 [`eza`](https://eza.rocks/) 作为更人性化的 `ls`。

这将在大多数计算机上打印出_大量_程序，但这里我们只关注一些最重要的。首先是一些简单的：

- `cat file`：打印 `file` 的内容。
- `sort file`：按排序顺序打印 `file` 中的各行。
- `uniq file`：去除 `file` 中连续的重复行。
- `head file` 和 `tail file`：分别打印 `file` 开头和结尾的几行。

> 建议安装并使用 [`bat`](https://github.com/sharkdp/bat) 替代 `cat`——它提供语法高亮和滚动功能。

还有 `grep pattern file`，它会在 `file` 中查找匹配 `pattern` 的行。这个命令值得稍微多讲一点，因为它_非常_有用，而且它的功能也比很多人预期的要丰富得多。这里的 `pattern` 实际上是一个_正则表达式_（regular expression），可以表达非常复杂的模式——我们将在 [代码质量讲座](/2026/code-quality/#regular-expressions) 中[深入介绍](/2026/code-quality/#regular-expressions)。你也可以传入一个目录而非文件（或者对当前目录省略它传 `.`）并加上 `-r` 参数来递归搜索目录下的所有文件。

> 建议安装并使用 [`ripgrep`](https://github.com/BurntSushi/ripgrep) 替代 `grep`——它更快、对用户更友好（但可移植性较差）。`ripgrep` 还会默认递归搜索当前工作目录！

还有一些功能稍复杂但也非常有用的工具。其中首推的是 `sed`，这是一个程序化的文件编辑器。它有自己的一套编程语言来对文件进行自动化编辑，但最常用的用法是：

```console
missing:~$ sed -i 's/pattern/replacement/g' file
```

这会将 `file` 中所有 `pattern` 的实例替换为 `replacement`。`-i` 表示我们希望替换在原文件中原地进行（而不是保持 `file` 不变、仅输出替换后的内容）。`s/` 是在 sed 编程语言中表达"我们要做替换"的方式。`/` 分隔了模式（pattern）和替换文本（replacement）。尾部的 `/g` 表示我们希望替换每一行上的_所有_匹配项，而不仅仅是第一个。与 `grep` 一样，这里的 `pattern` 是一个正则表达式，赋予了您很强的表达能力。正则表达式替换还允许 `replacement` 部分引用匹配模式中捕获的子串；我们很快就会看到一个例子。

接下来是 `find`，它可以用来查找（递归地）符合某些条件的文件。例如：

```console
missing:~$ find ~/Downloads -type f -name "*.zip" -mtime +30
```

查找下载目录中 30 天之前创建的 ZIP 文件。

```console
missing:~$ find ~ -type f -size +100M -exec ls -lh {} \;
```

查找主目录中大于 100M 的文件并列出它们。注意 `-exec` 接收一个以单独 `;` 结束的_命令_（这里的 `;` 需要像空格一样转义），其中 `{}` 会被 `find` 替换为每个匹配文件的路径。

```console
missing:~$ find . -name "*.py" -exec grep -l "TODO" {} \;
```

查找所有包含 TODO 标记的 `.py` 文件。

`find` 的语法可能看起来有点吓人，但希望这些例子能让你感受到它的有用之处！

> 建议安装并使用 [`fd`](https://github.com/sharkdp/fd) 替代 `find`——它更人性化（但可移植性较差！）。

接下来轮到 `awk`，和 `sed` 一样，它也有自己的编程语言。`sed` 专为编辑文件而设计，而 `awk` 专为_解析_文件而设计。`awk` 最典型的用途是处理具有规整格式的数据文件（比如 CSV 文件），从中提取每个记录（即每一行）的某些特定部分：

```console
missing:~$ awk '{print $2}' file
```

打印 `file` 中每一行的第二个空白符分隔的列。如果加上 `-F,` 参数，它会打印每一行的第二个逗号分隔的列。`awk` 能做更多的事情——过滤行、计算聚合值等等——详见练习。

将这些工具组合在一起，我们可以做一些很酷的事情，比如：

```console
missing:~$ ssh myserver 'journalctl -u sshd -b-1 | grep "Disconnected from"' \
  | sed -E 's/.*Disconnected from .* user (.*) [^ ]+ port.*/\1/' \
  | sort | uniq -c \
  | sort -nk1,1 | tail -n10 \
  | awk '{print $2}' | paste -sd,
postgres,mysql,oracle,dell,ubuntu,inspur,test,admin,user,root
```

这条命令从远程服务器抓取 SSH 日志（`ssh` 我们将在下一讲中详细介绍），搜索断开连接的消息，从每条消息中提取用户名，并以逗号分隔的形式打印出使用频率最高的 10 个用户名。全部在一个命令中完成！我们将每一步的分析留作练习。

## Shell 语言（bash）

上面的例子引入了一个新概念：_管道_（pipes, `|`）。它让你能将一个程序的输出"串接"到另一个程序的输入中。这之所以可行，是因为大多数命令行程序在 _没有_ 给出 `file` 参数时，会对它们的"标准输入"（standard input，即你的键盘输入默认进入的地方）进行操作。`|` 将 `|` 前面程序的"标准输出"（standard output，即通常打印到终端的内容）作为 `|` 后面程序的标准输入。这让你可以_组合_ shell 程序，也是让 shell 成为如此高效的工作环境的一部分原因！

实际上，大多数 shell 都实现了一套完整的编程语言（比如 bash），与 Python 或 Ruby 类似。它有变量、条件判断、循环和函数。当你在 shell 中运行命令时，你实际上是在编写一小段由 shell 解释执行的代码。我们今天不会教你所有 bash 的知识，但有一些你会特别有用的部分：

首先是重定向（redirects）：`>file` 可以将程序的标准输出写入 `file` 而不是终端，方便事后分析。`>>file` 会_追加_到 `file` 而不是覆盖它。还有 `<file`，它告诉 shell 从 `file` 读取而非从你的键盘读取，作为程序的标准输入。

> 这里值得顺便提一下 `tee` 程序。`tee` 会将标准输入打印到标准输出（和 `cat` 一样！），但_也会_将它写入一个文件。因此 `verbose cmd | tee verbose.log | grep CRITICAL` 会在全量详细日志保存到一个文件的同时，保持你的终端界面干净！

接下来是条件判断：`if command1; then command2; command3; fi` 会执行 `command1`，如果它没有出错，就会运行 `command2` 和 `command3`。你也可以在需要时使用 `else` 分支。最常用的作为 `command1` 的命令是 `test` 命令，通常缩写为 `[`，它让你可以评估各种条件，比如"某个文件是否存在"（`test -f file` / `[ -f file ]`）或"某个字符串是否等于另一个"（`[ "$var" = "string" ]`）。在 bash 中，还有 `[[ ]]`，它是 `test` 的"更安全"的内置版本，在引号处理方面有更少的怪异行为。

bash 也有两种形式的循环：`while` 和 `for`。`while command1; do command2; command3; done` 的功能与等价的 `if` 命令类似，只不过它会一遍又一遍地重新执行整个代码块，只要 `command1` 不出错就会持续进行。`for varname in a b c d; do command; done` 会执行 `command` 四次，每次让 `$varname` 分别取 `a`、`b`、`c` 和 `d` 中的一个值。除了直接列出各项，你通常会使用"_命令替换_"（command substitution），例如：

```bash
for i in $(seq 1 10); do
```

这执行了 `seq 1 10` 命令（它会打印从 1 到 10 的数字），然后将整个 `$()` 替换为该命令的输出，给你一个 10 次迭代的 for 循环。在旧代码中，你有时可能会看到使用反引号字面量的写法（比如 ``for i in `seq 1 10`; do``）而不是 `$()`，但你应强烈偏好 `$()` 写法，因为它可以嵌套。

虽然你_可以_直接在提示符下编写很长的 shell 脚本，但你通常更愿意把它们写入一个 `.sh` 文件中。例如，下面是一个脚本，它会在后台给 CPU 施加压力的同时，循环运行一个程序直到它失败，并只打印出失败运行的输出（对于复现偶发性测试失败很有用，比如）：

```bash
#!/bin/bash
set -euo pipefail

# Start CPU stress in background
stress --cpu 8 &
STRESS_PID=$!

# Setup log file
LOGFILE="test_runs_$(date +%s).log"
echo "Logging to $LOGFILE"

# Run tests until one fails
RUN=1
while cargo test my_test > "$LOGFILE" 2>&1; do
    echo "Run $RUN passed"
    ((RUN++))
done

# Cleanup and report
kill $STRESS_PID
echo "Test failed on run $RUN"
echo "Last 20 lines of output:"
tail -n 20 "$LOGFILE"
echo "Full log: $LOGFILE"
```

这里面有很多新内容，建议你花时间深入了解它们——它们在编写实用的 shell 指令时非常有用，比如后台作业（`&`）可以并发运行程序、复杂的 [shell 重定向](https://www.gnu.org/software/bash/manual/html_node/Redirections.html)，以及 [算术扩展](https://www.gnu.org/software/bash/manual/html_node/Arithmetic-Expansion.html)。

不过值得花一秒关注程序的开头两行。第一行是"shebang"——你也会在其他非 shell 脚本文件的顶部看到它。当一个以魔法咒语 `#!/path` 开头的文件被执行时，shell 会启动 `/path` 处的程序，并将文件的内容作为输入传入。对于 shell 脚本来说，这意味着将 shell 脚本的内容传递给 `/bin/bash`，但你也可以编写 Python 脚本，只需将 shebang 行设为 `/usr/bin/python` 即可！

第二行是让 bash 变得"更严格"的一种方式，用来缓解编写 shell 脚本时出现的不少"坑"。`set` 可以接受大量参数，但简要说明：`-e` 表示如果任何命令失败，脚本就会提前退出；`-u` 表示使用未定义的变量会让脚本崩溃，而不是简单地使用空字符串；`-o pipefail` 表示如果 `|` 管道序列中的任何程序失败，整个 shell 脚本也会提前退出。

> Shell 编程是一个深入的话题，就像任何编程语言一样，但要注意：bash 有不寻常数量的"陷阱"，甚至出现了多个 [专门列出这些陷阱的网站](https://tldp.org/LDP/abs/html/gotchas.html)。我强烈建议你在编写 shell 脚本时大量使用 [shellcheck](https://www.shellcheck.net/)。LLM 也非常擅长编写和调试 shell 脚本，以及当脚本在 bash 中变得过于笨拙（超过 100 行）时，将它们翻译成"正经"的编程语言（如 Python）。

# 下一步

到这里，你对 shell 的使用已经达到了完成基本任务的水平。你应该能够导航到感兴趣的文件位置，并使用大多数程序的基本功能。在接下来的讲座中，我们将讨论如何利用 shell 以及大量实用的命令行程序来执行和自动化更复杂的任务。

# 练习

本课程的所有课程都附带一系列练习。有些练习给你一个具体要完成的任务，另一些则是开放式的，比如"尝试使用 X 和 Y 程序"。我们强烈鼓励你动手尝试。

我们尚未为这些练习编写解答。如果你在某处特别卡住，很乐意在 [Discord](https://ossu.dev/#community) 的 `#missing-semester-forum` 频道发帖，或发送邮件给我们描述你已经尝试过的方法，我们会尽力帮助你。这些练习也很适合在 LLM 对话中作为初始提示——你可以交互式的深入探索这一主题。这些练习真正的价值在于发现答案的_过程_，而不仅仅是答案本身。我们鼓励你在完成练习时跟随自己的思路、提出"为什么"的问题，而不仅仅是寻找最短的解题路径。

1. 学习本课程时，你需要使用 Unix 风格的 shell，如 Bash 或 ZSH。如果你在 Linux 或 macOS 上，不需要做特殊设置。如果你在 Windows 上，需要确保你没有运行 cmd.exe 或 PowerShell——你可以使用 [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/) 或一个 Linux 虚拟机来使用 Unix 风格的命令行工具。要确保你正在运行合适的 shell，可以尝试执行命令 `echo $SHELL`。如果它返回类似 `/bin/bash` 或 `/usr/bin/zsh` 的结果，说明你正在运行正确的程序。

1. `ls` 的 `-l` 标志做了什么？运行 `ls -l /` 并检查输出。每一行的前 10 个字符代表什么意思？（提示：`man ls`）

1. 在命令 `find ~/Downloads -type f -name "*.zip" -mtime +30` 中，`*.zip` 是一个"通配符"（glob）。通配符是什么？创建一个包含一些文件的测试目录，并尝试 `ls *.txt`、`ls file?.txt` 和 `ls {a,b,c}.txt` 等模式。参见 Bash 手册中的 [Pattern Matching](https://www.gnu.org/software/bash/manual/html_node/Pattern-Matching.html)。

1. `'单引号'`、`"双引号"` 和 `$'ANSI 引号'` 有什么区别？编写一个命令来 echo 包含一个字面量 `$`、一个 `!` 和一个换行符的字符串。参见 [Quoting](https://www.gnu.org/software/bash/manual/html_node/Quoting.html)。

1. shell 有三个标准流：stdin（标准输入，编号 0）、stdout（标准输出，编号 1）和 stderr（标准错误，编号 2）。运行 `ls /nonexistent /tmp` 并将 stdout 重定向到一个文件、stderr 重定向到另一个文件。如何将两者重定向到同一个文件？参见 [Redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html)。

1. `$?` 保存着上一个命令的退出状态（0 表示成功）。`&&` 仅在上一条命令成功时才运行下一条命令；`||` 仅在上一条命令失败时才运行下一条命令。编写一条单行命令，仅在 `/tmp/mydir` 不存在时才创建它。参见 [Exit Status](https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html)。

1. 为什么 `cd` 必须内置在 shell 中，而不能是一个独立的程序？（提示：思考子进程能且不能影响其父进程的哪些内容。）

1. 编写一个脚本，接受一个文件名作为参数（`$1`），并使用 `test -f` 或 `[ -f ... ]` 检查该文件是否存在。它应根据文件是否存在输出不同的信息。参见 [Bash Conditional Expressions](https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html)。

1. 将上一题中的脚本保存到一个文件（例如 `check.sh`）。尝试用 `./check.sh somefile` 运行它。发生了什么？然后运行 `chmod +x check.sh` 再试一次。为什么这一步是必要的？（提示：在 `chmod` 前后分别查看 `ls -l check.sh` 的输出。）

1. 如果在脚本的 `set` 标志中加上 `-x` 会发生什么？尝试在一个简单的脚本中试试，并观察输出。参见 [The Set Builtin](https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html)。

1. 编写一条命令，将一个文件复制为带有今天日期的备份（例如 `notes.txt` → `notes_2026-01-12.txt`)。（提示：`$(date +%Y-%m-%d)`）。参见 [Command Substitution](https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html)。

1. 修改讲座中的偶发性测试脚本，让它接受测试命令作为参数传入，而不是硬编码 `cargo test my_test`。（提示：`$1` 或 `$@`）。参见 [Special Parameters](https://www.gnu.org/software/bash/manual/html_node/Special-Parameters.html)。

1. 使用管道找到你主目录中 5 个最常见的文件扩展名。（提示：组合使用 `find`、`grep` 或 `sed` 或 `awk`、`sort`、`uniq -c` 和 `head`。）

1. `xargs` 将 stdin 中的行转换为命令行参数。使用 `find` 和 `xargs` 配合（不使用 `find -exec`）来查找目录中所有的 `.sh` 文件，并用 `wc -l` 统计每个文件的行数。加分项：让它能处理文件名中包含空格的情况。（提示：`-print0` 和 `-0`）。参见 `man xargs`。

1. 使用 `curl` 获取课程网站的 HTML（`https://missing.csail.mit.edu/`），然后管道传递给 `grep` 来统计列出了多少讲座。（提示：寻找每个讲座出现一次的模式；使用 `curl -s` 静默进度输出。）

1. [`jq`](https://jqlang.github.io/jq/) 是一个用于处理 JSON 数据的强大工具。使用 `curl` 获取以下示例数据 `https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json`，并用 `jq` 提取出 version 大于 6 的人的 name 字段。（提示：先管道传入 `jq .` 查看数据结构；然后尝试 `jq '.[] | select(...) | .name'`）

1. `awk` 可以根据列值过滤行并操作输出。例如，`awk '$3 ~ /pattern/ {$4=""; print}'` 仅输出第三列匹配 `pattern` 的行，同时省略第四列。编写一条 `awk` 命令，仅输出第二列大于 100 的行，并交换第一列和第三列。用以下命令测试：`printf 'a 50 x\nb 150 y\nc 200 z\n'`

1. 分析讲座中 SSH 日志的管道：每一步分别做了什么？然后自己构建一个类似的管道，用于从 `~/.bash_history`（或 `~/.zsh_history`）中找到你最常用的 shell 命令。