---
layout: lecture
title: "调试与性能分析"
description: >
  学习如何使用日志、调试器和静态分析来调试程序，以及如何对代码进行性能分析。
thumbnail: /static/assets/thumbnails/2020/lec7.png
date: 2020-01-23
ready: true
video:
  aspect: 56.25
  id: l812pUnKxME
---

编程领域有一条黄金法则：代码不会按照你的期望运行，而是按照你的指令运行。弥合这之间差距的任务有时并不简单。
在本讲中，我们将介绍处理有 bug 和消耗大量资源的代码的实用技巧：调试（Debugging）和性能分析（Profiling）。

# 调试

## 打印调试与日志

"最有效的调试工具仍然是审慎的思考，搭配精心布置的打印语句。" —— Brian Kernighan，_Unix for Beginners_。

调试程序的一个方法是：在你发现问题的位置附近加入打印语句，然后反复迭代，直到你收集到足够的信息来理解是什么导致了问题。

另一种方法是使用日志（Logging）而非随手写的打印语句。日志比起普通的打印语句有以下几个优点：

- 你可以将日志输出到文件、套接字甚至远程服务器，而不仅仅是标准输出。
- 日志支持严重级别（如 INFO、DEBUG、WARN、ERROR 等），允许你据此过滤输出。
- 对于新出现的问题，你的日志很有可能会包含足够的信息来识别问题所在。

[这里](/static/files/logger.py) 是一个日志消息记录的示例代码：

```bash
$ python logger.py
# Raw output as with just prints
$ python logger.py log
# Log formatted output
$ python logger.py log ERROR
# Print only ERROR levels and above
$ python logger.py color
# Color formatted output
```

我个人最喜欢的一条小技巧是：给日志加上颜色。到目前为止，你应该已经意识到终端使用颜色来让信息更易读了。但它是怎么做到的呢？

