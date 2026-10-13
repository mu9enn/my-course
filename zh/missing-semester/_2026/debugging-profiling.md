---
layout: lecture
title: "调试与性能分析"
description: >
  学习如何使用日志和调试器调试程序，以及如何对代码进行性能分析（profiling）。
thumbnail: /static/assets/thumbnails/2026/lec4.png
date: 2026-01-15
ready: true
panopto: "https://mit.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=a72c48e3-5eb2-46fa-aa03-b3b700e1ca8d"
video:
  aspect: 56.25
  id: 8VYT9TcUmKs
---

编程领域有一条黄金法则：代码不会按照你期望的方式运行，而是按照你告诉它的方式运行。弥合这个差距有时相当困难。在本讲中，我们将介绍处理有 bug 和资源消耗大的代码时使用的实用技巧：调试（debugging）和性能分析（profiling）。

# 调试

## 打印调试与日志

> "最有效的调试工具仍然是缜密的思考，辅以恰如其分的打印语句。" —— Brian Kernighan，_Unix for Beginners_。

调试程序的第一种方法是在你发现问题所在的代码位置周围添加打印语句，然后逐步迭代，直到获取足够多的信息来定位问题的根源。

第二种方法是在程序中使用日志（logging），而不是临时的打印语句。日志本质上"更加谨慎的打印"，通常通过一个日志框架来实现，该框架内置了对以下功能的支持：

- 将日志（或日志的子集）重定向到其他输出位置的能力；
- 设置严重性级别（如 INFO、DEBUG、WARN、ERROR 等），并允许你根据这些级别过滤输出；
- 支持对与日志条目相关的数据进行结构化日志记录，从而可以在事后更方便地提取这些信息。

此外，通常还会在编程时主动加入日志语句，这样当你需要调试时，相关数据可能就已经在日志中了！事实上，一旦你通过打印语句找到并修复了问题，把这些打印语句转换为正式的日志语句后再删除，通常是有价值的。这样，如果将来出现类似的 bug，你无需修改代码就能获得所需的诊断信息。

> **第三方日志**：许多程序支持 `-v` 或 `--verbose` 标志来在运行时打印更多信息，这对于排查某个命令为何失败很有用。有些程序甚至允许重复使用该标志以获取更详细的内容。在调试服务（数据库、Web 服务器等）的问题时，查看它们的日志——在 Linux 上通常位于 `/var/log/`。使用 `journalctl -u <service>` 来查看 systemd 服务的日志。对于第三方库，检查它们是否支持通过环境变量或配置来开启调试日志。

## 调试器

当你明确知道要打印什么、可以轻松修改并重 run 代码时，打印调试法非常有效。但在你不确定需要哪些信息、bug 只在难以复现的条件下出现、或者修改并重 run 程序的代价很大（启动时间长、需要重建复杂的运行状态等）时，调试器就派上用场了。

调试器是让你能够与正在运行的程序进行交互的工具，它允许你：

- 当执行到某一行时暂停程序；
- 逐指令地单步执行；
- 在崩溃后检查变量的值；
- 在满足某个条件时暂停执行；
- 以及许多更高级的功能。

