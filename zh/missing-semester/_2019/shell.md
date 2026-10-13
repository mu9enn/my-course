---
layout: lecture
title: "Shell 与脚本编程"
presenter: Jon
date: 2019-01-15
order: 3
video:
  aspect: 56.25
  id: dbDRfmH5uSI
---

shell（命令行解释器）是计算机的高效文本界面。

shell 提示符：打开终端时出现在你面前的东西。它让你运行程序和命令；常用的有：

 - `cd` 用于切换目录
 - `ls` 用于列出文件和目录
 - `mv` 和 `cp` 用于移动和复制文件

但 shell 能让你做的远不止这些——你可以调用计算机上安装的任何程序，并且几乎任何你能想到的操作都有对应的命令行工具。而且它们往往比图形界面效率更高。我们将在本课堂逐一介绍其中许多工具。

shell 提供了一套交互式编程语言（即脚本）。有许多种 shell：

 - 你可能用过 `sh` 或 `bash`。
 - 也有匹配某种语言风格的，比如 `csh`。
 - 或者"更好"的 shell：`fish`、`zsh`、`ksh`。

本课我们将聚焦于无处不在的 `sh` 和 `bash`，但也可以随意尝试其他 shell。我个人喜欢 `fish`。

shell 脚本编程是你工具箱中非常实用的一把利器。你可以直接在提示符下编写程序，也可以把代码写入文件。加上 `#!/bin/sh` 并用 `chmod +x` 赋予执行权限后，shell 脚本就可以像普通程序一样运行。

## 与 shell 交互

重复运行一条命令：

```bash
for i in $(seq 1 5); do echo hello; done
```

这段代码值得仔细拆解：

 - `for x in list; do BODY; done`
   - `;` 用于终止一条命令——等价于换行符
   - 将 `list` 按空白符拆分，逐个赋值给 `x`，并执行循环体
   - 拆分方式是"空白符拆分"，我们稍后会回到这个话题
   - shell 中不使用花括号，因此用 `do` + `done` 作为循环的起止标记
 - `$(seq 1 5)`
   - 以参数 `1` 和 `5` 运行程序 `seq`
   - 用该程序的整个输出替换掉 `$()` 表达式
   - 等价于
     ```bash
     for i in 1 2 3 4 5
     ```
 - `echo hello`
   - shell 脚本中的一切都是命令
   - 此处运行 `echo` 命令，打印其参数——即参数 `hello`
   - 所有命令都在 `$PATH`（冒号分隔的目录列表）中搜索

我们可以使用变量：

```bash
for f in $(ls); do echo $f; done
```

这会打印出当前目录下每个文件的名称。

也可以用 `=` 来设置变量（注意等号两侧不能有空格）：

```bash
foo=bar
echo $foo
```

还有一些"特殊"变量：

 - `$1` 到 `$9`：脚本接收到的第 1～9 个参数
 - `$0`：脚本自身的名称
 - `$#`：参数的数量
 - `$$`：当前 shell 所在进程 ID

下面这段代码只打印目录：

```bash
for f in $(ls); do if test -d $f; then echo dir $f; fi; done
```

这里还有更多细节值得拆解：

 - `if CONDITION; then BODY; fi`
   - `CONDITION` 是一个命令——如果它返回的退出状态为 `0`（表示成功），则执行 `BODY`
   - 也可以插入 `else` 或 `elif` 分支
   - 同样没有花括号，所以用 `then` + `fi` 来标记条件体的起止
 - `test` 是另一个提供各种检查和比较功能的程序，当检查结果为真时以退出状态 `0` 退出（`$?` 变量可获取上一条命令的退出状态）
   - `man COMMAND` 是你的好帮手：运行 `man test` 查看文档
   - 也可以用 `[` + `]` 形式调用：`[ -d $f ]`
     - 看一下 `man test` 和 `which "["`

但等等——这段代码其实有 bug！如果有个文件名叫"My Documents"会怎样？

 - `for f in $(ls)` 会展开成 `for f in My Documents`
 - 先对 `My` 做测试，再对 `Documents` 做测试
 - 这显然不是我们想要的结果
 - 这是 shell 脚本中最常见的 bug 来源之一

