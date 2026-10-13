---
layout: lecture
title: "命令行环境"
description: >
  了解命令行程序的工作原理，包括输入/输出流、环境变量，以及通过 SSH 使用远程机器。
thumbnail: /static/assets/thumbnails/2026/lec2.png
date: 2026-01-13
ready: true
video:
  aspect: 56.25
  id: ccBGsPedE9Q
---

如上一讲所述，大多数 shell（命令行解释器）并不只是启动其他程序的简单外壳，它们在实践中提供了一套完整的编程语言，其中包含丰富的常用模式与抽象。然而，与大多数编程语言不同的是，shell 脚本的所有设计都围绕着"运行程序并让程序之间简洁高效地通信"这一核心展开。

特别是，shell 脚本深受 _约定俗成_（conventions）的约束。为了让一个命令行接口（CLI）程序在更广泛的 shell 环境中顺畅工作，它需要遵循一些通用模式。接下来我们将覆盖许多关键概念，帮助你理解命令行程序是如何工作的，以及广泛使用的关于如何配置和使用它们的基本约定。

# 命令行接口

在大多数编程语言中，编写一个函数的样子大致如下：

```
def add(x: int, y: int) -> int:
    return x + y
```

这里我们可以清晰地看到程序的输入和输出。相比之下，shell 脚本初看可能截然不同。

```shell
#!/usr/bin/env bash

if [[ -f $1 ]]; then
    echo "Target file already exists"
    exit 1
else
    if $DEBUG; then
        grep 'error' - | tee $1
    else
        grep 'error' - > $1
    fi
    exit 0
fi
```

要正确理解类似这样的脚本在做什么，我们首先需要引入一些概念——这些概念在 shell 程序之间或与 shell 环境通信时经常碰到：

- 参数（Arguments）
- 流（Streams）
- 环境变量（Environment variables）
- 返回码（Return codes）
- 信号（Signals）

## 参数

Shell 程序在执行时会接收到一个参数列表。在 shell 中，参数就是普通的字符串，程序如何解读它们完全由程序自身决定。例如，当我们执行 `ls -l folder/` 时，我们实际上是在用参数 `['-l', 'folder/']` 来运行 `/bin/ls` 这个程序。

在 shell 脚本内部，我们可以通过特殊的 shell 语法访问这些参数。第一个参数通过变量 `$1` 访问，第二个通过 `$2`，依此类推直到 `$9`。要一次性获取所有参数，我们使用 `$@`；要获取参数总数，使用 `$#`。此外，我们也可以通过 `$0` 获取程序自身的名称。

对于大多数程序而言，参数通常由 _标志（flags）_ 和普通字符串混合组成。标志之所以可以被识别，是因为它们以单破折号（`-`）或双破折号（`--`）开头。标志通常用于可选地修改程序的行为。例如 `ls -l` 改变了 `ls` 输出内容的格式。

你会看到带有长名称的双破折号标志，如 `--all`，以及带有单个字母的单破折号标志，如 `-a`。同一个选项经常可以两种格式都指定——`ls -a` 和 `ls --all` 是等价的。单破折号标志经常被缩写组合在一起，因此 `ls -l -a` 和 `ls -la` 也是等价的。标志的顺序通常也不影响结果——`ls -la` 和 `ls -al` 会产生相同的结果。有些标志相当普遍，当你越来越熟悉 shell 环境时，你会直觉性地使用它们，例如（`--help`、`--verbose`、`--version`）。

> 标志是 shell 约定的第一个好例子。shell 语言本身并不要求我们的程序以 `-` 或 `--` 的特定方式使用标志。我们完全可以写一个语法为 `myprogram +myoption myfile` 的程序，但这会引起混淆，因为使用者的预期是程序会使用破折号。
> 实际上，大多数编程语言都提供了 CLI 标志解析库（例如 Python 中的 `argparse`，用于解析使用破折号语法的参数）。

CLI 程序中的另一个常见约定是接受可变数量的同类型参数。当以这种方式给出参数时，命令会对每一个参数执行相同的操作。

```shell
mkdir src
mkdir docs
# 等价于
mkdir src docs
```

这种语法糖乍看似乎没有必要，但当与 _通配匹配（globbing）_ 结合时就会变得非常强大。通配匹配（或简称为 globs）是 shell 会在调用程序之前展开的特殊模式。

假设我们想要非递归地删除当前文件夹中所有 `.py` 文件。根据上一讲中学到的知识，我们可以通过运行以下命令来实现：

```shell
for file in $(ls | grep -P '\.py$'); do
    rm "$file"
done
```

但我们可以直接替换为 `rm *.py`！

当我们在终端中输入 `rm *.py` 时，shell 并不会调用 `/bin/rm` 这个程序并传入参数 `['*.py']`。相反，shell 会搜索当前文件夹中所有匹配 `*.py` 模式的文件——其中 `*` 可以匹配任意类型的零个或多个字符。因此，如果我们的文件夹中有 `main.py` 和 `utils.py`，那么 `rm` 程序实际收到的参数将是 `['main.py', 'utils.py']`。

你最会遇到的常见通配匹配模式包括通配符 `*`（任意类型的零个或多个）、`?`（恰好一个任意字符）和大括号 `{}`。大括号 `{}` 会将逗号分隔的模式列表展开为多个参数。

在实践中，用一些有代表性的例子来理解通配匹配效果最好。

```shell
touch folder/{a,b,c}.py
# 将展开为
touch folder/a.py folder/b.py folder/c.py

convert image.{png,jpg}
# 将展开为
convert image.png image.jpg

cp /path/to/project/{setup,build,deploy}.sh /newpath
# 将展开为
cp /path/to/project/setup.sh /path/to/project/build.sh /path/to/project/deploy.sh /newpath

# 通配匹配技巧也可以组合使用
mv *{.py,.sh} folder
# 将移动所有 *.py 和 *.sh 文件
```