大多数编程语言都支持（或自带）某种形式的调试器。最通用的**通用调试器**包括 [`gdb`](https://www.gnu.org/software/gdb/)（GNU Debugger）和 [`lldb`](https://lldb.llvm.org/)（LLVM Debugger），它们可以调试任何原生二进制文件。许多语言还有**语言特定的调试器**，它们与运行时集成得更紧密（如 Python 的 pdb 或 Java 的 jdb）。

`gdb` 是 C、C++、Rust 和其他编译型语言的默认标准调试器。它可以探测几乎任何进程，并获取其当前的机器状态：寄存器、堆栈、程序计数器等。

一些常用的 GDB 命令：

- `run` — 启动程序
- `b {function}` 或 `b {file}:{line}` — 设置断点
- `c` — 继续执行
- `step` / `next` / `finish` — 单步进入 / 单步跳过 / 单步跳出
- `p {variable}` — 打印变量的值
- `bt` — 显示回溯（调用栈）
- `watch {expression}` — 当表达式的值发生变化时暂停

> 考虑使用 GDB 的 TUI 模式（`gdb -tui`，或在 GDB 内按 `Ctrl-x a`），它会在分屏视图中并排显示源代码和命令提示符。

### 记录-回放调试

一些最令人头疼的 bug 是 _Heisenbugs_（海森堡 bug）：当你尝试观察它们时，它们似乎会消失或改变行为。竞态条件、时序相关的 bug、以及只在特定系统条件下才会出现的问题都属于这一类。传统的调试在这里通常无能为力，因为再次运行程序会产生不同的行为（例如，打印语句可能会让代码运行得足够慢，从而让竞态条件不再出现）。

**记录-回放调试**（record-replay debugging）通过记录程序的执行过程，并允许你以确定性的方式尽可能多地回放它，从而解决这个问题。更棒的是，你还可以_反向_穿越执行过程，精确定位错误发生的位置。

[rr](https://rr-project.org/) 是一款功能强大的 Linux 工具，它记录程序的执行并允许以完整的调试能力进行确定性回放。它与 GDB 兼容，所以你已熟悉其交互方式。

基本用法：

```bash
# 记录程序执行
rr record ./my_program

# 回放录制（会打开 GDB）
rr replay
```

真正的魔法发生在回放阶段。由于执行是确定性的，你可以使用**反向调试**命令：

- `reverse-continue`（`rc`）— 反向运行直到命中断点
- `reverse-step`（`rs`）— 反向单步执行一行
- `reverse-next`（`rn`）— 反向单步执行，跳过函数调用
- `reverse-finish` — 反向运行直到进入当前函数

这对调试来说非常强大。假设你遇到了一次崩溃——你不必猜测 bug 在哪里并设置断点，而是可以：

1. 运行到崩溃点
2. 检查损坏的状态
3. 在损坏的变量上设置一个观察点
4. `reverse-continue` 来精确找到它是在哪里被破坏的

**何时使用 rr：**
- 间歇性失败的不稳定测试
- 竞态条件和线程相关的 bug
- 难以复现的崩溃
- 任何你希望"时光倒流"的 bug

> 注意：rr 仅在 Linux 上可用，并且需要硬件性能计数器。它在没有暴露这些计数器的虚拟机中无法使用，例如大多数 AWS EC2 实例，它也不支持 GPU 访问。对于 macOS，可以看看 [Warpspeed](https://warpspeed.dev/)。

> **rr 与并发**：因为 rr 以确定性的方式记录执行过程，所以它会序列化线程调度。这意味着一些竞态条件在 rr 下可能不会表现出来（如果它们依赖于特定时序的话）。rr 仍然可以用于调试竞态条件——一旦你捕获了一个失败的运行，你可以可靠地回放它——但你可能需要多次记录才能抓到间歇性 bug。对于不涉及并发的 bug，rr 的效果最为出色：你总是可以精确复现执行，并使用反向调试来追踪损坏的位置。

## 系统调用追踪

有时你需要了解你的程序是如何与操作系统交互的。程序通过[系统调用](https://en.wikipedia.org/wiki/System_call)向内核请求服务——打开文件、分配内存、创建进程等等。追踪这些调用可以揭示程序为何挂起、它正在尝试访问哪些文件，以及它在哪里花费了等待时间。

### strace（Linux）和 dtruss（macOS）

[`strace`](https://www.man7.org/linux/man-pages/man1/strace.1.html) 允许你观察程序发出的每一个系统调用：

```bash
# 追踪所有系统调用
strace ./my_program

# 仅追踪与文件相关的调用
strace -e trace=file ./my_program

# 追踪子进程（对启动其他程序的程序非常重要）
strace -f ./my_program

# 追踪一个正在运行的进程
strace -p <PID>

# 显示时间信息
strace -T ./my_program
```

> 在 macOS 和 BSD 上，使用 [`dtruss`](https://www.manpagez.com/man/1/dtruss/)（它封装了 `dtrace`）来实现类似功能：

> 想要更深入地了解 `strace`，可以阅读 Julia Evans 的优秀 [strace zine](https://jvns.ca/strace-zine-unfolded.pdf)。

### bpftrace 和 eBPF

[eBPF](https://ebpf.io/)（扩展的 Berkeley 包过滤器）是一种功能强大的 Linux 技术，允许在内核中运行沙箱化的程序。[`bpftrace`](https://github.com/iovisor/bpftrace) 为编写 eBPF 程序提供了高级语法。这些是在内核中运行的任意程序，因此具有巨大的表达力（尽管语法有些类似 awk，略显笨拙）。最常见的用例是调查正在调用哪些系统调用，包括聚合操作（如计数或延迟统计），以及对系统调用参数进行内省（甚至过滤）。

```bash
# 追踪全局的文件打开系统调用（立即输出）
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'

# 按名称统计系统调用（在 Ctrl-C 时打印摘要）
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'
```

此外，你也可以使用 [`bcc`](https://github.com/iovisor/bcc) 之类的工具链直接用 C 语言编写 eBPF 程序，bcc 还附带了[许多实用的工具](https://www.brendangregg.com/blog/2015-09-22/bcc-linux-4.3-tracing.html)，如 `biosnoop`（用于打印磁盘操作的延迟分布）和 `opensnoop`（用于打印所有打开的文件）。

`strace` 的优势在于"即开即用"，而当你需要更低的开销、追踪内核函数、进行任何类型的聚合等时，`bpftrace` 是你应该选择的工具。不过要注意 `bpftrace` 必须以 `root` 运行，而且它通常监控整个内核，而非仅仅某个特定进程。要针对特定的程序，可以通过命令名或 PID 来过滤：

```bash
# 按命令名过滤（在 Ctrl-C 时打印摘要）
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_* /comm == "bash"/ { @[probe] = count(); }'

# 使用 -c 从启动时追踪特定命令（cpid = 子进程 PID）
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_* /pid == cpid/ { @[probe] = count(); }' -c 'ls -la'
```

`-c` 标志会运行指定的命令，并将 `cpid` 设置为其 PID，这在从程序启动开始追踪时非常有用。当被追踪的命令退出时，bpftrace 会打印聚合结果。

### 网络调试

对于网络问题，[`tcpdump`](https://www.man7.org/linux/man-pages/man1/tcpdump.1.html) 和 [Wireshark](https://www.wireshark.org/) 可以捕获并分析网络数据包：

```bash
# 捕获端口 80 上的数据包
sudo tcpdump -i any port 80

# 捕获并保存到文件供 Wireshark 分析
sudo tcpdump -i any -w capture.pcap
```

对于 HTTPS 流量，由于加密的存在，tcpdump 的作用就有限了。[mitmproxy](https://mitmproxy.org/) 之类的工具可以作为拦截代理来检查加密流量。浏览器的开发者工具（Network 标签页）通常是调试 Web 应用 HTTPS 请求的最简单方式——它们显示解密后的请求/响应数据、头信息和时间。

## 内存调试

内存错误——缓冲区溢出、释放后使用（use-after-free）、内存泄漏——是最危险也最难调试的bug 类型之一。它们往往不会立即崩溃，而是以某种方式破坏内存，导致问题在很久之后才出现。

### 检查器（Sanitizers）

查找内存错误的一种方法是使用**检查器**，它们是编译器提供的功能，可以对你的代码进行插桩，以在运行时检测错误。例如，广泛使用的**地址检查器**（AddressSanitizer, ASan）可以检测：

- 缓冲区溢出（栈、堆和全局）
- 释放后使用（use-after-free）
- 返回后使用（use-after-return）
- 内存泄漏

```bash
# 使用 AddressSanitizer 编译
gcc -fsanitize=address -g program.c -o program
./program
```

还有多种有用的检查器：

- **线程检查器**（ThreadSanitizer, TSan）：检测多线程代码中的数据竞态（`-fsanitize=thread`）
- **内存检查器**（MemorySanitizer, MSan）：检测对未初始化内存的读取（`-fsanitize=memory`）
- **未定义行为检查器**（UndefinedBehaviorSanitizer, UBSan）：检测如整数溢出等未定义行为（`-fsanitize=undefined`）

检查器需要重新编译，但速度足够快，可以在 CI 流水线中和日常开发中使用。

### Valgrind：当你无法重新编译时

[Valgrind](https://valgrind.org/) 以类似于虚拟机的方式运行你的程序来检测内存错误。它比检查器慢，但无需重新编译：

```bash
valgrind --leak-check=full ./my_program
```

在以下情况下使用 Valgrind：
- 你没有源代码
- 你无法重新编译（如第三方库）
- 你需要某些检查器无法提供的特定功能

Valgrind 实际上是一个功能强大的受控执行环境，我们在后面的性能分析部分还会进一步用到它！

## AI 用于调试

大语言模型（LLM）已经成为令人惊讶地有用的调试助手。它们在特定的调试任务方面表现出色，与传统工具形成互补。

**LLM 的擅长领域：**

- **解释晦涩的错误信息**：编译器错误，尤其是来自 C++ 模板或 Rust 借用检查器的错误，以晦涩难懂著称。LLM 可以将它们翻译成通俗的英文，并提出修复建议。

- **穿越语言和抽象边界**：如果你正在调试跨越多种语言的问题（例如 C 库中的 bug 通过 Python 绑定表现出来），LLM 可以帮助你导航不同的层次。它们特别擅长理解 FFI 边界、构建系统问题和跨语言调试（例如：我的程序报错了，但我认为是因为我某个依赖库中有 bug）。

- **将症状与根本原因关联起来**："我的程序运行正常但比预期多消耗了 10 倍内存" 这类模糊的症状，LLM 可以帮助调查，提出可能的原因和需要查找的内容。

- **分析崩溃转储和堆栈跟踪**：粘贴一个堆栈跟踪，询问可能导致它的原因。

> **关于调试符号的译者补充**：为了获取有意义的堆栈跟踪和调试信息，请确保你的二进制文件（以及任何链接的库）使用调试符号进行编译（`-g` 标志）。调试信息通常存储在 DWARF 格式中。此外，使用帧指针编译（`-fno-omit-frame-pointer`）可以使堆栈跟踪更加可靠，尤其对性能分析工具而言。如果没有这些，堆栈跟踪可能只显示内存地址或不完整。这对原生编译的程序（C++、Rust）比对 Python 或 Java 更加重要。

**需要牢记的局限性：**
- LLM 可能会"幻觉"出听起来合理但错误的解释
- 它们可能提出掩盖 bug 而非修复 bug 的建议
- 始终使用实际的调试工具来验证建议
- 它们最适合在理解你代码的基础上作为补充，而非替代品

> 这不同于 [开发环境讲座](/2026/development-environment/#ai-powered-development) 中涵盖的[通用 AI 编程能力](/2026/development-environment/#ai-powered-development)。这里我们专门讨论将 LLM 用作调试辅助工具。

# 性能分析

即使你的代码在功能上按照预期运行，如果在这个过程中耗尽了所有 CPU 或内存，那也远远不够。算法课程通常会教授大 O（big _O_）表示法，但不会教如何找到程序中的热点。既然[过早优化是万恶之源](https://wiki.c2.com/?PrematureOptimization)，你就应该了解分析器（profilers）和监控工具。它们会帮助你理解程序的哪些部分花费了最多的时间和/或资源，从而让你将精力集中在优化这些部分。

## 计时

衡量性能最简单的方法就是计时。在许多情况下，只需打印代码在两个点之间花费的时间就足够了。

然而，墙钟时间（wall clock time）可能会产生误导，因为你的计算机可能同时在运行其他进程或等待事件发生。`time` 命令区分了**墙钟时间**（Real）、**用户态时间**（User）和**内核态时间**（Sys）：

- **Real** — 从开始到结束的墙钟时间，包括等待时间
- **User** — 在 CPU 上运行用户代码的时间
- **Sys** — 在 CPU 上运行内核代码的时间

```bash
$ time curl https://missing.csail.mit.edu &> /dev/null
real	0m0.272s
user	0m0.079s
sys	    0m0.028s
```

这里这个请求花了将近 300 毫秒（wall clock 时间），但只消耗了 107 毫秒的 CPU 时间（user + sys）。其余时间是在等待网络。

## 资源监控

有时，分析程序性能的第一步是了解它的实际资源消耗情况。当程序受资源限制时，它们往往会运行缓慢。

- **通用监控**：[`htop`](https://htop.dev/) 是 `top` 的改进版本，它以各种统计信息的形式呈现当前运行的进程。常用快捷键：`<F6>` 排序进程，`t` 显示树状层级，`h` 切换线程显示。还有 [`btop`](https://github.com/aristocratos/btop) 监控**更多**内容。

- **I/O 操作**：[`iotop`](https://www.man7.org/linux/man-pages/man8/iotop.8.html) 显示实时的 I/O 使用信息。

- **内存使用**：[`free`](https://www.man7.org/linux/man-pages/man1/free.1.html) 显示总的空闲和已用内存。

- **打开的文件**：[`lsof`](https://www.man7.org/linux/man-pages/man8/lsof.8.html) 列出进程打开的文件信息。可用于检查哪个进程打开了特定文件。

- **网络连接**：[`ss`](https://www.man7.org/linux/man-pages/man8/ss.8.html) 允许你监控网络连接。一种常见用法是找出哪个进程占用了给定端口：`ss -tlnp | grep :8080`。

- **网络使用**：[`nethogs`](https://github.com/raboof/nethogs) 和 [`iftop`](https://pdw.ex-parrot.com/iftop/) 是用于监控每个进程网络使用情况的优秀交互式 CLI 工具。

## 可视化性能数据

人类在图形中识别模式的速度远快于在数字表格中。在分析性能时，绘制数据图通常能揭示在原始数字中不可见的趋势、尖峰和异常。

**让数据可绘制**：当为调试添加打印或日志语句时，考虑格式化输出以便日后轻松绘图。用 CSV 格式输出简单的"时间戳,值"（如 `1705012345,42.5`）比一句散文描述容易绘制得多。JSON 结构的日志也可以用最小的解析工作量来绘制。换句话说，以[整洁的方式](https://vita.had.co.nz/papers/tidy-data.pdf)记录你的数据。

**用 gnuplot 快速绘图**：对于简单的命令行绘图，[`gnuplot`](http://www.gnuplot.info/) 可以直接从数据文件生成图表：

```bash
# 绘制一个简单的 CSV（timestamp,value 格式）
gnuplot -e "set datafile separator ','; plot 'latency.csv' using 1:2 with lines"
```

**用 matplotlib 和 ggplot2 进行迭代探索**：对于更深入的分析，Python 的 [`matplotlib`](https://matplotlib.org/) 和 R 的 [`ggplot2`](https://ggplot2.tidyverse.org/) 支持迭代式探索。与一次性绘图不同，这些工具让你能够快速切片和转换数据以检验假设。ggplot2 的分面图（facet plots）功能尤为强大——你可以按类别将单个数据集拆分到多个子图中（例如，按端点或时间段对请求延迟进行分面），以揭示原本会被隐藏的模式。

**使用场景示例：**
- 绘制随时间变化的请求延迟，可以发现周期性减速（垃圾回收、定时任务、流量模式），而原始的分位数会掩盖这些现象
- 可视化一个不断增长的數據结构的插入时间，可能暴露算法复杂度问题——当底层数组容量翻倍时，向量插入的图表会显示出特征性的尖峰
- 按不同维度（请求类型、用户分组、服务器）对指标进行分面，往往能揭示"系统级别"的问题实际上仅限于某一类别

## CPU 分析器

大多数时候，当人们提到 _分析器_（profilers）时，他们指的是 _CPU 分析器_。主要有两种类型：

- **追踪型分析器**（Tracing profilers）：记录程序进行的每一次函数调用
- **采样型分析器**（Sampling profilers）：定期探测你的程序（通常为每毫秒一次），并记录程序的堆栈

采样型分析器的开销更低，通常更适合生产环境使用。

### perf：采样型分析器

[`perf`](https://www.man7.org/linux/man-pages/man1/perf.1.html) 是标准的 Linux 分析器。它可以分析任何程序而无需重新编译：

`perf stat` 给你一个快速概览，展示时间都花在了哪里：

```bash
$ perf stat ./slow_program

 Performance counter stats for './slow_program':

         3,210.45 msec task-clock                #    0.998 CPUs utilized
               12      context-switches          #    3.738 /sec
                0      cpu-migrations            #    0.000 /sec
              156      page-faults               #   48.587 /sec
   12,345,678,901      cycles                    #    3.845 GHz
    9,876,543,210      instructions              #    0.80  insn per cycle
    1,234,567,890      branches                  #  384.532 M/sec
       12,345,678      branch-misses             #    1.00% of all branches
```

真实程序的分析器输出包含大量信息。人类是视觉动物，阅读大量数字相当吃力。[火焰图](https://www.brendangregg.com/flamegraphs.html)是一种可视化方式，可以让分析数据更容易理解。

火焰图在 Y 轴上显示函数调用的层次结构，X 轴上显示与时间成正比的比例。它们是交互式的——你可以点击以缩小到程序的特定部分。

[![FlameGraph](https://www.brendangregg.com/FlameGraphs/cpu-bash-flamegraph.svg)](https://www.brendangregg.com/FlameGraphs/cpu-bash-flamegraph.svg)

要从 `perf` 数据生成火焰图：

```bash
# 记录性能数据
perf record -g ./my_program

# 生成火焰图（需要火焰图脚本）
perf script | stackcollapse-perf.pl | flamegraph.pl > flamegraph.svg
```

> 考虑使用 [Speedscope](https://www.speedscope.app/) 来获得交互式的 Web 版火焰图查看器，或使用 [Perfetto](https://perfetto.dev/) 进行全面的系统级分析。

### Valgrind 的 Callgrind：追踪型分析器

[`callgrind`](https://valgrind.org/docs/manual/cl-manual.html) 是一种分析工具，记录程序的调用历史和指令计数。与采样型分析器不同，它提供精确的调用计数，并能展示调用者和被调用者之间的关系：

```bash
# 使用 callgrind 运行
valgrind --tool=callgrind ./my_program

# 使用 callgrind_annotate（文本）或 kcachegrind（GUI）分析
callgrind_annotate callgrind.out.<pid>
kcachegrind callgrind.out.<pid>
```

Callgrind 比采样型分析器慢，但提供精确的调用计数，并且可以通过 `--cache-sim=yes` 选择性地模拟缓存行为，如果你需要这些信息的话。

> 如果你使用某种特定的语言，可能还有更专业的分析器。例如，Python 有 [`cProfile`](https://docs.python.org/3/library/profile.html) 和 [`py-spy`](https://github.com/benfred/py-spy)，Go 有 [`go tool pprof`](https://pkg.go.dev/cmd/pprof)，Rust 有 [`cargo-flamegraph`](https://github.com/flamegraph-rs/flamegraph)（实际上它可以用于任何编译型程序！）。

## 内存分析器

内存分析器帮助你了解程序随时间如何使用内存，并查找内存泄漏。

### Valgrind 的 Massif

[`massif`](https://valgrind.org/docs/manual/ms-manual.html) 分析堆内存的使用情况：

```bash
valgrind --tool=massif ./my_program
ms_print massif.out.<pid>
```

这会显示随时间变化的堆使用情况，帮助你识别内存泄漏和不必要的内存分配。

> 对于 Python，[`memory-profiler`](https://pypi.org/project/memory-profiler/) 提供了按行级别的内存使用信息。

## 基准测试

当需要比较不同实现或工具的性能时，[`hyperfine`](https://github.com/sharkdp/hyperfine) 对于命令行程序的基准测试非常出色：

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

> 对于 Web 开发，浏览器开发者工具包含出色的分析器。参见 [Firefox Profiler](https://profiler.firefox.com/docs/) 和 [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools/rendering-tools) 文档。

# 练习

## 调试

1. **调试一个排序算法**：以下伪代码实现了合并排序，但包含一个 bug。用你选择的语言实现它，然后使用调试器（gdb、lldb、pdb 或你 IDE 的调试器）找到并修复 bug。

   ```
   function merge_sort(arr):
       if length(arr) <= 1:
           return arr
       mid = length(arr) / 2
       left = merge_sort(arr[0..mid])
       right = merge_sort(arr[mid..end])
       return merge(left, right)

   function merge(left, right):
       result = []
       i = 0, j = 0
       while i < length(left) AND j < length(right):
           if left[i] <= right[j]:
               append result, left[i]
               i = i + 1
           else:
               append result, right[i]
               j = j + 1
       append remaining elements from left and right
       return result
   ```

   测试向量：`merge_sort([3, 1, 4, 1, 5, 9, 2, 6])` 应该返回 `[1, 1, 2, 3, 4, 5, 6, 9]`。使用断点并逐步执行 merge 函数，找到错误元素被选择的位置。

2. 安装 [`rr`](https://rr-project.org/) 并使用反向调试来查找一个损坏 bug。将此程序保存为 `corruption.c`：

   ```c
   #include <stdio.h>

   typedef struct {
       int id;
       int scores[3];
   } Student;

   Student students[2];

   void init() {
       students[0].id = 1001;
       students[0].scores[0] = 85;
       students[0].scores[1] = 92;
       students[0].scores[2] = 78;

       students[1].id = 1002;
       students[1].scores[0] = 90;
       students[1].scores[1] = 88;
       students[1].scores[2] = 95;
   }

   void curve_scores(int student_idx, int curve) {
       for (int i = 0; i < 4; i++) {
           students[student_idx].scores[i] += curve;
       }
   }

   int main() {
       init();
       printf("=== Initial state ===\n");
       printf("Student 0: id=%d\n", students[0].id);
       printf("Student 1: id=%d\n", students[1].id);

       curve_scores(0, 5);

       printf("\n=== After curving ===\n");
       printf("Student 0: id=%d\n", students[0].id);
       printf("Student 1: id=%d\n", students[1].id);

       if (students[1].id != 1002) {
           printf("\nERROR: Student 1's ID was corrupted! Expected 1002, got %d\n",
                  students[1].id);
           return 1;
       }
       return 0;
   }
   ```

   使用 `gcc -g corruption.c -o corruption` 编译并运行它。Student 1 的 ID 被损坏了，但损坏发生在只接触 student 0 的函数中。使用 `rr record ./corruption` 和 `rr replay` 找到罪魁祸首。在 `students[1].id` 上设置一个观察点，并在损坏发生后使用 `reverse-continue` 找到确切是哪行代码覆写了它。

3. 使用 AddressSanitizer 调试一个内存错误。将其保存为 `uaf.c`：

   ```c
   #include <stdlib.h>
   #include <string.h>
   #include <stdio.h>

   int main() {
       char *greeting = malloc(32);
       strcpy(greeting, "Hello, world!");
       printf("%s\n", greeting);

       free(greeting);

       greeting[0] = 'J';
       printf("%s\n", greeting);

       return 0;
   }
   ```

   首先在不使用检查器的情况下编译和运行：`gcc uaf.c -o uaf && ./uaf`。它可能看起来正常工作。现在使用 AddressSanitizer 编译：`gcc -fsanitize=address -g uaf.c -o uaf && ./uaf`。阅读错误报告。ASan 发现了什么 bug？修复它指出的问题。

4. 使用 `strace`（Linux）或 `dtruss`（macOS）来追踪类似 `ls -l` 的命令所发出的系统调用。它正在做哪些系统调用？尝试追踪一个更复杂的程序，看看它打开了哪些文件。

5. 使用 LLM 来帮助调试一个晦涩的错误信息。尝试复制一个编译器错误（尤其是来自 C++ 模板或 Rust 的），并请求解释和修复。尝试将 `strace` 或地址检查器的部分输出也给它。

## 性能分析

1. 使用 `perf stat` 为你选择的程序获取基本的性能统计信息。不同的计数器分别代表什么含义？

2. 使用 `perf record` 进行分析。将此程序保存为 `slow.c`：

   ```c
   #include <math.h>
   #include <stdio.h>

   double slow_computation(int n) {
       double result = 0;
       for (int i = 0; i < n; i++) {
           for (int j = 0; j < 1000; j++) {
               result += sin(i * j) * cos(i + j);
           }
       }
       return result;
   }

   int main() {
       double r = 0;
       for (int i = 0; i < 100; i++) {
           r += slow_computation(1000);
       }
       printf("Result: %f\n", r);
       return 0;
   }
   ```

   使用调试符号编译：`gcc -g -O2 slow.c -o slow -lm`。运行 `perf record -g ./slow`，然后 `perf report` 查看时间花在了哪里。尝试使用火焰图脚本生成火焰图。

3. 使用 `hyperfine` 对同一任务的不同实现进行基准测试（例如 `find` 与 `fd`、`grep` 与 `ripgrep`，或你自己代码的两个版本）。

4. 运行一个资源密集型的程序时，使用 `htop` 监控你的系统。尝试使用 `taskset` 限制进程可以使用哪些 CPU：`taskset --cpu-list 0,2 stress -c 3`。为什么 `stress` 没有使用三个 CPU？

5. 一个常见的问题是：你想要监听的端口已经被其他进程占用了。学习如何找到那个进程：首先执行 `python -m http.server 4444` 在端口 4444 上启动一个最小的 Web 服务器。在另一个终端中运行 `ss -tlnp | grep 4444` 来查找该进程。使用 `kill <PID>` 终止它。