## 参数拆分

bash 会按空白符拆分参数——但这并不总是你想要的结果。

 - 需要加引号来处理参数中包含空格的情况。`for f in "My Documents"` 就可以正确工作
 - 前面的代码里还有类似的问题——你能看出来吗？`test -d $f`：如果 `$f` 包含空白符，`test` 就会出错！
 - `echo` 碰巧没有问题，因为拆分之后再按空格合并——但如果文件名中包含换行符呢？它会变成空格！
 - 对不想被拆分的所有变量使用都要加引号
 - 但怎么修复上面那段脚本呢？你觉得 `for f in "$(ls)"` 会怎样？

答案就是**通配**（globbing）。

 - bash 知道如何使用模式查找文件：
   - `*` 匹配任意长度的字符序列
   - `?` 匹配单个任意字符
   - `{a,b,c}` 匹配其中的任意一个字符
 - `for f in *`：该目录下的所有文件
 - 通配时，每个匹配到的文件都成为独立的参数
   - 但使用时仍然需要加引号：`test -d "$f"`
 - 可以构造更高级的模式：
   - `for f in a*`：当前目录下所有以 `a` 开头的文件
   - `for f in foo/*.txt`：`foo` 目录下所有 `.txt` 文件
   - `for f in foo/*/p??.txt`
     `foo` 的子目录中以 `p` 开头的三字母 `.txt` 文件

空白符相关的问题远不止这些：

 - `if [ $foo = "bar" ]; then`——看出问题了吗？
 - 如果 `$foo` 为空怎么办？此时传给 `[` 的参数只剩 `=` 和 `bar`……
 - _可以_通过 `[ x$foo = "xbar" ]` 来绕过这个陷阱，但实在不够优雅
 - 更好的做法是使用 `[[`：bash 的内建比较符，拥有专门的语法解析
   - 它还允许使用 `&&` 代替 `-a`、`||` 代替 `-o` 等

<!-- TODO: arrays? $@. ${array[@]} vs "${array[@]}". -->

## 组合能力

shell 的强大之处在于其组合能力：可以把多个程序连接起来，而不是依赖一个"包打天下"的超级程序。

核心字符是 `|`（管道）。

 - `a | b` 表示同时运行 `a` 和 `b`，将 `a` 的全部输出作为 `b` 的输入，最后打印 `b` 的输出。

所有你启动的程序（"进程"）都拥有三条"流"：

 - `STDIN`：程序读取输入时，数据来源于此
 - `STDOUT`：程序打印输出时，数据流向此处
 - `STDERR`：程序可以选择使用的第二条输出流
 - 默认情况下，`STDIN` 是你的键盘，`STDOUT` 和 `STDERR` 都是你的终端。但你也可以改变它们！
   - `a | b` 使 `a` 的 `STDOUT` 成为 `b` 的 `STDIN`。
   - 此外还有：
     - `a > foo`（`a` 的 `STDOUT` 写入文件 `foo`）
     - `a 2> foo`（`a` 的 `STDERR` 写入文件 `foo`）
     - `a < foo`（`a` 的 `STDIN` 从文件 `foo` 中读取）
     - 提示：`tail -f` 会在文件被写入的同时实时打印新内容
 - 这有什么用？让你可以操纵程序的输出！
   - `ls | grep foo`：所有包含单词 `foo` 的文件
   - `ps | grep foo`：所有包含单词 `foo` 的进程
   - `journalctl | grep -i intel | tail -n5`：最后 5 条包含"intel"（不区分大小写）的系统日志
   - `who | sendmail -t me@example.com`：把当前登录用户列表发送到 `me@example.com`
   - 构成了后续我们将深入讨论的大量数据整理操作的基础

bash 还提供了一些其他组合程序的方式。

你可以用 `(a; b) | tac` 来组合命令：先运行 `a`，再运行 `b`，然后把它们的全部输出交给 `tac` 处理——后者会把输入按逆序打印出来。