`ls` 或 `grep` 这类程序使用的是 [ANSI 转义序列](https://en.wikipedia.org/wiki/ANSI_escape_code)，即一组特殊的字符序列，用来指示你的 shell 改变输出的颜色。例如，执行 `echo -e "\e[38;2;255;0;0mThis is red\e[0m"` 会在你的终端上以红色打印 `This is red`，前提是终端支持 [真彩色](https://github.com/termstandard/colors#truecolor-support-in-output-devices)。如果你的终端不支持真彩色（例如 macOS 的 Terminal.app），你可以使用支持面更广的 16 色转义码，例如 `echo -e "\e[31;1mThis is red\e[0m"`。

以下脚本会将许多 RGB 颜色打印到终端中（同样，前提是终端支持真彩色）。

```bash
#!/usr/bin/env bash
for R in $(seq 0 20 255); do
    for G in $(seq 0 20 255); do
        for B in $(seq 0 20 255); do
            printf "\e[38;2;${R};${G};${B}m█\e[0m";
        done
    done
done
```

## 第三方日志

随着你构建的软件系统越来越大，你很可能遇到以独立程序运行的依赖项。Web 服务器、数据库或消息中间件就是这类依赖的典型例子。
与这些系统交互时，经常需要阅读它们的日志，因为客户端的错误信息往往不够充分。

幸运的是，大多数程序会在你系统的某个位置写入它们自己的日志。在 UNIX 系统中，程序通常会将日志写入 `/var/log`。
例如，[NGINX](https://www.nginx.com/) Web 服务器将其日志放在 `/var/log/nginx` 下。
更近一些，越来越多的系统开始使用**系统日志**，几乎所有日志消息都会写入其中。
大多数（但非全部）Linux 系统使用 `systemd`，这是一个系统守护进程，控制着系统中的许多事务（如哪些服务已启用并在运行）。
`systemd` 将日志以专用格式存放在 `/var/log/journal`，你可以使用 [`journalctl`](https://www.man7.org/linux/man-pages/man1/journalctl.1.html) 命令来查看这些消息。
同样，macOS 上仍然有 `/var/log/system.log`，但越来越多的工具使用系统日志，可以通过 [`log show`](https://www.manpagez.com/man/1/log/) 查看。
在大多数 UNIX 系统上，你也可以使用 [`dmesg`](https://www.man7.org/linux/man-pages/man1/dmesg.1.html) 命令来访问内核日志。

如果你想在系统日志中记录日志，可以使用 [`logger`](https://www.man7.org/linux/man-pages/man1/logger.1.html) shell 程序。
下面是一个使用 `logger` 并检查条目是否成功写入系统日志的示例。
此外，大多数编程语言都提供了将日志写入系统日志的绑定（bindings）。

```bash
logger "Hello Logs"
# On macOS
log show --last 1m | grep Hello
# On Linux
journalctl --since "1m ago" | grep Hello
```

正如我们在数据清洗（Data Wrangling）讲座中所看到的，日志可能会非常冗长，需要一定程度的处理和过滤才能获得你需要的信息。
如果你发现自己需要大量过滤 `journalctl` 和 `log show` 的输出，可以考虑使用它们的参数，以在输出的第一遍处理中进行过滤。
还有一些工具如 [`lnav`](https://lnav.org/) 提供了改进的日志文件展示和导航方式。

## 调试器

当打印调试法不够用时，你就应该使用调试器（Debugger）。
调试器是允许你与程序执行过程交互的程序，支持以下功能：

- 当程序执行到某一行时暂停程序执行。
- 逐行逐步执行程序。
- 程序崩溃后检查变量的值。
- 在给定条件满足时暂停执行。
- 以及更多高级功能

许多编程语言都自带某种形式的调试器。
在 Python 中，这就是 Python 调试器 [`pdb`](https://docs.python.org/3/library/pdb.html)。

以下是对 `pdb` 支持的一些命令的简要说明：

- **l**(ist) — 显示当前行周围 11 行代码，或继续上一次显示。
- **s**(tep) — 执行当前行，在第一处可暂停的位置停下。
- **n**(ext) — 继续执行，直到到达当前函数中的下一行或函数返回。
- **b**(reak) — 设置断点（根据提供的参数而定）。
- **p**(rint) — 在当前上下文中求值表达式并打印其值。还有 **pp** 可以使用 [`pprint`](https://docs.python.org/3/library/pprint.html) 来美化显示。
- **r**(eturn) — 继续执行直到当前函数返回。
- **q**(uit) — 退出调试器。

下面我们通过一个例子来演示如何使用 `pdb` 修复以下有 bug 的 Python 代码。（参见讲座视频。）

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n):
            if arr[j] > arr[j+1]:
                arr[j] = arr[j+1]
                arr[j+1] = arr[j]
    return arr

print(bubble_sort([4, 2, 1, 8, 7, 6]))
```

需要注意的是，由于 Python 是解释型语言，我们可以使用 `pdb` 的交互式 shell 来执行命令和指令。
[`ipdb`](https://pypi.org/project/ipdb/) 是一个改进版的 `pdb`，它使用 [`IPython`](https://ipython.org) REPL，提供 tab 补全、语法高亮、更详细的回溯信息和更强大的内省能力，同时保留了与 `pdb` 模块相同的接口。

对于更底层的编程，你可能会想要了解 [`gdb`](https://www.gnu.org/software/gdb/)（以及其提升体验的改进版本 [`pwndbg`](https://github.com/pwndbg/pwndbg)）和 [`lldb`](https://lldb.llvm.org/)。
它们专为 C 类语言的调试而优化，但同样可以用来探测几乎任何进程并获取其当前机器状态：寄存器、栈、程序计数器等。

## 专用工具

即使你尝试调试的是一个黑盒二进制文件，也有能帮助你的工具。
当程序需要执行只有内核才能完成的操作时，它们会使用 [系统调用（System Calls）](https://en.wikipedia.org/wiki/System_call)。
有一些命令可以让你追踪程序发出的系统调用。在 Linux 上有 [`strace`](https://www.man7.org/linux/man-pages/man1/strace.1.html)，macOS 和 BSD 上有 [`dtrace`](https://dtrace.org/about/)。`dtrace` 使用起来可能有些棘手，因为它使用自己的 `D` 语言，但有一个名为 [`dtruss`](https://www.manpagez.com/man/1/dtruss/) 的封装器提供了与 `strace` 更相似的接口（更多详情见[这里](https://8thlight.com/blog/colin-jones/2015/11/06/dtrace-even-better-than-strace-for-osx.html)）。

下面是一些使用 `strace` 或 `dtruss` 来追踪 `ls` 执行时 [`stat`](https://www.man7.org/linux/man-pages/man2/stat.2.html) 系统调用的例子。如果想要更深入地了解 `strace`，[这篇文章](https://blogs.oracle.com/linux/strace-the-sysadmins-microscope-v2)和[这本小册子](https://jvns.ca/strace-zine-unfolded.pdf)是很好的阅读材料。

```bash
# On Linux
sudo strace -e lstat ls -l > /dev/null
# On macOS
sudo dtruss -t lstat64_extended ls -l > /dev/null
```

在某些情况下，你可能需要查看网络数据包来确定程序中的问题。
[`tcpdump`](https://www.man7.org/linux/man-pages/man1/tcpdump.1.html) 和 [Wireshark](https://www.wireshark.org/) 这类工具是网络包分析器，可以让您读取网络包的内容并根据不同条件进行过滤。

对于 Web 开发，Chrome / Firefox 的开发者工具非常实用。它们提供了大量工具，包括：
- 源代码 — 检查任何网站的 HTML / CSS / JS 源代码。
- 实时 HTML / CSS / JS 修改 — 更改网站内容、样式和行为以进行测试（你可以亲自验证网站截图并不能作为有效证明）。
- JavaScript shell — 在 JS REPL 中执行命令。
- 网络 — 分析请求时间线。
- 存储 — 查看 Cookie 和本地应用存储。

## 静态分析

对于某些问题，你不需要运行任何代码。
例如，只需仔细观察一段代码，你就可能发现循环变量覆盖了一个已存在的变量或函数名；或者程序在定义之前读取了一个变量。
这就是 [静态分析（Static Analysis）](https://en.wikipedia.org/wiki/Static_program_analysis) 工具的用武之地。
静态分析程序以源代码作为输入，使用编码规则对其进行分析，从而推理其正确性。

在以下 Python 代码片段中有几个错误。
首先，我们的循环变量 `foo` 覆盖了前面定义的函数 `foo`。另外，最后一行我们写的是 `baz` 而不是 `bar`，所以程序在完成 `sleep` 调用后会崩溃（这个调用会持续一分钟）。

```python
import time

def foo():
    return 42

for foo in range(5):
    print(foo)
bar = 1
bar *= 0.2
time.sleep(60)
print(baz)
```

静态分析工具可以发现这类问题。当我们在代码上运行 [`pyflakes`](https://pypi.org/project/pyflakes) 时，会看到与两个 bug 相关的错误。[`mypy`](https://mypy-lang.org/) 是另一个可以检测类型检查问题的工具。在这里，`mypy` 会警告我们 `bar` 初始是 `int` 类型，然后被隐式转换为 `float`。
同样，请注意所有这些问题都是在没有运行代码的情况下被发现的。

```bash
$ pyflakes foobar.py
foobar.py:6: redefinition of unused 'foo' from line 3
foobar.py:11: undefined name 'baz'

$ mypy foobar.py
foobar.py:6: error: Incompatible types in assignment (expression has type "int", variable has type "Callable[[], Any]")
foobar.py:9: error: Incompatible types in assignment (expression has type "float", variable has type "int")
foobar.py:11: error: Name 'baz' is not defined
Found 3 errors in 1 file (checked 1 source file)
```

在 Shell 工具讲座中，我们介绍过 [`shellcheck`](https://www.shellcheck.net/)，这是一个用于 Shell 脚本的类似工具。

大多数编辑器和 IDE 支持在编辑器中显示这些工具的输出，高亮警告和错误的位置。
这通常被称为 **代码检查（Code Linting）**，它也可以用来显示其他类型的问题，如风格违规或不安全的代码结构。

在 vim 中，插件 [`ale`](https://vimawesome.com/plugin/ale) 或 [`syntastic`](https://vimawesome.com/plugin/syntastic) 可以实现这一点。
对于 Python，[`pylint`](https://github.com/PyCQA/pylint) 和 [`pep8`](https://pypi.org/project/pep8/) 是风格检查器的例子，[`bandit`](https://pypi.org/project/bandit/) 是一个用于发现常见安全问题的工具。
对于其他语言，人们整理了全面的静态分析工具列表，如 [Awesome Static Analysis](https://github.com/mre/awesome-static-analysis)（你可能想看看 _Writing_ 部分）以及 linters 列表 [Awesome Linters](https://github.com/caramelomartins/awesome-linters)。

与风格检查互补的一个工具是代码格式化器，如 Python 的 [`black`](https://github.com/psf/black)、Go 的 `gofmt`、Rust 的 `rustfmt` 或 JavaScript、HTML、CSS 的 [`prettier`](https://prettier.io/)。
这些工具自动格式化你的代码，使其与给定编程语言的常见风格模式保持一致。
尽管你可能不愿放弃对代码风格的掌控，但标准化代码格式将帮助其他人阅读你的代码，也会让你更擅长阅读其他人的（风格标准化的）代码。

# 性能分析

即使你的代码在功能上行为符合预期，如果它在此过程中消耗了所有 CPU 或内存，那也远远不够。
算法课程通常会教授大 _O_ 记法，但很少教如何在你的程序中找出热点（hot spots）。
由于[过早优化是万恶之源](https://wiki.c2.com/?PrematureOptimization)，你应该了解性能分析工具（profilers）和监控工具。它们会帮助你理解程序中哪些部分消耗了最多的时间和 / 或资源，从而让你专注于优化这些部分。

## 计时

与调试情况类似，在许多场景中，只需打印代码在两个时间点之间花费的时间就足够了。
下面是一个使用 [`time`](https://docs.python.org/3/library/time.html) 模块的 Python 示例。

```python
import time, random
n = random.randint(1, 10) * 100

# Get current time
start = time.time()

# Do some work
print("Sleeping for {} ms".format(n))
time.sleep(n/1000)

# Compute time between start and now
print(time.time() - start)

# Output
# Sleeping for 500 ms
# 0.5713930130004883
```

然而，挂钟时间（wall clock time）可能会产生误导，因为你的计算机可能同时在运行其他进程或等待事件发生。工具通常会将时间区分为 _Real_（真实）、_User_（用户）和 _Sys_（系统）。一般来说，_User_ + _Sys_ 告诉你进程实际在 CPU 上花费了多少时间（更详细的解释见[这里](https://stackoverflow.com/questions/556405/what-do-real-user-and-sys-mean-in-the-output-of-time1)）。

- _Real_ — 从程序开始到结束的挂钟时间，包括其他进程所占的时间以及被阻塞的时间（例如等待 I/O 或网络）。
- _User_ — 在 CPU 上运行用户代码所花费的时间。
- _Sys_ — 在 CPU 上运行内核代码所花费的时间。

例如，尝试运行一个发出 HTTP 请求的命令，并用 [`time`](https://www.man7.org/linux/man-pages/man1/time.1.html) 作为前缀。在慢速连接下，你可能会得到如下输出。这里请求花了超过 2 秒才完成，但进程只使用了 15ms 的 CPU 用户时间和 12ms 的内核 CPU 时间。

```bash
$ time curl https://missing.csail.mit.edu &> /dev/null
real    0m2.561s
user    0m0.015s
sys     0m0.012s
```

## 性能分析器

### CPU

大多数时候，当人们提到"性能分析器"时，他们实际上指的是"CPU 性能分析器"，这是最常见的。
CPU 性能分析器主要有两种类型：_追踪型（Tracing）_ 和 _采样型（Sampling）_。
追踪型性能分析器会记录程序执行的每一个函数调用，而采样型性能分析器会定期（通常每毫秒）探测程序并记录程序的栈。
它们使用这些记录来呈现程序在哪些方面花费最多时间的聚合统计信息。
如果你想了解更多细节，[这篇文章](https://jvns.ca/blog/2017/12/17/how-do-ruby---python-profilers-work-) 是一个很好的入门文章。

大多数编程语言都提供了某种命令行性能分析器，你可以用它来分析代码。
它们通常可以与功能完善的 IDE 集成，但本讲座我们将专注于命令行工具本身。

在 Python 中，我们可以使用 `cProfile` 模块来分析每个函数调用的耗时。下面是一个简单的示例，用 Python 实现了一个粗糙的 grep：

```python
#!/usr/bin/env python

import sys, re

def grep(pattern, file):
    with open(file, 'r') as f:
        print(file)
        for i, line in enumerate(f.readlines()):
            pattern = re.compile(pattern)
            match = pattern.search(line)
            if match is not None:
                print("{}: {}".format(i, line), end="")

if __name__ == '__main__':
    times = int(sys.argv[1])
    pattern = sys.argv[2]
    for i in range(times):
        for file in sys.argv[3:]:
            grep(pattern, file)
```

我们可以使用以下命令来分析这段代码。分析输出可以看到，IO 花费了大部分时间，而编译正则表达式也花了不少时间。由于正则表达式只需要编译一次，我们可以将其从 for 循环中提取出来。

```
$ python -m cProfile -s tottime grep.py 1000 '^(import|\s*def)[^,]*$' *.py

[omitted program output]

 ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     8000    0.266    0.000    0.292    0.000 {built-in method io.open}
     8000    0.153    0.000    0.894    0.000 grep.py:5(grep)
    17000    0.101    0.000    0.101    0.000 {built-in method builtins.print}
     8000    0.100    0.000    0.129    0.000 {method 'readlines' of '_io._IOBase' objects}
    93000    0.097    0.000    0.111    0.000 re.py:286(_compile)
    93000    0.069    0.000    0.069    0.000 {method 'search' of '_sre.SRE_Pattern' objects}
    93000    0.030    0.000    0.141    0.000 re.py:231(compile)
    17000    0.019    0.000    0.029    0.000 codecs.py:318(decode)
        1    0.017    0.017    0.911    0.911 grep.py:3(<module>)

[omitted lines]
```

Python `cProfile` 性能分析器的一个注意事项是（许多分析器也是如此）：它显示的是每个函数调用的耗时。这在很多情况下会让人感到不直观，尤其是当你在代码中使用第三方库时，因为内部函数调用也会被计入。

一种更直观的方式是按行显示耗时，这正是 _行分析器（Line Profilers）_ 所做的。

例如，以下 Python 代码对课程网站发起请求，并解析响应以获取页面上的所有 URL：

```python
#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup

# This is a decorator that tells line_profiler
# that we want to analyze this function
@profile
def get_urls():
    response = requests.get('https://missing.csail.mit.edu')
    s = BeautifulSoup(response.content, 'lxml')
    urls = []
    for url in s.find_all('a'):
        urls.append(url['href'])

if __name__ == '__main__':
    get_urls()
```

如果使用了 Python 的 `cProfile` 性能分析器，我们会得到超过 2500 行的输出，即使排序也难以理解时间花在哪里了。使用 [`line_profiler`](https://github.com/pyutils/line_profiler) 快速运行一下，就会显示每行所花费的时间：

```bash
$ kernprof -l -v a.py
Wrote profile results to urls.py.lprof
Timer unit: 1e-06 s

Total time: 0.636188 s
File: a.py
Function: get_urls at line 5

Line #  Hits         Time  Per Hit   % Time  Line Contents
==============================================================
 5                                           @profile
 6                                           def get_urls():
 7         1     613909.0 613909.0     96.5      response = requests.get('https://missing.csail.mit.edu')
 8         1      21559.0  21559.0      3.4      s = BeautifulSoup(response.content, 'lxml')
 9         1          2.0      2.0      0.0      urls = []
10        25        685.0     27.4      0.1      for url in s.find_all('a'):
11        24         33.0      1.4      0.0          urls.append(url['href'])
```

### 内存

在 C 或 C++ 这类语言中，内存泄漏可能导致程序永远不会释放不再需要的内存。
为了帮助进行内存调试，你可以使用 [Valgrind](https://valgrind.org/) 等工具来帮助你识别内存泄漏。

在 Python 这类垃圾回收语言中，使用内存分析器仍然很有用，因为只要你持有对内存中对象的引用，它们就不会被垃圾回收。
下面是一个示例程序及其运行 [memory-profiler](https://pypi.org/project/memory-profiler/) 时的输出（注意装饰器的用法与 `line-profiler` 类似）。

```python
@profile
def my_func():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    return a

if __name__ == '__main__':
    my_func()
```

```bash
$ python -m memory_profiler example.py
Line #    Mem usage  Increment   Line Contents
==============================================
     3                           @profile
     4      5.97 MB    0.00 MB   def my_func():
     5     13.61 MB    7.64 MB       a = [1] * (10 ** 6)
     6    166.20 MB  152.59 MB       b = [2] * (2 * 10 ** 7)
     7     13.61 MB -152.59 MB       del b
     8     13.61 MB    0.00 MB       return a
```

### 事件分析

正如对于调试的 `strace` 一样，当你进行性能分析时，你可能希望忽略所运行代码的具体细节，将其视为一个黑盒。
[`perf`](https://www.man7.org/linux/man-pages/man1/perf.1.html) 命令抽象了 CPU 差异，不报告时间或内存，而是报告与你的程序相关的系统事件。
例如，`perf` 可以轻松报告糟糕的缓存局部性、大量的页面故障或活锁（livelocks）。以下是该命令的概览：

- `perf list` — 列出 perf 可以追踪的事件
- `perf stat COMMAND ARG1 ARG2` — 获取与进程或命令相关的各种事件的计数
- `perf record COMMAND ARG1 ARG2` — 记录命令的运行并将统计数据保存到名为 `perf.data` 的文件中
- `perf report` — 格式化并打印 `perf.data` 中收集的数据

### 可视化

真实程序的 profiler 输出包含大量信息，因为软件项目本身就具有内在复杂性。
人类是视觉动物，在读取大量数字并从其中提取意义方面相当糟糕。
因此，有很多工具可以以更易于解析的方式展示性能分析器的输出。

一种常见的展示采样型性能分析器 CPU 性能分析信息的方法是使用 [火焰图（Flame Graph）](https://www.brendangregg.com/flamegraphs.html)，它将在 Y 轴上显示函数调用的层次结构，在 X 轴上按比例显示耗时。它们也是交互式的，让你能够缩放到程序的特定部分并查看其调用栈（试着点击下面的图片）。

[![FlameGraph](https://www.brendangregg.com/FlameGraphs/cpu-bash-flamegraph.svg)](https://www.brendangregg.com/FlameGraphs/cpu-bash-flamegraph.svg)

调用图（Call Graph）或控制流图通过以函数作为节点、函数之间的调用作为有向边来显示程序内子例程之间的关系。当与性能分析信息（如调用次数和耗时）结合时，调用图对于解释程序的流程非常有用。
在 Python 中，你可以使用 [`pycallgraph`](https://pycallgraph.readthedocs.io/) 库来生成它们。

![Call Graph](https://upload.wikimedia.org/wikipedia/commons/2/2f/A_Call_Graph_generated_by_pycallgraph.png)

## 资源监控

有时，分析程序性能的第一步是了解其实际资源消耗情况。
当程序受资源限制时（例如没有足够的内存或处于慢速网络连接），往往会运行得很慢。
有许多命令行工具可以探测和显示不同的系统资源，如 CPU 使用率、内存使用率、网络、磁盘使用率等。

- **通用监控** — 最受欢迎的可能是 [`htop`](https://htop.dev/)，它是 [`top`](https://www.man7.org/linux/man-pages/man1/top.1.html) 的改进版。
`htop` 展示系统中当前运行进程的各种统计信息。`htop` 有许多选项和快捷键，一些有用的包括：`<F6>` 对进程排序，`t` 显示树形层次结构，`h` 切换线程显示。
类似实现的还有 [`glances`](https://nicolargo.github.io/glances/)，拥有出色的 UI。若要获取所有进程的聚合指标，[`dool`](https://github.com/scottchiefbaker/dool) 是另一个好用的工具，它计算 I/O、网络、CPU 利用率、上下文切换等多个子系统的实时资源指标。
- **I/O 操作** — [`iotop`](https://www.man7.org/linux/man-pages/man8/iotop.8.html) 显示实时的 I/O 使用信息，便于检查某个进程是否在执行繁重的 I/O 磁盘操作。
- **磁盘使用** — [`df`](https://www.man7.org/linux/man-pages/man1/df.1.html) 显示每个分区的指标，[`du`](https://man7.org/linux/man-pages/man1/du.1.html) 显示当前目录中每个文件的**磁**盘**使**用量。在这些工具中，`-h` 参数让程序以**人**类可读的格式打印。
`du` 的一个交互式版本是 [`ncdu`](https://dev.yorhel.nl/ncdu)，它允许你导航文件夹并在导航过程中删除文件和文件夹。
- **内存使用** — [`free`](https://www.man7.org/linux/man-pages/man1/free.1.html) 显示系统中总的空闲和已用内存量。内存也会在 `htop` 等工具中显示。
- **打开的文件** — [`lsof`](https://www.man7.org/linux/man-pages/man8/lsof.8.html) 列出进程所打开文件的文件信息。它可以非常方便地用于检查哪个进程打开了某个特定文件。
- **网络连接与配置** — [`ss`](https://www.man7.org/linux/man-pages/man8/ss.8.html) 允许你监控传入和传出网络包的统计信息以及接口统计信息。`ss` 的一个常见用法是找出机器上哪个进程正在使用给定端口。若要显示路由、网络设备和接口，可以使用 [`ip`](https://man7.org/linux/man-pages/man8/ip.8.html)。请注意，`netstat` 和 `ifconfig` 已被分别弃用，建议使用上述工具替代。
- **网络使用** — [`nethogs`](https://github.com/raboof/nethogs) 和 [`iftop`](https://pdw.ex-parrot.com/iftop/) 是监控网络使用情况的优秀交互式 CLI 工具。

如果你想测试这些工具，也可以使用 [`stress`](https://linux.die.net/man/1/stress) 命令对机器施加人工负载。

### 专用工具

有时候，黑盒基准测试就足以判断使用什么软件。
[`hyperfine`](https://github.com/sharkdp/hyperfine) 等工具可以让你快速对命令行程序进行基准测试。
例如，在 shell 工具与脚本讲座中，我们推荐了 `fd` 而非 `find`。我们可以用 `hyperfine` 来比较它们在常用任务中的表现。
下面的例子中，`fd` 在我的机器上比 `find` 快 20 倍。

```bash
$ hyperfine --warmup 3 'fd -e jpg' 'find . -iname "*.jpg"'
Benchmark #1: fd -e jpg
  Time (mean ± σ):      51.4 ms ±   2.9 ms    [User: 121.0 ms, System: 160.5 ms]
  Range (min … max):    44.2 ms …  60.1 ms    56 runs

Benchmark #2: find . -iname "*.jpg"
  Time (mean ± σ):      1.126 s ±  0.101 s    [User: 141.1 ms, System: 956.1 ms]
  Range (min … max):    0.975 s …  1.287 s    10 runs

Summary
  'fd -e jpg' ran
   21.89 ± 2.33 times faster than 'find . -iname "*.jpg"'
```

与调试类似，浏览器也自带了一套出色的工具，用于分析网页加载性能，让你了解时间花在哪里（加载、渲染、脚本执行等）。
更多信息见 [Firefox](https://profiler.firefox.com/docs/) 和 [Chrome](https://developers.google.com/web/tools/chrome-devtools/rendering-tools)。

# 练习

## 调试

1. 在 Linux 上使用 `journalctl` 或在 macOS 上使用 `log show`，获取最近一天的超级用户访问和命令记录。
如果没有记录，你可以执行一些无害的命令（如 `sudo ls`），然后再检查。

1. 完成[这个](https://github.com/spiside/pdb-tutorial) `pdb` 动手教程以熟悉各种命令。想要更深入的教程，请阅读[这篇](https://realpython.com/python-debugging-pdb)。

1. 安装 [`shellcheck`](https://www.shellcheck.net/) 并尝试检查以下脚本。这段代码有什么问题？修复它。在你的编辑器中安装一个 linter 插件，以便自动获得警告提示。

   ```bash
   #!/bin/sh
   ## Example: a typical script with several problems
   for f in $(ls *.m3u)
   do
     grep -qi hq.*mp3 $f \
       && echo -e 'Playlist $f contains a HQ file in mp3 format'
   done
   ```

1. （进阶）阅读关于[可逆调试（Reversible Debugging）](https://undo.io/resources/reverse-debugging-whitepaper/)的内容，并使用 [`rr`](https://rr-project.org/) 或 [`RevPDB`](https://morepypy.blogspot.com/2016/07/reverse-debugging-for-python.html) 运行一个简单示例。

## 性能分析

1. [这里](/static/files/sorts.py) 是一些排序算法的实现。使用 [`cProfile`](https://docs.python.org/3/library/profile.html) 和 [`line_profiler`](https://github.com/pyutils/line_profiler) 来比较插入排序和快速排序的运行时间。每个算法的瓶颈是什么？然后使用 `memory_profiler` 检查内存消耗，为什么插入排序更好？现在看一下就地版的快速排序。挑战：使用 `perf` 来查看每种算法的循环计数和缓存命中率与未命中率。

1. 下面是一段（可能有些曲折的）Python 代码，使用一个函数来计算每个 Fibonacci 数：

   ```python
   #!/usr/bin/env python
   def fib0(): return 0

   def fib1(): return 1

   s = """def fib{}(): return fib{}() + fib{}()"""

   if __name__ == '__main__':

       for n in range(2, 10):
           exec(s.format(n, n-1, n-2))
       # from functools import lru_cache
       # for n in range(10):
       #     exec("fib{} = lru_cache(1)(fib{})".format(n, n))
       print(eval("fib9()"))
   ```

   将代码保存到一个文件并使其可执行。安装前置工具：[`pycallgraph`](https://lewiscowles1986.github.io/py-call-graph/) 和 [`graphviz`](https://graphviz.org/)。（如果你能运行 `dot`，说明你已经安装了 GraphViz。）使用 `pycallgraph graphviz -- ./fib.py` 运行代码，然后查看 `pycallgraph.png` 文件。`fib0` 被调用了几次？我们可以通过为函数添加缓存（memoization）来改进。取消注释那几行并重新生成图像。现在我们每个 `fibN` 函数被调用了几次？

1. 一个常见问题是你想要监听的端口已经被其他进程占用了。让我们来学习如何发现那个进程的 pid。首先执行 `python -m http.server 4444` 来启动一个在端口 `4444` 上监听的最小 Web 服务器。在另一个终端中运行 `lsof | grep LISTEN` 来打印所有监听中的进程和端口。找到该进程的 pid 并运行 `kill <PID>` 终止它。

1. 限制进程的资源可以是工具箱中的另一个有用工具。
尝试运行 `stress -c 3` 并使用 `htop` 可视化 CPU 使用率。然后，执行 `taskset --cpu-list 0,2 stress -c 3` 并观察。`stress` 占用了三个 CPU 吗？为什么没有？阅读 [`man taskset`](https://www.man7.org/linux/man-pages/man1/taskset.1.html)。
挑战：使用 [`cgroups`](https://www.man7.org/linux/man-pages/man7/cgroups.7.html) 实现同样的效果。尝试限制 `stress -m` 的内存消耗。

1. （进阶）命令 `curl ipinfo.io` 发起一个 HTTP 请求并获取你公网 IP 的信息。打开 [Wireshark](https://www.wireshark.org/)，尝试嗅探 `curl` 发送和接收的请求与响应数据包。（提示：使用 `http` 过滤器来仅查看 HTTP 数据包。）
