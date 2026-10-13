---
layout: lecture
title: "Shell 工具与脚本"
description: >
  学习编写 shell 脚本并使用强大的命令行工具。
thumbnail: /static/assets/thumbnails/2020/lec2.png
date: 2020-01-14
ready: true
video:
  aspect: 56.25
  id: kgII-YWo3Zw
---

本节课程将介绍把 bash 用作脚本语言的一些基础知识，以及一系列 shell 工具，涵盖你在命令行中需要频繁执行的最常见任务。

# 脚本编写

到目前为止，我们已经学会了如何在 shell 中执行命令并将它们用管道（pipe）连接起来。
但在许多场景下，你需要依次执行一系列命令，并使用条件判断或循环等控制流表达式。

Shell 脚本在复杂度上又进了一步。
大多数 shell 都自带一种脚本语言，包含变量、控制流以及自己的语法。
Shell 脚本与其他脚本语言的不同之处在于：它被优化用于执行与 shell 相关的任务。
因此，创建命令管道、将结果保存到文件以及从标准输入读取数据，这些都是 shell 脚本的原语（primitive），这使得它在这些场景下比通用的脚本语言更容易使用。
本节我们将聚焦于 bash 脚本，因为它是使用最广泛的。

在 bash 中赋值变量，使用 `foo=bar` 的语法，并通过 `$foo` 访问变量的值。
注意，`foo = bar` 不会生效，因为它会被解释为调用名为 `foo` 的程序，并传入参数 `=` 和 `bar`。
一般来说，在 shell 脚本中，空格字符会执行参数分割。这种行为刚开始可能会让人觉得困惑，所以请务必留意。

bash 中的字符串可以使用 `'` 或 `"` 作为定界符来定义，但两者并不等价。
用 `'` 括起来的是**字面字符串**，不会替换变量值；而用 `"` 括起来的字符串则会进行变量替换。

```bash
foo=bar
echo "$foo"
# prints bar
echo '$foo'
# prints $foo
```

与大多数编程语言一样，bash 支持多种控制流结构，包括 `if`、`case`、`while` 和 `for`。
同样，`bash` 也支持函数，函数可以接收参数并对其进行操作。下面是一个创建目录并 `cd` 进入该目录的函数示例。


```bash
mcd () {
    mkdir -p "$1"
    cd "$1"
}
```

