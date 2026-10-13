---
layout: lecture
title: "课程导论 + Shell"
description: >
  了解本课程的设计动机，并上手使用 shell。
thumbnail: /static/assets/thumbnails/2020/lec1.png
date: 2020-01-13
ready: true
video:
  aspect: 56.25
  id: Z56Jmr9Z34Q
---

# 动机

作为计算机科学家，我们深知计算机在辅助重复性任务方面表现卓越。然而，我们常常忘记这一点同样适用于我们_使用_计算机的方式，而不仅仅是我们希望程序执行的计算。当我们面对任何与计算机相关的问题时，身边有大量工具触手可及，它们能让我们事半功倍，解决更复杂的问题。然而许多开发者只使用了其中极小的一部分——我们仅靠死记硬背几句"咒语"勉强应付，一旦卡住就盲目地从网上复制粘贴别人的命令。

本课程就是为了弥补这一缺失。

我们希望教你：如何充分用好你已知的工具、为你提供新工具箱里的新工具，并希望能够激发你自己去探索（甚至创造）更多工具的热情。我们认为，这正是大多数计算机科学课程表中缺失的一门课。

# 课程结构

本课程共包含 11 个 1 小时的讲座，每个讲座围绕一个[特定主题](/2020/)展开。这些讲座彼此相对独立，但随着学期推进，我们会默认你已熟悉之前讲座中涉及的内容。网上有讲座笔记，但课堂上展示的内容（例如各种演示 demo）很多并未收录在笔记中。我们会录制讲座视频并在线发布。

由于仅有 11 个 1 小时的讲座，内容相当密集。为了让你在适合自己的节奏下熟悉内容，每个讲座都附带一组练习，引导你掌握讲座的核心要点。每个讲座之后，我们会举办办公时间（office hours），届时我们会在线答疑。如果你是通过网络旁听本课程，可以通过
[missing-semester@mit.edu](mailto:missing-semester@mit.edu) 给我们发送邮件提问。

受时间限制，我们无法像完整的学分课程那样对每个工具都深入讲解。在可行的情况下，我们会为你提供进一步深入学习某个工具或主题的资源链接；如果某个工具特别吸引你，也欢迎随时联系我们，我们很乐意为你指点方向！

# 主题一：Shell

## 什么是 shell？

如今的计算机提供了各式各样的操作界面：精美的图形用户界面、语音交互界面，甚至增强现实/虚拟现实（AR/VR）也随处可见。这些界面在 80% 的使用场景中表现优异，但它们往往在本质上有功能限制——你无法按下尚未存在的按钮，也无法发出尚未被编程设定的语音指令。要想充分利用计算机提供的全部工具，我们必须回归传统，使用文本界面：**Shell（命令行解释器）**。

几乎你能拿到手的任何平台都至少有一个 shell，许多平台甚至提供多种 shell 供你选择。虽然它们在细节上可能有所不同，但本质上大同小异：它们都能让你运行程序、给程序输入数据，并以半结构化的方式检查程序的输出。

在本讲座中，我们将以 **Bourne Again SHell**（简称 **bash**）为重点。bash 是最广泛使用的 shell 之一，它的语法与你在其他许多 shell 中见到的语法非常相似。要打开一个 shell _提示符_（prompt，即你输入命令的地方），你需要一个 _终端_（terminal）。你的设备很可能已经预装了终端，或者你可以很方便地安装一个。

## 使用 shell

启动终端后，你会看到一个 _提示符_，通常看起来大致如下：

```console
missing:~$
```

这是与 shell 交互的主要文本界面。它告诉你：你当前连接的机器名是 `missing`，你的"当前工作目录"（current working directory，即你当前所处的位置）是 `~`（home 目录的缩写）。`$` 表示你当前不是 root 用户（稍后会详细介绍）。在这个提示符下，你可以输入 _命令_，shell 会对其进行解释。最基本的命令就是执行程序：

```console
missing:~$ date
Fri 10 Jan 2020 11:49:31 AM EST
missing:~$
```

在这里，我们执行了 `date` 程序，它（或许并不令人意外地）打印出了当前的日期和时间。shell 随即等待我们输入下一个命令。我们还可以为命令附带 _参数_（arguments）：

```console
missing:~$ echo hello
hello
```