> 某些 shell（如 zsh）支持更多高级形式的通配匹配，例如 `**`，它会将递归路径也展开。因此 `rm **/*.py` 将递归地删除所有 .py 文件。


## 流

每当我们执行类似下面的命令管道时：

```shell
cat myfile | grep -P '\d+' | uniq -c
```

我们可以看到 `grep` 程序同时与 `cat` 和 `uniq` 程序进行通信。

一个重要的观察是，这三个程序实际上是**同时**在执行的。也就是说，shell 并不会先调用 `cat`、然后 `grep`、再然后 `uniq`。相反，shell 会一次性启动全部三个程序，并将 `cat` 的输出连接到 `grep` 的输入，再将 `grep` 的输出连接到 `uniq` 的输入。在使用管道操作符 `|` 时，shell 处理的是在一连串程序之间流动的数据流。

我们可以通过以下方式证明这种并发关系——管道中的所有命令都会立即启动：

```console
$ (sleep 15 && cat numbers.txt) | grep -P '^\d$' | sort | uniq  &
[1] 12345
$ ps | grep -P '(sleep|cat|grep|sort|uniq)'
  32930 pts/1    00:00:00 sleep
  32931 pts/1    00:00:00 grep
  32932 pts/1    00:00:00 sort
  32933 pts/1    00:00:00 uniq
  32948 pts/1    00:00:00 grep
```

我们可以看到，除了 `cat` 之外的所有进程都立即在运行。shell 会一次性生成所有进程，在所有进程结束之前就将它们的流连接起来。`cat` 要等到 `sleep` 完成后才会启动，而 `cat` 的输出会被发送到 `grep`，依此类推。

每个程序都有一个输入流，称为 _stdin_（标准输入）。进行管道连接时，stdin 会被自动连接。在脚本中，许多程序将 `-` 作为文件名来接受"从 stdin 读取"：

```shell
# 当数据来自管道时，以下两条等价
echo "hello" | grep "hello"
echo "hello" | grep "hello" -
```

类似地，每个程序还有两个输出流：stdout（标准输出）和 stderr（标准错误）。标准输出是最常见的，它用于将程序的输出管道连接到下一道命令。标准错误则是一个备用流，供程序报告警告和其他类型的问题，而不让这部分输出被链中的下一道命令解析。

```console
$ ls /nonexistent
ls: cannot access '/nonexistent': No such file or directory
$ ls /nonexistent | grep "pattern"
ls: cannot access '/nonexistent': No such file or directory
# 错误信息仍然会出现，因为 stderr 并未被管道化
$ ls /nonexistent 2>/dev/null
# 无输出——stderr 被重定向到了 /dev/null
```

shell 提供了重定向这些流的语法。以下是一些示例。

```shell
# 将 stdout 重定向到文件（覆盖）
echo "hello" > output.txt

# 将 stdout 重定向到文件（追加）
echo "world" >> output.txt

# 将 stderr 重定向到文件
ls foobar 2> errors.txt

# 将 stdout 和 stderr 重定向到同一个文件
ls foobar &> all_output.txt

# 将 stdin 从文件读取
grep "pattern" < input.txt

# 通过将输出重定向到 /dev/null 来丢弃输出
cmd > /dev/null 2>&1
```