这里的 `$1` 是脚本/函数的第一个参数。
与许多其他脚本语言不同，bash 使用一系列特殊变量来引用参数、退出码以及其他相关变量。下面列出其中一些，更完整的列表可以在[这里](https://tldp.org/LDP/abs/html/special-chars.html)找到。

- `$0` — 脚本名称
- `$1` 到 `$9` — 脚本参数。`$1` 是第一个参数，依此类推。
- `$@` — 所有参数
- `$#` — 参数数量
- `$?` — 上一条命令的**退出状态码**（return code）
- `$$` — 当前脚本的进程标识符（PID）
- `!!` — 完整的上一条命令（包含参数）。一个常见的用法是：执行命令后因为权限不足而失败，你可以通过 `sudo !!` 快速重新以 root 身份执行。
- `$_` — 上一条命令的最后一个参数。在交互式 shell 中，你同样可以按下 `Esc` 再按 `.` 或 `Alt+.` 快速获取该值。

命令通常通过 `STDOUT`（标准输出）返回输出，通过 `STDERR`（标准错误）返回错误，并通过一个**退出状态码**（return code）以更适合脚本使用的方式报告错误。
退出状态码或**退出状态**（exit status）是脚本/命令用来沟通执行结果的方式。
返回值 0 通常表示一切正常；任何非 0 值都表示出现了错误。

退出状态可以通过 `&&`（与运算符）和 `||`（或运算符）来条件性地执行命令，这两个运算符都是[短路求值](https://en.wikipedia.org/wiki/Short-circuit_evaluation)运算符。
命令也可以通过分号 `;` 在同一行内分隔。
`true` 程序的退出状态码始终为 0，`false` 命令的退出状态码始终为 1。
我们来看几个例子：

```bash
false || echo "Oops, fail"
# Oops, fail

true || echo "Will not be printed"
#

true && echo "Things went well"
# Things went well

false && echo "Will not be printed"
#

true ; echo "This will always run"
# This will always run

false ; echo "This will always run"
# This will always run
```

另一种常见需求是将命令的输出获取到变量中。这可以通过**命令替换**（command substitution）来实现。
当你写成 `$( CMD )` 时，shell 会先执行 `CMD`，然后将该命令的输出代入原来所在的位置。
例如，如果你写 `for file in $(ls)`，shell 会先调用 `ls`，然后对这些值进行迭代。

一个不那么知名但类似的特性是**进程替换**（process substitution）：`<( CMD )` 会执行 `CMD`，将其输出放到一个临时文件中，然后把 `<()` 替换为该临时文件的路径。这在某些命令期望通过文件而非通过 STDIN 接收值时非常有用。
例如，`diff <(ls foo) <(ls bar)` 会显示 `foo` 和 `bar` 两个目录中文件的差异。

---

既然刚才的信息量比较大，我们来通过一个完整的例子把这些特性串联起来。这个脚本会遍历我们传入的参数，在每个文件中 `grep` 搜索字符串 `foobar`，如果没有找到，就把 `# foobar` 作为注释追加到文件末尾。

```bash
#!/bin/bash

echo "Starting program at $(date)" # Date will be substituted

echo "Running program $0 with $# arguments with pid $$"

for file in "$@"; do
    grep foobar "$file" > /dev/null 2> /dev/null
    # When pattern is not found, grep has exit status 1
    # We redirect STDOUT and STDERR to a null register since we do not care about them
    if [[ $? -ne 0 ]]; then
        echo "File $file does not have any foobar, adding one"
        echo "# foobar" >> "$file"
    fi
done
```

在比较中，我们测试了 `$?` 是否不等于 0。
bash 实现了许多此类比较操作 —— 你可以在 [`test`](https://www.man7.org/linux/man-pages/man1/test.1.html) 的手册页中找到完整列表。
在 bash 中进行比较时，尽量使用双括号 `[[ ]]` 而不是单括号 `[ ]`。这样可以降低犯错的概率，不过这样写无法兼容 `sh`。更详细的说明可以看[这里](https://mywiki.wooledge.org/BashFAQ/031)。

在运行脚本时，你经常需要提供格式相似的文件名。bash 提供了多种方式让这件事变得更简单——通过执行**文件名扩展**（filename expansion）。这些技术通常统称为 shell **通配**（globbing）。

- **通配符**（Wildcards）—— 当你需要进行某种模糊匹配时，可以使用 `?` 和 `*` 分别匹配一个字符或任意数量的字符。例如，给定文件 `foo`、`foo1`、`foo2`、`foo10` 和 `bar`，命令 `rm foo?` 会删除 `foo1` 和 `foo2`，而 `rm foo*` 会删除所有以 `foo` 开头的文件，保留 `bar`。
- **花括号扩展**（Curly braces `{}`）—— 当一系列命令中存在公共子串时，你可以使用花括号让 bash 自动展开。这在移动或转换文件时非常实用。

```bash
convert image.{png,jpg}
# Will expand to
convert image.png image.jpg

cp /path/to/project/{foo,bar,baz}.sh /newpath
# Will expand to
cp /path/to/project/foo.sh /path/to/project/bar.sh /path/to/project/baz.sh /newpath

# Globbing techniques can also be combined
mv *{.py,.sh} folder
# Will move all *.py and *.sh files


mkdir foo bar
# This creates files foo/a, foo/b, ... foo/h, bar/a, bar/b, ... bar/h
touch {foo,bar}/{a..h}
touch foo/x bar/y
# Show differences between files in foo and bar
diff <(ls foo) <(ls bar)
# Outputs
# < x
# ---
# > y
```

<!-- Lastly, pipes `|` are a core feature of scripting. Pipes connect one program's output to the next program's input. We will cover them more in detail in the data wrangling lecture. -->

编写 `bash` 脚本可能会有些棘手且不够直观。有一些工具（如 [shellcheck](https://github.com/koalaman/shellcheck)）可以帮助你发现 sh/bash 脚本中的错误。

需要注意的是，脚本不一定非得用 bash 编写——从终端调用的时候，其他语言的脚本同样可以执行。
下面是一个简单的 Python 脚本，它按逆序输出其所有参数：

```python
#!/usr/local/bin/python
import sys
for arg in reversed(sys.argv[1:]):
    print(arg)
```

内核（kernel）之所以知道用 Python 解释器而不是 shell 命令来执行这个脚本，是因为我们在脚本顶部加入了一行 [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)) 行。

在 shebang 中使用 [`env`](https://www.man7.org/linux/man-pages/man1/env.1.html) 命令是较好的做法——它会在系统路径中查找命令的实际位置，从而提高脚本的可移植性。`env` 会用到我们在第一节课程中介绍的 `PATH` 环境变量来解析路径。
这个例子的 shebang 行应写为 `#!/usr/bin/env python`。

shell 函数与脚本之间有一些区别，你应该牢记于心：

- 函数必须与 shell 使用同一种语言，而脚本可以用任何语言编写。这就是脚本中包含 shebang 很重要的原因。
- 函数在读取其定义时被加载一次；脚本则每次执行时都会重新加载。这使得函数的加载速度略快，但你一旦修改了函数，就必须重新加载其定义。
- 函数在**当前 shell 环境**中执行，而脚本在**独立的进程**中执行。因此，函数可以修改环境变量（例如更改当前目录），而脚本不能。通过 [`export`](https://www.man7.org/linux/man-pages/man1/export.1p.html) 导出的环境变量会以值传递的方式传递给脚本。
- 与任何编程语言一样，函数是实现模块化、代码复用和提高 shell 代码可读性的强大结构。大多数 shell 脚本中都会包含自己的函数定义。

# Shell 工具

## 了解如何使用命令

到了这个阶段，你可能想知道在之前的别名（aliasing）一节中提到的那些命令（如 `ls -l`、`mv -i`、`mkdir -p`）的标志（flag）究竟是何含义。
更一般地说，给定一个命令，你该如何了解它的作用以及它的各种选项？

你当然可以上网搜索，但由于 UNIX 的出现早于 Stack Overflow，系统本身提供了获取这些信息的内置方法。

正如我们在 shell 课程中看到的，最直接的方法是用 `-h` 或 `--help` 标志来调用该命令。
更详细的查询方式是使用 `man` 命令。
[`man`](https://www.man7.org/linux/man-pages/man1/man.1.html) 是 manual 的缩写，它为你指定的命令提供**手册页**（manpage）。
例如，`man rm` 会输出 `rm` 命令的行为说明及其接受的所有标志，包括我们之前提到的 `-i` 标志。
事实上，我之前为每个命令链接的，都是这些命令在 Linux 手册页中的在线版本。
即使是你安装的第三方命令，如果开发者编写了手册并把它包含在安装过程中，也会有对应的 manpage 条目。

对于基于 ncurses 的交互式工具，命令帮助通常可以通过在程序中键入 `:help` 或 `?` 来访问。

有时候，manpage 会对命令的描述过于详细，让人难以快速弄清在常见用法中应该使用哪些标志或语法。
[TLDR pages](https://tldr.sh/) 是一个很好的补充方案——它专注于提供命令的实际使用示例，让你快速找出该用哪些选项。
比如，我发现自己参考 [`tar`](https://tldr.inbrowser.app/pages/common/tar) 和 [`ffmpeg`](https://tldr.inbrowser.app/pages/common/ffmpeg) 的 tldr 页面的次数远多于它们的 manpage。

## 查找文件

每个程序员都会面临的一个最常见的重复性任务，就是查找文件（或目录）。
所有 UNIX 类系统都自带 [`find`](https://www.man7.org/linux/man-pages/man1/find.1.html)——一款功能强大的 shell 工具，用于查找文件。
`find` 会递归地搜索匹配某些条件的文件。几个例子：

```bash
# Find all directories named src
find . -name src -type d
# Find all python files that have a folder named test in their path
find . -path '*/test/*.py' -type f
# Find all files modified in the last day
find . -mtime -1
# Find all zip files with size in range 500k to 10M
find . -size +500k -size -10M -name '*.tar.gz'
```

除了列出文件，`find` 还可以对匹配查询的文件执行操作。
这个特性可以极大地简化那些相当单调的任务。

```bash
# Delete all files with .tmp extension
find . -name '*.tmp' -exec rm {} \;

# Find all PNG files and convert them to JPG
find . -name '*.png' -exec magick {} {}.jpg \;
```

尽管 `find` 无处不在，但它的语法有时不太好记。
例如，如果你只想查找匹配某个模式 `PATTERN` 的文件，你必须执行 `find -name '*PATTERN*'`（如果你希望匹配时不区分大小写，可以使用 `-iname`）。

你可以为此创建别名，但 shell 哲学的一部分是：多探索不同的方案总是好的。
请记住，shell 最优秀的特性之一就在于你只是在调用程序——所以你可以为某些工具找到（甚至自己编写）替代品。
例如，[`fd`](https://github.com/sharkdp/fd) 是一款简单、快速且用户友好的 `find` 替代品。
它提供了一些非常贴心的默认行为，如彩色输出、默认正则表达式匹配以及 Unicode 支持。我认为它的语法也更加直观。
例如，查找模式 `PATTERN` 的命令是 `fd PATTERN`。

大家普遍认为 `find` 和 `fd` 都不错，但你中可能有人在想：每次查找文件都效率太低了，有没有可能编译某种索引或数据库来加速搜索？
这正是 [`locate`](https://www.man7.org/linux/man-pages/man1/locate.1.html) 的作用。
`locate` 使用一个数据库，该数据库通过 [`updatedb`](https://www.man7.org/linux/man-pages/man1/updatedb.1.html) 进行更新。
在大多数系统中，`updatedb` 每天通过 [`cron`](https://www.man7.org/linux/man-pages/man8/cron.8.html) 定时更新一次。
因此这两种方案之间存在一个**速度 vs 新鲜度**的取舍。
此外，`find` 和类似工具还可以使用文件大小、修改时间或文件权限等属性来查找文件，而 `locate` 仅使用文件名。
更深入的对比可以参考[这里](https://unix.stackexchange.com/questions/60205/locate-vs-find-usage-pros-and-cons-of-each-other)。

## 查找代码

按名称查找文件很有用，但很多时候你想根据文件的**内容**进行搜索。
一种常见的需求是：查找所有包含某个模式的文件，以及该模式在文件中出现的具体位置。
对此，大多数 UNIX 类系统都提供了 [`grep`](https://www.man7.org/linux/man-pages/man1/grep.1.html)——一个从输入文本中匹配模式的通用工具。
`grep` 是一款极具价值的 shell 工具，我们将在数据处理课程中更深入地介绍它。

现在你只需要知道，`grep` 有许多标志使其成为非常灵活的工具。
我经常使用的一些标志包括：`-C` 用于获取匹配行**C**ontext（上下文），`-v` 用于 in**v**ert（反转）匹配，即打印所有**不**匹配该模式的行。
例如，`grep -C 5` 会打印匹配行前 5 行和后 5 行的上下文。

当需要在大量文件中快速搜索时，可以使用 `-R` 标志，它会递归地进入子目录并在文件中查找匹配字符串。

但 `grep -R` 还有很多改进空间，比如忽略 `.git` 文件夹、支持多核 CPU 等。
因此人们开发出了许多 `grep` 的替代品，包括 [ack](https://github.com/beyondgrep/ack3)、[ag](https://github.com/ggreer/the_silver_searcher) 和 [rg](https://github.com/BurntSushi/ripgrep)。
它们都非常优秀，功能基本相同。
目前我选择使用 ripgrep（`rg`），因为它既快速又直观。几个示例：

```bash
# Find all python files where I used the requests library
rg -t py 'import requests'
# Find all files (including hidden files) without a shebang line
rg -u --files-without-match "^#\!"
# Find all matches of foo and print the following 5 lines
rg foo -A 5
# Print statistics of matches (# of matched lines and files )
rg --stats PATTERN
```

需要注意的是，与 `find`/`fd` 的情况一样——重要的是你知道这类问题可以用这些工具快速解决，而具体使用哪一个工具并不是最关键的事。

## 查找 shell 命令

到目前为止，我们学会了如何查找文件和代码。但随着你在 shell 中花的时间越来越多，你可能想要找到自己曾经输入过的某个命令。

首先要知道，按下**上箭头键**会返回你上一条命令，持续按下去就会慢慢浏览你的 shell 历史记录。

`history` 命令可以让你以编程方式访问 shell 历史记录。
它会把你的 shell 历史打印到标准输出。
如果我们想在其中搜索，可以把输出管道传给 `grep` 来查找匹配的模式。
`history | grep find` 会输出包含子串 "find" 的命令。

在大多数 shell 中，你可以使用 `Ctrl+R` 在历史记录中进行**反向搜索**。
按下 `Ctrl+R` 后，你可以键入一个你想匹配的子串来搜索历史中的命令。
反复按下 `Ctrl+R` 会在匹配结果之间循环。
在 [zsh](https://github.com/zsh-users/zsh-history-substring-search) 中，这个功能也可以通过 UP/DOWN 箭头来启用。
在 `Ctrl+R` 的基础上，结合 [fzf](https://github.com/junegunn/fzf/wiki/Configuring-shell-key-bindings#ctrl-r) 的绑定，会有更好的体验。
`fzf` 是一款通用型的模糊查找器，可以与许多命令配合使用。
在这里它被用来模糊匹配你的历史记录，并以一种方便且视觉上令人愉悦的方式呈现结果。

另一个我很喜欢的与历史相关的技巧是**基于历史的自动补全**（history-based autosuggestions）。
这项功能最早由 [fish](https://fishshell.com/) shell 引入——它会根据你最近输入过的、与当前命令有共同前缀的命令，动态地自动补全当前 shell 命令。
它可以在 [zsh](https://github.com/zsh-users/zsh-autosuggestions) 中启用，是一个大幅提升 shell 使用体验的技巧。

你可以修改 shell 的历史记录行为，例如不让带有前导空格的命令被记录下来。
这在输入包含密码或其他敏感信息的命令时非常有用。
在 `.bashrc` 中添加 `HISTCONTROL=ignorespace` 或在 `.zshrc` 中添加 `setopt HIST_IGNORE_SPACE` 即可实现。
如果你不慎忘了加前导空格，始终可以通过编辑 `.bash_history` 或 `.zsh_history` 手动删除该条目。

## 目录导航

到目前为止，我们假设你已经身处需要操作的位置。
但如何快速地在目录之间导航呢？

当然有简单的方法，比如编写 shell 别名或使用 [ln -s](https://www.man7.org/linux/man-pages/man1/ln.1.html) 创建符号链接，但事实上，开发者们现在已经想出了相当巧妙且复杂的解决方案。

与本课程的主题一致——你经常应该为最常见的场景优化。
[`fasd`](https://github.com/clvv/fasd) 和 [`autojump`](https://github.com/wting/autojump) 等工具可以快速查找常用和/或最近的目录。
fasd 按照**_最近频度_**（_frecency_，即 _frequency_ 频率 + _recency_ 最近程度）对文件和目录进行排名。
默认情况下，`fasd` 会添加一个 `z` 命令，让你可以使用**子字符串**快速 `cd` 到一个最近访问过的目录。
例如，如果你经常去 `/home/user/files/cool_project`，只需 `z cool` 就能跳转过去。
使用 autojump，同样的跳转可以用 `j cool` 来实现。

还有一些更复杂的工具可以帮你快速了解一个目录的整体结构，例如 [`tree`](https://linux.die.net/man/1/tree)、[`broot`](https://github.com/Canop/broot)，甚至是功能完整的全套文件管理器，如 [`nnn`](https://github.com/jarun/nnn) 或 [`ranger`](https://github.com/ranger/ranger)。

# 练习

1. 阅读 [`man ls`](https://www.man7.org/linux/man-pages/man1/ls.1.html)，写出一个满足以下要求的 `ls` 命令：

    - 列出所有文件，包括隐藏文件
    - 以人类可读的格式显示文件大小（如 1.1M 而不是 1153433）
    - 按最近修改时间排序
    - 输出带颜色

    一个示例输出如下：

    ```
    -rw-r--r--   1 user group 1.1M Jan 14 09:53 baz
    drwxr-xr-x   5 user group  160 Jan 14 09:53 .
    -rw-r--r--   1 user group  514 Jan 14 06:42 bar
    -rw-r--r--   1 user group 106M Jan 13 12:12 foo
    drwx------+ 47 user group 1.5K Jan 12 18:08 ..
    ```

{% comment %}
ls -lath --color=auto
{% endcomment %}

1. 编写两个 bash 函数 `marco` 和 `polo`，功能如下：
   每当你执行 `marco` 时，应将当前工作目录以某种方式保存下来；之后无论你在哪个目录下执行 `polo`，它都应把你 `cd` 回到你执行 `marco` 时的那个目录。
   为方便调试，你可以将代码写入 `marco.sh` 文件，然后通过执行 `source marco.sh` 重新加载到 shell 中。

{% comment %}
marco() {
    export MARCO=$(pwd)
}

polo() {
    cd "$MARCO"
}
{% endcomment %}

1. 假设你有一个偶尔才会失败的命令。为了调试它，你需要捕获它的输出，但等待一次失败可能需要很长时间。
   请编写一个 bash 脚本，运行下面的脚本直到它失败，捕获它的标准输出和标准错误到文件中，并在最后一次性打印所有内容。
    Bonus：如果你还能报告脚本失败前共运行了多少次，则额外加分。

    ```bash
    #!/usr/bin/env bash

    n=$(( RANDOM % 100 ))

    if [[ n -eq 42 ]]; then
       echo "Something went wrong"
       >&2 echo "The error was using magic numbers"
       exit 1
    fi

    echo "Everything went according to plan"
    ```

{% comment %}
#!/usr/bin/env bash

count=0
until [[ "$?" -ne 0 ]];
do
  count=$((count+1))
  ./random.sh &> out.txt
done

found error after $count runs
cat out.txt
{% endcomment %}

1. 正如我们在课程中所学，`find` 的 `-exec` 功能对于对搜索结果中的文件执行操作非常强大。
   但如果你想对**所有**文件做某件事（比如创建一个 zip 压缩包）该怎么办？
   到目前为止你应该已经知道，命令可以从参数和 STDIN 接收输入。
   在使用管道时，我们连接的是 STDOUT 和 STDIN，但有些命令（如 `tar`）需要从参数中获取输入。
   为了弥合这一鸿沟，有 [`xargs`](https://www.man7.org/linux/man-pages/man1/xargs.1.html) 命令——它会使用 STDIN 作为参数来执行命令。
   例如 `ls | xargs rm` 会删除当前目录中的所有文件。

    你的任务是：编写一条命令，递归查找文件夹中所有的 HTML 文件，并为它们创建一个 zip 包。
    注意，你的命令应该即使在文件名中包含空格的情况下也能正常工作（提示：查看 `xargs` 的 `-d` 标志）。
    {% comment %}
    find . -type f -name "*.html" | xargs -d '\n'  tar -cvzf archive.tar.gz
    {% endcomment %}

    如果你使用的是 macOS，请注意默认的 BSD `find` 与 [GNU coreutils](https://en.wikipedia.org/wiki/List_of_GNU_Core_Utilities_commands) 中包含的不太一样。你可以在 `find` 中使用 `-print0`，在 `xargs` 中使用 `-0` 标志。
    作为 macOS 用户，你应该意识到 macOS 自带的命令行工具可能与 GNU 对应版本存在差异——如果需要，你可以使用 [Homebrew](https://brew.sh/) 安装 GNU 版本。

1. （进阶）编写一条命令或脚本，递归查找一个目录中**最近修改**的文件。
   更一般地，你能按修改时间倒序列出所有文件吗？