这里，我们告诉 shell 执行 `echo` 程序，并传入参数 `hello`。`echo` 程序的作用仅仅是把它的参数打印出来。shell 通过以空白字符为分隔符拆分命令文本来解析这条命令，然后运行由第一个词指定的程序，并将后续的每个词作为程序可以访问的参数传给它。如果你要传入的参数中包含空格或其他特殊字符（比如一个名为"My Photos"的目录），你可以用单引号 `'` 或双引号 `"` 把整个参数括起来（`"My Photos"`），也可以用反斜杠 `\` 对相关的特殊字符进行转义（`My\ Photos`）。

那么 shell 是如何找到 `date` 或 `echo` 这些程序的呢？shell 本身就是一个编程环境，和 Python 或 Ruby 类似——它拥有变量、条件判断、循环和函数（下一讲介绍！）。你在 shell 中运行的每一条命令，实际上都是在写一小段由 shell 解释执行的代码。如果 shell 被要求执行的命令不匹配任何编程关键字，它便会查阅一个名为 `$PATH` 的 _环境变量_（environment variable），该变量列出了 shell 在接收到命令时需要搜索哪些目录：

```console
missing:~$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
missing:~$ which echo
/bin/echo
missing:~$ /bin/echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

当我们运行 `echo` 命令时，shell 看到需要执行 `echo` 这个程序，于是依次在 `$PATH` 中以冒号 `:` 分隔的目录列表中查找名为 `echo` 的文件。找到之后，shell 就执行它（前提是文件具有 _可执行权限_；稍后详解）。我们可以使用 `which` 程序来查找某个程序名对应的是哪个文件。我们也可以直接给出要执行文件的 _路径_（path），从而绕过 `$PATH` 的搜索。

## 在 shell 中导航

shell 中的路径是一个由分隔符分隔的目录列表；在 Linux 和 macOS 上使用 `/` 分隔，在 Windows 上使用 `\` 分隔。在 Linux 和 macOS 上，路径 `/` 是文件系统的"根"，所有目录和文件都位于其下；而在 Windows 上，每个磁盘分区都有一个根目录（例如 `C:\`）。在本课程中，我们主要假定你使用的是类 Unix 文件系统。以 `/` 开头的路径称为 _绝对路径_（absolute path）。其他所有路径均为 _相对路径_（relative path）。相对路径是相对于当前工作目录而言的，我们可用 `pwd` 命令查看当前工作目录，用 `cd` 命令更改它。在路径中，`.` 表示当前目录，`..` 表示其上级目录：

```console
missing:~$ pwd
/home/missing
missing:~$ cd /home
missing:/home$ pwd
/home
missing:/home$ cd ..
missing:/$ pwd
/
missing:/$ cd ./home
missing:/home$ pwd
/home
missing:/home$ cd missing
missing:~$ pwd
/home/missing
missing:~$ ../../bin/echo hello
hello
```

注意我们的 shell 提示符一直跟踪显示着当前的工作目录。你可以将提示符配置为显示各种有用信息，我们将在之后的讲座中介绍这一点。

一般来说，除非显式指定，否则程序会在当前工作目录下运行。例如，它通常会在那里查找文件，并在需要时在那里创建新文件。

要查看某个目录下有什么内容，我们使用 `ls` 命令：

```console
missing:~$ ls
missing:~$ cd ..
missing:/home$ ls
missing
missing:/home$ cd ..
missing:/$ ls
bin
boot
dev
etc
home
...
```

除非将某个目录作为 `ls` 的第一个参数传入，否则 `ls` 会打印当前目录的内容。大多数命令都接受以 `-` 开头的 _标志_（flags）和 _选项_（options，即带值的标志）来修改自身行为。通常，运行一个程序并带上 `-h` 或 `--help` 标志，就会打印出帮助文本，告诉你有哪些标志和选项可用。例如 `ls --help` 告诉我们：

```
  -l                         use a long listing format