另一个体现 Unix 哲学的强大工具是 [`fzf`](https://github.com/junegunn/fzf)，一个模糊查找器。它从 stdin 读取行数据，并提供一个交互式界面来过滤和选择：

```console
$ ls | fzf
$ cat ~/.bash_history | fzf
```

`fzf` 可以与许多 shell 操作集成。在讨论 shell 定制时我们会看到更多用法。


## 环境变量

在 bash 中为变量赋值使用的语法是 `foo=bar`，然后通过 `$foo` 语法来访问该变量的值。注意，`foo = bar` 是无效的语法——shell 会将其解析为调用程序 `foo`，并传入参数 `['=', 'bar']`。在 shell 脚本中，空格字符的作用是进行参数分隔。这种行为可能令人困惑，也不容易习惯，所以需要牢记。

Shell 变量没有类型，它们全是字符串。注意在 shell 中编写字符串表达式时，单引号和双引号并非可以互换的。以 `'` 括起来的字符串是纯文字字符串，不会展开变量、不会执行命令替换、也不处理转义序列；而以 `"` 括起来的字符串则可以做这些事。

```shell
foo=bar
echo "$foo"
# 输出 bar
echo '$foo'
# 输出 $foo
```

要捕获命令的输出并赋给变量，我们使用 _命令替换_（command substitution）。当我们执行：

```shell
files=$(ls)
echo "$files" | grep README
echo "$files" | grep ".py"
```

`ls` 的输出（更确切地说是 stdout）会被放入变量 `$files` 中，我们稍后可以访问它。`$files` 变量的内容确实包含了 `ls` 输出中的换行符，这也是 `grep` 等程序知道如何独立处理每一项的原因。

一个较少人知道但类似的特性是 _进程替换_（process substitution），`<( CMD )` 会执行 `CMD` 并将输出放在一个临时文件中，然后以该文件的名称替换 `<()`。这在命令需要通过文件而不是通过 STDIN 来接收值时很有用。例如，`diff <(ls src) <(ls docs)` 将显示 `src` 和 `docs` 两个目录中文件的差异。

每当一个 shell 程序调用另一个程序时，它还会传递一组变量，通常被称为 _环境变量_。在 shell 中，我们可以运行 `printenv` 来查看当前的环境变量。要显式地传递一个环境变量，我们可以在命令前加上变量赋值：

> 环境变量惯例上全部大写（例如 `HOME`、`PATH`、`DEBUG`）。这是一种惯例而非技术要求，但遵循这一惯例有助于将环境变量与通常是小写的本地 shell 变量区分开来。

```shell
TZ=Asia/Tokyo date  # 打印东京的当前时间
echo $TZ  # 这将为空，因为 TZ 仅对子命令设置
```

或者，我们可以使用内建的 `export` 命令来修改当前环境，从而使所有子进程都继承该变量：

```shell
export DEBUG=1
# 从这里开始的所有程序都将有 DEBUG=1 在其环境中
bash -c 'echo $DEBUG'
# 输出 1
```

要删除一个变量，使用内建命令 `unset`，例如 `unset DEBUG`。

> 环境变量是另一个 shell 约定。它们可以用来隐式地而非显式地修改许多程序的行为。例如，shell 会将当前用户的主目录路径设置到环境变量 `$HOME` 中。然后程序可以访问这个变量来获取信息，而不需要显式的 `--home /home/alice`。另一个常见例子是 `$TZ`，许多程序用它来根据指定的时区格式化日期和时间。

## 返回码

如前所述，shell 程序的主要输出通过 stdout/stderr 流和文件系统副作用来传达。

默认情况下，shell 脚本会返回退出码零。惯例是：零表示一切顺利，非零则表示遇到了某些问题。要返回一个非零退出码，我们必须使用 shell 内建的 `exit NUM`。我们可以通过访问特殊变量 `$?` 来查看上一个运行的命令的返回码。

shell 拥有布尔操作符 `&&` 和 `||` 来分别执行 AND 和 OR 运算。与我们在常规编程语言中遇到的不同，shell 中的操作符针对的是程序的返回码。这两个操作符都是[短路求值](https://en.wikipedia.org/wiki/Short-circuit_evaluation)操作符。这意味着它们可用于根据前一个命令的成功或失败来条件性地运行命令——成功与否取决于返回码是否为零。一些示例：

```shell
# 只有当 grep 成功（找到匹配）时才会执行 echo
grep -q "pattern" file.txt && echo "Pattern found"

# 只有当 grep 失败（无匹配）时才会执行 echo
grep -q "pattern" file.txt || echo "Pattern not found"

# true 是一个总是成功的 shell 程序
true && echo "This will always print"

# 而 false 是一个总是失败的 shell 程序
false || echo "This will always print"
```

`if` 和 `while` 语句遵循相同的原则——它们都使用返回码来做决策：

```shell
# if 使用条件命令的返回码（0 = 真，非零 = 假）
if grep -q "pattern" file.txt; then
    echo "Found"
fi

# while 循环只要命令返回 0 就继续
while read line; do
    echo "$line"
done < file.txt
```

## 信号

在某些情况下，你可能需要在程序执行过程中中断它，例如某个命令需要花费太长时间才能完成。中断程序最简单的方法是按下 `Ctrl-C`，程序大概率会停止。但这实际上是如何运作的，为什么有时它无法让进程停止？

```console
$ sleep 100
^C
$
```

> 注意，这里的 `^C` 是在终端中键入 `Ctrl-C` 时的显示方式。

在底层，这里发生的过程如下：

1. 我们按下了 `Ctrl-C`
2. shell 识别出了这个特殊的字符组合
3. shell 进程向 `sleep` 进程发送了一个 SIGINT 信号
4. 该信号中断了 `sleep` 进程的执行

信号是一种特殊的通信机制。当一个进程接收到信号时，它会停止执行、处理该信号，并根据信号所携带的信息潜在地改变执行流程。因此，信号是 _软件中断_（software interrupts）。

在我们的案例中，输入 `Ctrl-C` 会促使 shell 向该进程发送一个 `SIGINT` 信号。下面是一个简单的 Python 程序示例——它捕获 `SIGINT` 并忽略它，不再停止。要终止这个程序，我们可以改用 `SIGQUIT` 信号，即键入 `Ctrl-\`。

```python
#!/usr/bin/env python
import signal, time

def handler(signum, time):
    print("\nI got a SIGINT, but I am not stopping")

signal.signal(signal.SIGINT, handler)
i = 0
while True:
    time.sleep(.1)
    print("\r{}".format(i), end="")
    i += 1
```

如果我们向这个程序发送两次 `SIGINT`，再发送一次 `SIGQUIT`，会发生以下情况。注意，`^` 是在终端中键入 `Ctrl` 时的显示方式。

```console
$ python sigint.py
24^C
I got a SIGINT, but I am not stopping
26^C
I got a SIGINT, but I am not stopping
30^\[1]    39913 quit       python sigint.py
```

虽然 `SIGINT` 和 `SIGQUIT` 通常都与终端相关的请求有关，但一个更通用的、用于请求进程优雅退出的信号是 `SIGTERM`。要发送这个信号，我们可以使用 [`kill`](https://www.man7.org/linux/man-pages/man1/kill.1.html) 命令，语法为 `kill -TERM <PID>`。

信号的功能不仅仅是杀死进程。例如，`SIGSTOP` 可以暂停一个进程。在终端中，键入 `Ctrl-Z` 会促使 shell 发送一个 `SIGTSTP` 信号，即 Terminal Stop 的缩写（也就是终端版本的 `SIGSTOP`）。

随后我们可以使用 [`fg`](https://www.man7.org/linux/man-pages/man1/fg.1p.html) 或 [`bg`](https://man7.org/linux/man-pages/man1/bg.1p.html) 分别在前台或后台继续运行被暂停的任务。

[`jobs`](https://www.man7.org/linux/man-pages/man1/jobs.1p.html) 命令列出了与当前终端会话关联的未完成任务。你可以使用它们的 pid 来引用这些任务（可以用 [`pgrep`](https://www.man7.org/linux/man-pages/man1/pgrep.1.html) 来查找 pid）。更直观地，你也可以使用百分号后面跟任务编号的方式来引用一个进程（编号由 `jobs` 显示）。要引用上一个放入后台的任务，可以使用 `$!` 这个特殊参数。

还有一件事需要知道：命令后面加上 `&` 后缀可以让命令在后台运行，将提示符返还给你，但它仍然会使用 shell 的 STDOUT，这可能会令人困扰（在这种情况下可以使用 shell 重定向）。等价地，要让一个已经在运行的程序进入后台，你可以先按 `Ctrl-Z`，然后执行 `bg`。

> 译者补充：后台进程仍然是你终端的子进程，关闭终端时它们会被杀死（这又会发送另一个信号 `SIGHUP`）。为了防止这种情况，你可以使用 [`nohup`](https://www.man7.org/linux/man-pages/man1/nohup.1.html)（一个忽略 `SIGHUP` 的包装器）来运行程序，如果进程已经在运行了，可以使用 `disown`。另外，你也可以使用终端复用器，我们在下一节会看到。

下面是展示上述部分概念的一个会话示例。

```
$ sleep 1000
^Z
[1]  + 18653 suspended  sleep 1000

$ nohup sleep 2000 &
[2] 18745
appending output to nohup.out

$ jobs
[1]  + suspended  sleep 1000
[2]  - running    nohup sleep 2000

$ kill -SIGHUP %1
[1]  + 18653 hangup     sleep 1000

$ kill -SIGHUP %2   # nohup 保护进程免受 SIGHUP

$ jobs
[2]  + running    nohup sleep 2000

$ kill %2
[2]  + 18745 terminated  nohup sleep 2000
```

一个特殊的信号是 `SIGKILL`，因为它不能被进程捕获，它将总是立即终止进程。然而，它可能会带来不良副作用，例如留下孤儿子进程。

你可以[在此处](https://en.wikipedia.org/wiki/Signal_(IPC))了解这些信号以及其他信号的更多信息，或者键入 [`man signal`](https://www.man7.org/linux/man-pages/man7/signal.7.html) 或 `kill -l`。

在 shell 脚本中，你可以使用内建的 `trap` 命令来在接收到信号时执行命令。这对于清理操作很有用：

```shell
#!/usr/bin/env bash
cleanup() {
    echo "Cleaning up temporary files..."
    rm -f /tmp/mytemp.*
}
trap cleanup EXIT  # 脚本退出时执行清理
trap cleanup SIGINT SIGTERM  # 也在 Ctrl-C 或 kill 时执行
```
{% comment %}
### 用户、文件和权限

最后，程序还有一种间接通信的方式——使用文件。要让程序正确地读取/写入/删除文件和文件夹，文件权限必须允许该操作。

列出特定文件将产生如下输出：

```console
$ ls -l notes.txt
-rw-r--r--  1 alice  users  12693 Jan 11 23:05 notes.txt
```

在这里 `ls` 列出了文件的所有者是用户 `alice`，组是 `users`。然后 `rw-r--r--` 是一种表示权限的缩写。在此案例中，文件 `notes.txt` 对 alice 用户有读写权限 `rw-`，而对组和其他用户只有读权限。

```console
$ ./script.sh
# 权限被拒绝
$ chmod +x script.sh
$ ls -l script.sh
-rwxr-xr-x  1 alice  users  3125 Jan 11 23:07 script.sh
$ ./script.sh
```

要使一个脚本可执行，必须设置可执行权限，这就是我们为什么必须使用 `chmod`（change mode，修改模式）程序的原因。`chmod` 的语法虽然直观，但首次接触时并不明显。如果你和我一样更喜欢通过示例来学习，那么 `tldr` 工具（注意，你需要先安装它）是一个很好的用例。

```console
❯ tldr chmod
  Change the access permissions of a file or directory.
  More information: <https://www.gnu.org/software/coreutils/chmod>.

  Give the [u]ser who owns a file the right to e[x]ecute it:

      chmod u+x path/to/file

  Give the [u]ser rights to [r]ead and [w]rite to a file/directory:

      chmod u+rw path/to/file

  Give [a]ll users rights to [r]ead and e[x]ecute:

      chmod a+rx path/to/file
```

运行 `tldr chmod` 查看更多示例，包括递归操作和组权限。

> 你的 shell 可能会显示 `command not found: tldr`。这是因为它是一个较新的工具，大多数系统没有预装。关于如何安装工具的很好参考是 [https://command-not-found.com](https://command-not-found.com) 这个网站。它包含了大量 CLI 工具的说明，面向流行的操作系统发行版。

每个程序都以系统上的特定用户身份运行。我们可以使用 `whoami` 命令来查找我们的用户名，使用 `id -u` 来查找我们的 UID（用户标识，即操作系统分配给该用户的整数值）。

当运行 `sudo command` 时，`command` 将以 root 用户身份运行，这可以绕过系统的大多数权限。尝试运行 `sudo whoami` 和 `sudo id -u` 来看看输出如何变化（你可能会被要求输入密码）。要更改文件或文件夹的所有者，我们使用 `chown` 命令。

你可以在[这里](https://en.wikipedia.org/wiki/File-system_permissions#Traditional_Unix_permissions)了解有关 UNIX 文件权限的更多信息。

到目前为止我们专注于本地机器，但很多这些技能在配合远程服务器使用时价值更大。

{% endcomment %}

# 远程机器

程序员在日常工作中使用远程服务器变得越来越普遍。这里最常用的工具是 SSH（Secure Shell，安全外壳），它将帮助我们连接到远程机器并提供现在熟悉的 shell 接口。我们通过如下命令连接到服务器：

```bash
ssh alice@server.mit.edu
```

这里我们尝试以用户 `alice` 的身份 ssh 到服务器 `server.mit.edu`。

`ssh` 的一个经常被忽略的特性是它有能力非交互式地运行命令。`ssh` 会正确处理发送命令的 stdin 并接收其 stdout，因此我们可以将它与其他命令结合使用。

```shell
# 此处 ls 在远程端运行，wc 在本地运行
ssh alice@server ls | wc -l

# 此处 ls 和 wc 都在远程端运行
ssh alice@server 'ls | wc -l'

```

> 尝试安装 [Mosh](https://mosh.org/) 作为 SSH 的替代品，它可以处理断线、进入/退出睡眠状态、切换网络以及处理高延迟链路。

要让 `ssh` 允许我们在远程服务器上运行命令，我们需要证明自己是经过授权的。这可以通过密码或 SSH 密钥来完成。基于密钥的身份验证利用公钥密码学来向服务器证明客户端拥有私钥的密钥，而无需泄露密钥。基于密钥的身份验证既更方便也更安全，因此你应该优先使用它。注意，私钥（通常是 `~/.ssh/id_rsa`，以及较新的 `~/.ssh/id_ed25519`）实际上就是你的密码，因此请像对待密码一样对待它，永远不要共享其内容。

要生成密钥对，你可以运行 [`ssh-keygen`](https://www.man7.org/linux/man-pages/man1/ssh-keygen.1.html)。
```bash
ssh-keygen -a 100 -t ed25519 -f ~/.ssh/id_ed25519
```

如果你曾经配置过使用 SSH 密钥推送到 GitHub，那么你可能已经按照[这里的步骤](https://help.github.com/articles/connecting-to-github-with-ssh/)进行操作了，并且已经拥有一对有效的密钥。要检查你是否设置了 passphrase 并验证它，你可以运行 `ssh-keygen -y -f /path/to/key`。

在服务器端，`ssh` 会查找 `.ssh/authorized_keys` 来决定哪些客户端应该被允许进入。要将公钥复制到服务器上，你可以使用：

```bash
cat .ssh/id_ed25519.pub | ssh alice@remote 'cat >> ~/.ssh/authorized_keys'

# 或者更简单地（如果 ssh-copy-id 可用）

ssh-copy-id -i .ssh/id_ed25519 alice@remote
```

除了运行命令之外，`ssh` 建立的连接还可以用来安全地从服务器传输文件到本地以及从本地传输到服务器。[`scp`](https://www.man7.org/linux/man-pages/man1/scp.1.html) 是最传统的工具，语法为 `scp path/to/local_file remote_host:path/to/remote_file`。[`rsync`](https://www.man7.org/linux/man-pages/man1/rsync.1.html) 通过检测本地和远程中相同文件来改进 `scp`，并避免重复复制。它还可以对符号链接和权限提供更细粒度的控制，并拥有诸如 `--partial` 标志之类的额外功能，可以从之前中断的复制处恢复。`rsync` 的语法与 `scp` 类似。

SSH 客户端配置位于 `~/.ssh/config`，它允许我们为主机声明配置并设置默认参数。此配置文件不仅仅是 `ssh` 会读取的——其他程序如 `scp`、`rsync`、`mosh` 等也会读取它。

```bash
Host vm
    User alice
    HostName 172.16.174.141
    Port 2222
    IdentityFile ~/.ssh/id_ed25519

# 配置也可以使用通配符
Host *.mit.edu
    User alice
```



# 终端复用器

在使用命令行接口时，你经常需要同时运行多个程序。例如，你可能想要并排运行编辑器和程序。虽然可以通过打开新的终端窗口来实现，但使用终端复用器是更灵活的解决方案。

终端复用器如 [`tmux`](https://www.man7.org/linux/man-pages/man1/tmux.1.html) 允许你使用面板和标签来复用终端窗口，从而让你以高效的方式与多个 shell 会话进行交互。此外，终端复用器让你可以分离当前的终端会话，并在之后重新附加。因此，终端复用器在使用远程机器时非常方便，因为它避免了对 `nohup` 等技巧的需求。

当今最受欢迎的终端复用器是 [`tmux`](https://www.man7.org/linux/man-pages/man1/tmux.1.html)。`tmux` 高度可配置，使用其关联的快捷键，你可以创建多个标签和面板，并快速在它们之间导航。

`tmux` 期望你了解它的快捷键，所有快捷键的形式都是 `<C-b> x`，这意味着：(1) 按下 `Ctrl+b`，(2) 释放 `Ctrl+b`，然后 (3) 按下 `x`。`tmux` 有以下层级的对象：

- **会话（Sessions）** —— 一个会话是一个独立的工作空间，包含一个或多个窗口
    + `tmux` 启动一个新的会话。
    + `tmux new -s NAME` 以指定名称启动。
    + `tmux ls` 列出当前会话。
    + 在 `tmux` 内键入 `<C-b> d` 分离当前会话。
    + `tmux a` 附加最后的会话。可以使用 `-t` 标志来指定哪一个。

- **窗口（Windows）** —— 等价于编辑器或浏览器中的标签，它们是同一会话中视觉上不同的部分
    + `<C-b> c` 创建新窗口。要关闭它，只需通过 `<C-d>` 终止 shell 即可。
    + `<C-b> N` 前往第 _N_ 个窗口。注意它们是有编号的。
    + `<C-b> p` 前往上一个窗口。
    + `<C-b> n` 前往下一个窗口。
    + `<C-b> ,` 重命名当前窗口。
    + `<C-b> w` 列出当前窗口。

- **面板（Panes）** —— 类似于 vim 的分割，面板让你在同一个视觉显示中拥有多个 shell。
    + `<C-b> "` 水平分割当前面板。
    + `<C-b> %` 垂直分割当前面板。
    + `<C-b> <方向>` 移动到指定_方向_的面板。方向即方向键。
    + `<C-b> z` 切换当前面板的缩放状态。
    + `<C-b> [` 开始回滚模式。之后可以按 `<space>` 开始选择，按 `<enter>` 复制该选择。
    + `<C-b> <space>` 循环切换面板排列方式。

> 要了解关于 tmux 的更多信息，请阅读[这篇](https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/)快速教程和[这篇](https://linuxcommand.org/lc3_adv_termmux.php)更详细的解释。

在拥有了 tmux 和 SSH 这两个工具后，你会希望在任何机器上都能让你的环境变得熟悉和舒适。这就是 shell 定制的用武之地。

# 定制 Shell

大量命令行程序使用名为 _点文件_（dotfiles）的纯文本文件来配置（因为文件名以 `.` 开头，例如 `~/.vimrc`，这样它们在 `ls` 目录列表中默认被隐藏）。

> 点文件是另一个 shell 约定。前面的 `.` 是为了在列出时"隐藏"它们（是的，又是一个约定）。

Shell 是使用这些文件进行配置的程序之一。在启动时，你的 shell 会读取许多文件来加载其配置。根据 shell 的种类，以及你启动的是登录会话（login session）和/或交互式会话（interactive session），整个过程可能相当复杂。[这里](https://web.archive.org/web/20260329133158/https://blog.flowblok.id.au/2013-02/shell-startup-scripts.html)有一篇关于该主题的出色参考资料。

对于 `bash`，编辑 `.bashrc` 或 `.bash_profile` 在大多数系统上都能工作。其他一些可以通过点文件配置的工具的例子包括：

- `bash` - `~/.bashrc`、`~/.bash_profile`
- `git` - `~/.gitconfig`
- `vim` - `~/.vimrc` 以及 `~/.vim` 文件夹
- `ssh` - `~/.ssh/config`
- `tmux` - `~/.tmux.conf`

一个常见的配置更改是向 shell 中添加查找程序的新路径。在安装软件时你会遇到这种模式：

```shell
export PATH="$PATH:path/to/append"
```

这里，我们告诉 shell 将 `$PATH` 变量的值设置为它当前的值再加上一个新增路径，并让所有子进程都继承这个新 PATH 值。这将允许子进程找到位于 `path/to/append` 下的程序。

定制你的 shell 通常意味着安装新的命令行工具。包管理器让这变得非常简单——它们负责下载、安装和更新软件。不同的操作系统有不同的包管理器：macOS 使用 [Homebrew](https://brew.sh/)，Ubuntu/Debian 使用 `apt`，Fedora 使用 `dnf`，而 Arch 使用 `pacman`。我们将在"发布代码"讲中更深入地讨论包管理器。

以下是如何使用 Homebrew 在 macOS 上安装两个实用工具：

```shell
# ripgrep：一个默认设置更佳的更快 grep
brew install ripgrep

# fd：一个更快、对用户更友好的 find
brew install fd
```

安装这些之后，你可以使用 `rg` 替代 `grep`，使用 `fd` 替代 `find`。

> **关于 `curl | bash` 的警告**：你经常会看到类似 `curl -fsSL https://example.com/install.sh | bash` 的安装指令。这种模式会下载一个脚本并立即执行它，虽然方便但存在风险——你正在执行未经审查的代码。更安全的方法是：先下载、审查、再执行：
> ```shell
> curl -fsSL https://example.com/install.sh -o install.sh
> less install.sh  # 审查脚本
> bash install.sh
> ```
> 有些安装器会使用一种稍微更安全的变体：`/bin/bash -c "$(curl -fsSL https://url)"`，这至少确保 bash 解释该脚本而不是你当前的 shell。

当你尝试运行一个未安装命令时，你的 shell 会显示 `command not found`。网站 [command-not-found.com](https://command-not-found.com) 是一个有用的资源，你可以用它来搜索任何命令，以了解如何跨不同的包管理器和操作系统发行版安装它。

另一个有用的工具是 [`tldr`](https://tldr.sh/)，它提供简化版、以示例为中心的 man 页。无需阅读冗长的文档，你可以快速查看常见用法模式：

```console
$ tldr fd
  An alternative to find.
  Aims to be faster and easier to use than find.

  Recursively find files matching a pattern in the current directory:
      fd "pattern"

  Find files that begin with "foo":
      fd "^foo"

  Find files with a specific extension:
      fd --extension txt
```

有时你不需要一个新程序，而只需要为带有特定标志的已有命令设置一个快捷方式。这就是别名（aliases）的用武之地。

我们也可以使用 `alias` shell 内建命令创建自己的命令别名。shell 别名是另一条命令的简短形式，shell 会在求值表达式之前自动替换它。例如，bash 中的别名具有以下结构：

```bash
alias alias_name="command_to_alias arg1 arg2"
```

> 注意等号 `=` 周围没有空格，因为 [`alias`](https://www.man7.org/linux/man-pages/man1/alias.1p.html) 是一个 shell 命令，它只接受一个参数。

别名有许多便捷的特性：

```bash
# 为常见标志创建速写
alias ll="ls -lh"

# 为常用命令节省大量输入
alias gs="git status"
alias gc="git commit"

# 防止打错字
alias sl=ls

# 覆盖已有命令以获得更好的默认值
alias mv="mv -i"           # -i 在覆盖前提示
alias mkdir="mkdir -p"     # -p 按需创建父目录
alias df="df -h"           # -h 以人类可读格式输出

# 别名可以组合
alias la="ls -A"
alias lla="la -l"

# 要忽略一个别名，在其前面加上 \
\ls
# 或者用 unalias 完全禁用一个别名
unalias la

# 要查看别名定义，直接调用它即可
alias ll
# 将输出 ll='ls -lh'
```

别名有其局限性：它们不能在命令中间接收参数。对于更复杂的行为，你应该使用 shell 函数。

大多数 shell 都支持 `Ctrl-R` 进行反向历史搜索。输入 `Ctrl-R` 并开始输入，即可搜索之前的命令。之前我们引入了 `fzf` 作为模糊查找器；配置好 fzf 的 shell 集成后，`Ctrl-R` 会变成对整个历史记录的交互式模糊搜索，远强于默认的搜索方式。

应该如何组织你的点文件？它们应该在一个单独的文件夹中、纳入版本控制，并通过一个脚本来**符号链接**到正确位置。这有以下好处：

- **易于安装**：如果你登录一台新机器，应用你的自定义设置只需一分钟。
- **可移植性**：你的工具在所有地方都能以相同的方式工作。
- **同步**：你可以在任何地方更新点文件并保持它们同步。
- **变更追踪**：你可能会在整个编程生涯中维护点文件，而版本历史对于长期项目来说非常有价值。

你的点文件中应该放什么？
你可以通过阅读在线文档或[man 页](https://en.wikipedia.org/wiki/Man_page)来了解你的工具设置。另一种很好的方法是在互联网上搜索关于特定程序的博文——作者会告诉他们你偏好的定制方式。还有另一种学习定制的方法是浏览其他人的点文件：你可以在 GitHub 上找到大量[点文件仓库](https://github.com/search?o=desc&q=dotfiles&s=stars&type=Repositories)——[最流行的一个在这里](https://github.com/mathiasbynens/dotfiles)（不过我们不建议你盲目复制配置）。[这里](https://dotfiles.github.io/)是另一个关于该主题的优质资源。

所有课程讲师的点文件都在 GitHub 上公开可用：[Anish](https://github.com/anishathalye/dotfiles)、[Jon](https://github.com/jonhoo/configs)、[Jose](https://github.com/jjgo/dotfiles)。

**框架和插件**也可以改进你的 shell。一些流行的通用框架是 [prezto](https://github.com/sorin-ionescu/prezto) 或 [oh-my-zsh](https://ohmyz.sh/)，还有一些专注于特定功能的小型插件：

- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting) — 在你输入时自动为有效/无效命令着色
- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) — 在你输入时从历史记录中建议命令
- [zsh-completions](https://github.com/zsh-users/zsh-completions) — 额外的补全定义
- [zsh-history-substring-search](https://github.com/zsh-users/zsh-history-substring-search) — 类似 fish 的历史搜索
- [powerlevel10k](https://github.com/romkatv/powerlevel10k) — 快速且可定制的提示主题

像 [fish](https://fishshell.com/) 这样的 shell 默认包含了很多这些功能。

> 你不需要 oh-my-zsh 这样庞大的框架来获得这些功能。单独安装插件通常更快，也让你拥有更多控制权。大型框架可能会显著减慢 shell 启动速度，所以请考虑只安装你真正使用的部分。


# Shell 中的 AI

有多种方式可以在 shell 中整合 AI 工具。以下是一些在不同集成层级的示例：

**命令生成**：像 [`simonw/llm`](https://github.com/simonw/llm) 这样的工具可以帮助从自然语言描述中生成 shell 命令：

```console
$ llm cmd "find all python files modified in the last week"
find . -name "*.py" -mtime -7
```

**管道集成**：LLM 可以集成到 shell 管道中，用于处理和转换数据。当你需要从不一致的格式中提取信息，而使用正则表达式会很痛苦时，它们特别有用：

```console
$ cat users.txt
Contact: john.doe@example.com
User 'alice_smith' logged in at 3pm
Posted by: @bob_jones on Twitter
Author: Jane Doe (jdoe)
Message from mike_wilson yesterday
Submitted by user: sarah.connor
$ INSTRUCTIONS="Extract just the username from each line, one per line, nothing else"
$ llm "$INSTRUCTIONS" < users.txt
john.doe
alice_smith
bob_jones
jdoe
mike_wilson
sarah.connor
```

注意我们使用了 `"$INSTRUCTIONS"`（加引号），因为变量包含空格，以及 `< users.txt` 将文件内容重定向到 stdin。

**AI shell**：像 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 这样的工具充当一个元 shell（meta-shell），接受英文命令并将其转化为 shell 操作、文件编辑以及更复杂的多步骤任务。

# 终端模拟器

与定制 shell 一样，花些时间来选择你的**终端模拟器**（terminal emulator）及其设置也值得。终端模拟器是一种提供文本界面、供你的 shell 运行的 GUI 程序。市面上有许多终端模拟器。

由于你可能在终端中花费数百甚至数千小时，值得研究一下它的设置。你可能想要修改的终端方面包括：

- 字体选择
- 配色方案
- 快捷键
- 标签/面板支持
- 回滚配置
- 性能（一些较新的终端如 [Alacritty](https://github.com/alacritty/alacritty) 或 [Ghostty](https://ghostty.org/) 提供 GPU 加速）。



# 练习

## 参数与通配匹配

1. 你可能会看到类似 `cmd --flag -- --notaflag` 的命令。`--` 是一个特殊参数，告诉程序停止解析标志。`--` 之后的所有内容都被视为位置参数。这在什么情况下可能有用？尝试运行 `touch -- -myfile`，然后尝试在不使用 `--` 的情况下删除它。

1. 阅读 [`man ls`](https://www.man7.org/linux/man-pages/man1/ls.1.html)，并写出一条 `ls` 命令，以如下方式列出文件：
    - 包含所有文件，包括隐藏文件
    - 文件大小以人类可读格式列出（如 454M，而不是 454279954）
    - 文件按最近修改时间排序
    - 输出有颜色

    示例输出如下：

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

1. 进程替换 `<(command)` 允许你将命令的输出当作文件来使用。使用 `diff` 配合进程替换来比较 `printenv` 和 `export` 的输出。为什么它们不同？（提示：尝试 `diff <(printenv | sort) <(export | sort)`）。

## 环境变量

1. 编写 bash 函数 `marco` 和 `polo`，实现如下行为：当你执行 `marco` 时，应将当前工作目录以某种方式保存下来；然后当你执行 `polo` 时，无论你在什么目录下，`polo` 都应该将你 `cd` 回到你执行 `marco` 时的目录。为方便调试，你可以将代码写入 `marco.sh` 文件，并通过执行 `source marco.sh` 重新加载定义到 shell 中。

{% comment %}
marco() {
    export MARCO=$(pwd)
}

polo() {
    cd "$MARCO"
}
{% endcomment %}

## 返回码

1. 假设你有一个很少失败的命令。为了调试它，你需要捕获其输出，但等到一次失败可能需要很长时间。编写一个 bash 脚本，运行以下脚本直到它失败，并将标准输出和标准错误输出保存到文件中，最后打印所有内容。额外加分：你还可以报告脚本失败了多少次。

    ```bash
    #!/usr/bin/env bash

    n=$(( RANDOM % 100 ))

    if [[ $n -eq 42 ]]; then
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

echo "found error after $count runs"
cat out.txt
{% endcomment %}

## 信号与任务控制

1. 在终端中启动一个 `sleep 10000` 任务，用 `Ctrl-Z` 将其放入后台，并用 `bg` 恢复其执行。现在使用 [`pgrep`](https://www.man7.org/linux/man-pages/man1/pgrep.1.html) 来找到它的 pid，并用 [`pkill`](https://man7.org/linux/man-pages/man1/pgrep.1.html) 来终止它，全程不要输入 pid。（提示：使用 `-lf` 标志）。

1. 假设你在另一个进程完成之前不想启动一个进程。你会怎么做？在此练习中，我们的限制进程始终是 `sleep 60 &`。一种实现方式是使用 [`wait`](https://www.man7.org/linux/man-pages/man1/wait.1p.html) 命令。尝试启动 `sleep` 命令，然后让 `ls` 等待后台进程完成。

    然而，如果我们从不同的 bash 会话开始，这种策略会失败，因为 `wait` 仅对子进程有效。我们在讲义中没有讨论的一个特性是 `kill` 命令的成功时返回码为零、失败时为非零。`kill -0` 不会发送信号，但如果进程不存在则会给出非零退出状态。编写一个名为 `pidwait` 的 bash 函数，它接受一个 pid 并等待给定进程完成。你应该使用 `sleep` 来避免不必要地浪费 CPU。

## 文件与权限

1. （进阶）编写一条命令或脚本来递归地查找一个目录中最近修改的文件。更一般地，你能否按修改时间列出所有文件？

## 终端复用器

1. 跟随此 `tmux` [教程](https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/)学习，然后按照[这些步骤](https://www.hamvocke.com/blog/a-guide-to-customizing-your-tmux-conf/)了解一些基本定制。

## 别名与点文件

1. 创建一个别名 `dc`，当你打错字时让它解析为 `cd`。

1. 运行 `history | awk '{$1="";print substr($0,2)}' | sort | uniq -c | sort -n | tail -n 10` 来获取你使用最多的 10 条命令，并考虑为它们编写更短的别名。注意：这适用于 Bash；如果你使用 ZSH，请用 `history 1` 替代 `history`。

1. 为你的点文件创建一个文件夹并建立版本控制。

1. 为至少一个程序添加配置，例如你的 shell，并包含一些定制（从简单开始，比如通过设置 `$PS1` 来定制你的 shell 提示符）。

1. 设置一种在新机器上快速（无需手动操作）安装你点文件的方法。可以是一个简单的调用 `ln -s` 的 shell 脚本，也可以使用[专用工具](https://dotfiles.github.io/utilities/)。

1. 在一个全新的虚拟机上测试你的安装脚本。

1. 将你所有当前的工具配置迁移到你的点文件仓库。

1. 在 GitHub 上公开你的点文件。

## 远程机器（SSH）

为这些练习安装一个 Linux 虚拟机（或使用已有虚拟机）。如果你不熟悉虚拟机，请查看[这篇](https://hibbard.eu/install-ubuntu-virtual-box/)教程来安装一个。

1. 进入 `~/.ssh/` 并检查是否有 SSH 密钥对。如果没有，使用 `ssh-keygen -a 100 -t ed25519` 生成。建议使用密码并配合 `ssh-agent`，更多信息[见此](https://www.ssh.com/ssh/agent)。

1. 编辑 `.ssh/config`，添加如下条目：

    ```bash
    Host vm
        User username_goes_here
        HostName ip_goes_here
        IdentityFile ~/.ssh/id_ed25519
        LocalForward 9999 localhost:8888
    ```

1. 使用 `ssh-copy-id vm` 将你的 SSH 密钥复制到服务器。

1. 在你的 VM 中通过执行 `python -m http.server 8888` 启动一个 Web 服务器。在你的机器上通过访问 `http://localhost:9999` 来访问 VM 上的 Web 服务器。

1. 通过执行 `sudo vim /etc/ssh/sshd_config` 编辑你的 SSH 服务器配置，通过编辑 `PasswordAuthentication` 的值来禁用密码认证。通过编辑 `PermitRootLogin` 的值来禁用 root 登录。使用 `sudo service sshd restart` 重启 `ssh` 服务。再次尝试 ssh 连接。

1. （挑战）在 VM 中安装 [`mosh`](https://mosh.org/) 并建立连接。然后断开服务器/VM 的网络适配器。mosh 能否从此恢复？

1. （挑战）了解 `ssh` 中 `-N` 和 `-f` 标志的用途，并找出一个实现后台端口转发的命令。