一个不太为人所知但非常有用的技巧是**进程替换**（process substitution）。`b <(a)` 会运行 `a`，为其输出流生成一个临时文件名，并将该文件名作为参数传递给 `b`。例如：

```bash
diff <(journalctl -b -1 | head -n20) <(journalctl -b -2 | head -n20)
```

它会显示上次开机日志和前上次开机日志前 20 行之间的差异。

<!-- TODO: exit codes? -->

## 作业与进程控制

如果你想让某些程序在后台长期运行，该怎么办？

 - `&` 后缀可以让程序"在后台运行"
   - 它会立即把提示符还给你
   - 如果你想同时运行两个程序（比如一个服务器和一个客户端），这就很方便：`server & client`
   - 注意此时正在运行的程序仍然以你的终端作为 `STDOUT`！试一下：`server > server.log & client`
 - 用 `jobs` 查看所有此类进程
   - 会注意到状态显示为"Running"
 - 用 `fg %JOB` 把它带回前台（不带参数则带回最近的一个）
 - 如果想把当前程序放到后台运行：`^Z` + `bg`（其中 `^Z` 表示按下 `Ctrl+Z`）
   - `^Z` 暂停当前进程并将其变为一个"作业"
   - `bg` 在后台运行上一个作业（相当于你加了 `&`）
 - 后台作业仍然与当前会话关联，登出后会终止。`disown` 可以切断这种关联。也可以用 `nohup`。
 - `$!` 是最后一个后台进程的进程 ID

<!-- TODO: process output control (^S and ^Q)? -->

计算机上还有哪些其他进程？

 - `ps` 是你的好帮手：列出正在运行的进程
   - `ps -A`：打印所有用户的所有进程（也等价于 `ps ax`）
   - `ps` 有很多参数：详见 `man ps`
 - `pgrep`：通过搜索查找进程（类似 `ps -A | grep`）
   - `pgrep -af`：搜索并连同参数一起显示
 - `kill`：通过进程 ID 向进程发送一个**信号**（`pkill` 可以通过搜索加 `-f` 来定位进程）
   - 信号告诉进程"执行某个动作"
   - 最常见的：`SIGKILL`（`-9` 或 `-KILL`）：命令它*立即*退出，等价于 `^\`
   - 还有 `SIGTERM`（`-15` 或 `-TERM`）：命令它优雅退出，等价于 `^C`

## 命令行标志（Flags）

大多数命令行工具使用 **flags** 来接收参数。flags 通常分为短格式（`-h`）和长格式（`--help`）。一般运行 `CMD -h` 或 `man CMD` 就能获得该程序支持的所有 flags 列表。

短 flags 通常可以合并使用，`rm -r -f` 等价于 `rm -rf` 或 `rm -fr`。

一些常见 flags 已经成为事实上的标准，在很多程序中都能看到：

* `-a` 通常表示"全部文件"（即还包括以点号开头的隐藏文件）
* `-f` 通常表示"强制"，比如 `rm -f`
* `-h` 通常显示帮助信息
* `-v` 通常启用详细信息（verbose）输出
* `-V` 通常显示命令的版本号

此外，双破折号 `--` 被内置命令和许多其他命令用来标记命令选项的结束。`--` 之后只接受位置参数。例如，如果你有一个名为 `-v` 的文件（确实可以创建这样的文件），想用 `grep` 搜索它，`grep pattern -- -v` 可以工作，而 `grep pattern -v` 则不行（后者会被解释为开启忽略大小写的选项）。实际上，创建这种文件的一个方法就是用 `touch -- -v`。

## 练习

1. 如果你完全不了解 shell，建议阅读更全面的指南，如 [BashGuide](https://mywiki.wooledge.org/BashGuide)。如果想要更深入的入门介绍，[The Linux Command Line](https://linuxcommand.org/tlcl.php) 是一本很好的参考书。

1. **PATH、which、type**

    我们简要讨论了 `PATH` 环境变量用于定位你通过命令行运行的程序。让我们进一步探索：
    - 运行 `echo $PATH`（或者 `echo $PATH | tr -s ':' '\n'` 以美化输出），查看其内容，里面列出了哪些路径？
    - 命令 `which` 用于在用户的 `PATH` 中定位某个程序。尝试对 `echo`、`ls` 或 `mv` 等常见命令运行 `which`。注意 `which` 有一定局限性，因为它不理解 shell 别名。对这些相同命令尝试运行 `type` 和 `command -v`。它们的输出有什么区别？
    - 运行 `PATH=`（清空 PATH），然后再次尝试运行前面的命令——有些能运行，有些不能。你能想明白原因吗？

1. **特殊变量**
    - 变量 `~` 展开成什么？`.` 呢？`..` 呢？
    - 变量 `$?` 有什么作用？
    - 变量 `$_` 有什么作用？
    - 变量 `!!` 展开成什么？`!!*` 呢？`!l` 呢？
    - 查阅这些选项的文档并熟悉它们的用法

1. **xargs**

    有时管道并不完全适用，因为接收管道输入的命令并不期望换行分隔的格式。例如 `file` 命令可以告诉你文件的属性。

    尝试运行 `ls | file` 和 `ls | xargs file`。`xargs` 在做什么？

1. **Shebang**

    在编写脚本时，你可以使用 [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)) 行来告诉 shell 使用哪个解释器来解释脚本。创建一个名为 `hello` 的脚本，内容如下，用 `chmod +x hello` 使其可执行。然后用 `./hello` 执行它。接着删掉第一行再执行一次。看看 shell 是如何使用第一行的？

    ```bash
      #! /usr/bin/python

      print("Hello World!")
    ```

    你经常会看到 shebang 形如 `#! /usr/bin/env bash` 的程序。这是一种更具可移植性的方案，但它也有自己的[优缺点](https://unix.stackexchange.com/questions/29608/why-is-it-better-to-use-usr-bin-env-name-instead-of-path-to-name-as-my)。`env` 和 `which` 有什么区别？`env` 使用哪个环境变量来决定运行哪个程序？

