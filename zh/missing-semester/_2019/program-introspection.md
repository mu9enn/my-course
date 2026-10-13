---
layout: lecture
title: "程序内省"
presenter: Anish
date: 2019-01-29
order: 1
video:
  aspect: 62.5
  id: 74MhV-7hYzg
---

# 调试（Debugging）

当 `printf` 式的调试（即在代码中频繁打印变量值来排查问题）已经不够用时，就该请出调试器（debugger）了。

调试器允许你与程序的运行过程进行交互，你可以做这样的事情：

- 在程序执行到某一行时暂停其运行
- 逐行单步执行（single-step）程序
- 检查变量的值
- 以及大量更高级的功能

## GDB / LLDB

[GDB](https://www.gnu.org/software/gdb/) 和 [LLDB](https://lldb.llvm.org/)，支持多种类 C 语言。

让我们来看 [example.c](/2019/files/example.c)。用调试标志编译：
`gcc -g -o example example.c`。

打开 GDB：

`gdb example`

一些常用命令：

- `run` — 运行程序
- `b {函数名}` — 设置断点（breakpoint）
- `b {文件名}:{行号}` — 设置断点
- `c` — 继续执行（continue）
- `step` / `next` / `finish` — 单步进入 / 单步跨过 / 单步跳出
- `p {变量}` — 打印变量的值
- `watch {表达式}` — 设置观察点（watchpoint），当该表达式的值发生变化时触发
- `rwatch {表达式}` — 设置观察点，当该表达式的值被读取时触发
- `layout` — 打开源码/寄存器/内存的可视化布局

> 译者补充：`step`、`next` 和 `finish` 的区别在于它们对函数调用的处理方式。`step` 会在遇到函数调用时进入该函数内部；`next` 则直接跨过整个函数调用，停在下一行；`finish` 会一直运行直到当前函数返回。对于初学者来说，用 `next` 跳过你不太关心的函数调用，用 `step` 跟踪你正在排查的逻辑，是比较实用的策略。

## PDB

[PDB](https://docs.python.org/3/library/pdb.html) 是 Python 的调试器。

在你想进入 PDB 调试的地方插入 `import pdb; pdb.set_trace()`，它基本上是一个调试器（类似 GDB）和 Python 交互 Shell 的混合体。

## Web 浏览器的开发者工具（Developer Tools）

这是另一种调试器，只不过带有图形界面，方便你检查网页的 DOM、网络请求、性能等。

# strace

观察程序调用了哪些系统调用（system call）：`strace {程序}`。

> 译者补充：系统调用是程序与操作系统内核之间的接口。比如当你打开一个文件、读写网络、分配内存时，底层最终都是通过系统调用完成的。`strace` 会把所有这类调用及其参数、返回值打印出来，帮你定位「程序到底在向操作系统要什么」。

# 性能分析（Profiling）

性能分析的种类很多：CPU 分析、内存分析等。

最简方案：`time`。

## Go

用 CPU 分析器运行测试代码：`go test -cpuprofile=cpu.out`

分析性能分析结果：`go tool pprof -web cpu.out`

用内存分析器运行测试代码：`go test -memprofile=mem.out`

分析性能分析结果：`go tool pprof -web mem.out`

## Perf

基本性能统计：`perf stat {命令}`

用分析器运行一个程序：`perf record {命令}`

分析性能分析结果：`perf report`