```

```console
missing:~$ ls -l /home
drwxr-xr-x 1 missing  users  4096 Jun 15  2019 missing
```

这为我们提供了每个文件或目录的更多详细信息。首先，行首的 `d` 告诉我们 `missing` 是一个目录。接下来是三组三个字符（`rwx`）。它们分别指示了文件的所有者（`missing`）、文件所属的组（`users`）以及其他所有人对该项目分别拥有什么权限。`-` 表示该主体不具备该项权限。在上述例子中，只有所有者被允许修改（`w`）`missing` 目录（即在其中添加或删除文件）。要进入一个目录，用户必须对该目录（及其所有上级目录）拥有"搜索"权限（以"执行"权限表示：`x`）。要列出其内容，用户必须对该目录拥有读取（`r`）权限。对于普通文件，权限正如你预期的一般。注意 `/bin` 中几乎大部分文件都对最后一组"其他所有人"设置了 `x` 权限，这意味着任何人都可以执行这些程序。

此时你还应该了解另外几个常用程序：`mv`（移动或重命名文件）、`cp`（复制文件）和 `mkdir`（创建新目录）。

如果你希望 _了解更多_ 某个程序的参数、输入、输出或它的工作原理，可以尝试 `man` 程序。它以程序名为参数，展示该程序的 _手册页_（manual page）。按 `q` 退出。

```console
missing:~$ man ls
```

## 连接程序

在 shell 中，每个程序都关联着两条主要的"数据流"：它们的 _输入流_（input stream）和 _输出流_（output stream）。当程序试图读取输入时，它从输入流中读取；当程序打印内容时，它写到输出流中。通常情况下，一个程序的输入和输出都来自你的终端——即你的键盘作为输入、你的屏幕作为输出。但我们也可以"重新接线"这些流！

最简单的重定向形式是 `< file` 和 `> file`。它们分别将程序的输入流和输出流重定向到一个文件：

```console
missing:~$ echo hello > hello.txt
missing:~$ cat hello.txt
hello
missing:~$ cat < hello.txt
hello
missing:~$ cat < hello.txt > hello2.txt
missing:~$ cat hello2.txt
hello
```

如上面例子所示，`cat` 是一个将文件 _concatenate_（拼接）在一起的程序。当 `cat` 接收到文件名作为参数时，它会按顺序把每个文件的内容打印到其输出流中。但当 `cat` 没有接收任何参数时，它会从输入流读取内容并打印到输出流（如第三个示例）。

你还可以使用 `>>` 向文件末尾追加内容。而输入/输出重定向最强大的用法在于 _管道_（pipes）的使用。`|` 运算符让你可以"串联"多个程序，使得一个程序的输出成为另一个程序的输入：

```console
missing:~$ ls -l / | tail -n1
drwxr-xr-x 1 root  root  4096 Jun 20  2019 var
missing:~$ curl --head --silent google.com | grep --ignore-case content-length | cut --delimiter=' ' -f2
219
```

我们将在"数据处理"（data wrangling）讲座中更深入地介绍如何利用管道的更多细节。

## 一个多功能而强大的工具

在大多数类 Unix 系统上，有一个用户是特殊的：那就是 "root" 用户。你可能在前面列出的文件信息中看到过它。root 用户凌驾于（几乎）所有限制之上，可以在系统中创建、读取、更新和删除任何文件。不过你通常不应该以 root 用户身份登录系统，因为这样做很容易不小心把系统搞坏。你应该使用的是 `sudo` 命令。顾名思义，`sudo` 允许你"以 su（super user，即 super user 的缩写，意为超级用户/管理员）的身份做某事"。当你遇到权限被拒绝（Permission denied）的错误时，通常是因为你需要以 root 身份来操作。不过动手之前，务必先确认你真的打算这么做！

有一件你需要 root 权限才能做的事是向挂载在 `/sys` 下的 `sysfs` 文件系统写入数据。`sysfs` 将许多内核参数以文件的形式暴露出来，这样你就可以在不使用专用工具的情况下轻松地动态重新配置内核。**请注意，sysfs 在 Windows 或 macOS 上并不存在。**

例如，你笔记本电脑屏幕的亮度通过以下路径下一个名为 `brightness` 的文件来暴露：

```
/sys/class/backlight
```

向这个文件中写入一个数值，就可以改变屏幕亮度。你第一反应可能是这样做：

```console
$ sudo find -L /sys/class/backlight -maxdepth 2 -name '*brightness*'
/sys/class/backlight/thinkpad_screen/brightness
$ cd /sys/class/backlight/thinkpad_screen
$ sudo echo 3 > brightness
An error occurred while redirecting file 'brightness'
open: Permission denied
```

这个错误可能令人惊讶。毕竟我们已经用了 `sudo` 运行命令！这是关于 shell 运行方式的一个重要知识点。像 `|`、`>` 和 `<` 这样的操作是由 _shell_（而非各个单独的程序）来执行的。`echo` 等程序并不"知道" `|` 的存在；它们只是从输入流读取并向输出流写入，无论输入输出是什么。在上述例子中，_shell_（以你的普通用户身份认证，而非 root）试图以写入方式打开 brightness 文件，再把它设置为 `sudo echo` 的输出目标，但被拒绝，因为 shell 本身并没有以 root 身份运行。利用这个认识，我们可以绕开这个限制：

```console
$ echo 3 | sudo tee brightness
```

因为在这里是 `tee` 程序以写入方式打开 `/sys` 文件，而 _它_ 是以 `root` 身份运行的，所以权限限制就顺利通过了。你可以透过 `/sys` 控制各种有趣且有实用价值的系统事项，比如各种系统 LED 的状态（你的路径可能不同）：

```console
$ echo 1 | sudo tee /sys/class/leds/input6::scrolllock/brightness
```

# 下一步

到这里，你已经对 shell 有了足够的了解，足以完成一些基本任务。你应该能够导航查找感兴趣的文件，并熟练使用大多数程序的基本功能。在下一讲中，我们将讨论如何利用 shell 和众多好用的命令行程序来执行并自动化更复杂的任务。

# 练习

本课程的所有讲座都附有练习。有些练习会要求你完成一个具体的任务，而另一些则是开放式的，比如"尝试使用 X 和 Y 程序"。我们非常鼓励你亲自尝试。

我们并未为练习编写答案。如果你在某个具体问题上卡住了，欢迎给我们发邮件描述你到目前为止尝试过的内容，我们会尽力帮助你。

 1. 在本课程中，你需要使用类 Unix 的 shell，例如 Bash 或 ZSH。如果你在 Linux 或 macOS 上，无需做任何特殊配置。如果你在 Windows 上，请确保你没有在使用 `cmd.exe` 或 PowerShell；你可以使用 [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/) 或一台 Linux 虚拟机来使用类 Unix 的命令行工具。要确认你正在运行合适的 shell，可以试试执行命令 `echo $SHELL`。如果输出类似 `/bin/bash` 或 `/usr/bin/zsh`，说明你正在运行正确的程序。
 1. 在 `/tmp` 下新建一个名为 `missing` 的目录。
 1. 查阅 `touch` 程序的用法。`man` 程序是你的好帮手。
 1. 使用 `touch` 在 `missing` 目录中创建一个新的文件，名为 `semester`。
 1. 逐行将以下内容写入该文件：
    ```
    #!/bin/sh
    curl --head --silent https://missing.csail.mit.edu
    ```
    第一行可能需要花些功夫才能正确输入。需要知道的是，`#` 在 Bash 中用来开启注释，而 `!` 在双引号（`"`）字符串中也具有特殊含义。Bash 对单引号字符串（`'`）的处理方式不同——在这种情况下使用单引号即可。详见 Bash 手册中关于[引用（Quoting）](https://www.gnu.org/software/bash/manual/html_node/Quoting.html) 的部分。
 1. 尝试执行这个文件——即在 shell 中输入该脚本的路径（`./semester`）然后按回车。通过观察 `ls` 的输出（提示：查看文件的权限位）来理解为什么它不会工作。
 1. 通过显式启动 `sh` 解释器并将 `semester` 作为其第一个参数来运行该命令，即执行 `sh semester`。为什么这次能成功，而 `./semester` 不行？
 1. 查阅 `chmod` 程序（例如，使用 `man chmod`）。
 1. 使用 `chmod` 使得你可以直接运行 `./semester`，而不必再键入 `sh semester`。你的 shell 是如何知道应该用 `sh` 来解释这个文件的？详见 [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)) 行的相关说明。
 1. 使用 `|` 和 `>` 将 `semester` 输出的"最后修改时间"写入你 home 目录下的一个名为 `last-modified.txt` 的文件中。
 1. 写一个命令，从 `/sys` 中读取你笔记本电脑电池电量或台式机 CPU 温度。注意：如果你是 macOS 用户，你的操作系统没有 sysfs，可以跳过此练习。