1. **管道、进程替换、子 shell**

    创建一个名为 `slow_seq.sh` 的脚本，内容如下，并用 `chmod +x slow_seq.sh` 使其可执行。

    ```bash
      #! /usr/bin/env bash

      for i in $(seq 1 10); do
              echo $i;
              sleep 1;
      done
    ```

    管道（以及进程替换）与使用子 shell 执行（即 `$()`）之间存在区别。运行以下命令并观察差异：

    - `./slow_seq.sh | grep -P "[3-6]"`
    - `grep -P "[3-6]" <(./slow_seq.sh)`
    - `echo $(./slow_seq.sh) | grep -P "[3-6]"`

1. **杂项**
    - 尝试运行 `touch {a,b}{a,b}` 然后 `ls`，看到了什么？
    - 有时你希望既保留 STDIN 同时仍将其管道输出到文件。尝试运行 `echo HELLO | tee hello.txt`
    - 尝试运行 `cat hello.txt > hello.txt`，你预期会发生什么？实际发生了什么？
    - 运行 `echo HELLO > hello.txt`，然后运行 `echo WORLD >> hello.txt`。`hello.txt` 的内容是什么？`>` 和 `>>` 有什么区别？
    - 运行 `printf "\e[38;5;81mfoo\e[0m\n"`。输出有什么不同？如果想了解更多，可以搜索 ANSI 颜色转义序列。
    - 运行 `touch a.txt`，然后运行 `^txt^log`，bash 为你做了什么？再试一下 `fc`。它做了什么？

1. **键盘快捷键**

    对于经常使用的应用程序，熟悉其键盘快捷键是值得的。输入以下快捷键，尝试弄清楚它们的作用以及在哪些场景下使用比较方便。对于其中一些，上网搜索它们的功能可能更简单。（记住：`^X` 表示按下 `Ctrl+X`）

    - `^A`、`^E`
    - `^R`
    - `^L`
    - `^C`、`^\` 和 `^D`
    - `^U` 和 `^Y`

{% comment %}

TODO

1. **parallel**
- set -e, set -x
- traps

{% endcomment %}