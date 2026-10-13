---
layout: lecture
title: "命令行环境"
description: >
  了解作业控制、终端复用器、点文件和远程 SSH 连接。
thumbnail: /static/assets/thumbnails/2020/lec5.png
date: 2020-01-21
ready: true
video:
  aspect: 56.25
  id: e8BO_dYxk5c
---

在本节中，我们将介绍多种可以改进 shell 使用体验的方法。到目前为止，我们已经一直在使用 shell，但主要局限于执行各种命令。接下来，我们将学习如何同时运行多个进程并有效地追踪它们，如何停止或暂停特定的进程，以及如何将进程放到后台运行。

我们还将学习如何通过定义别名（aliases）和使用点文件（dotfiles）配置 shell 及其他工具。这两者都能帮你节省时间——例如，在所有机器上复用同一套配置，而无需反复输入冗长的命令。我们还会了解如何通过 SSH 操作远程机器。


# 作业控制

有些情况下，你需要在程序运行过程中中断它，比如某个命令执行时间过长（例如 `find` 在一个结构非常庞大的目录中搜索）。大多数时候，按 `Ctrl-C` 即可停止命令。但这究竟是如何运作的？为什么有时 `Ctrl-C` 无法终止进程？

## 终止进程

你的 shell 使用一种名为**信号（signal）**的 UNIX 通信机制向进程传达信息。当进程收到信号时，它会停止当前的执行、处理该信号，并可能根据信号携带的信息改变执行流程。因此，信号本质上是**软件中断（software interrupts）**。

在我们的场景中，输入 `Ctrl-C` 会提示 shell 向进程发送一个 `SIGINT` 信号。

下面是一个极简的 Python 程序，它捕获 `SIGINT` 信号并将其忽略，因此不再被终止。要杀掉这个程序，我们可以改用 `SIGQUIT` 信号，即输入 `Ctrl-\`。

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

下面展示了向该程序发送两次 `SIGINT`，随后发送一次 `SIGQUIT` 时发生的情况。注意，`^` 是终端中键入 `Ctrl` 时的显示方式。

```
$ python sigint.py
24^C
I got a SIGINT, but I am not stopping
26^C
I got a SIGINT, but I am not stopping
30^\[1]    39913 quit       python sigint.py
```

虽然 `SIGINT` 和 `SIGQUIT` 通常都与终端相关的请求相关联，但更通用的请求进程优雅退出的信号是 `SIGTERM`。要发送该信号，我们可以使用 [`kill`](https://www.man7.org/linux/man-pages/man1/kill.1.html) 命令，语法为 `kill -TERM <PID>`。

## 暂停与后台进程

信号的功能不只是终止进程。例如，`SIGSTOP` 可以暂停进程。在终端中，按 `Ctrl-Z` 会提示 shell 发送一个 `SIGTSTP` 信号（Terminal Stop 的缩写，即终端版本的 `SIGSTOP`）。

随后可使用 [`fg`](https://www.man7.org/linux/man-pages/man1/fg.1p.html) 或 [`bg`](https://man7.org/linux/man-pages/man1/bg.1p.html) 分别在前台或后台继续已暂停的作业。

[`jobs`](https://www.man7.org/linux/man-pages/man1/jobs.1p.html) 命令会列出与当前终端会话关联的未完成作业。

你可以使用进程的 pid 引用这些作业（可以使用 [`pgrep`](https://www.man7.org/linux/man-pages/man1/pgrep.1.html) 来查找 pid）。更直观的方式是，你也可以使用百分号加上作业编号来引用一个进程（作业编号由 `jobs` 显示）。要引用最后一个被放到后台的作业，你可以使用特殊参数 `$!`。

还需要知道的一点是，命令末尾的 `&` 后缀会在后台运行该命令并立即返回提示符，尽管它仍然会使用 shell 的 STDOUT（可能会产生一些烦人的输出），此时可以使用 shell 重定向来处理。

要将一个正在运行的程序放到后台，可以先按 `Ctrl-Z`，然后执行 `bg`。

注意，后台进程仍然是你的终端的子进程，关闭终端会导致它们被终止（这会发送另一个信号 `SIGHUP`）。要避免这种情况，你可以使用 [`nohup`](https://www.man7.org/linux/man-pages/man1/nohup.1.html) 来运行程序（它包装了对 `SIGHUP` 的忽略），或者在进程已经启动后使用 `disown`。另外，你也可以使用终端复用器，下一节将对此进行介绍。

下面是一个示例会话，展示了上述的一些概念。

```
$ sleep 10000
^Z
[1]  + 18653 suspended  sleep 10000

$ nohup sleep 2000 &
[2] 18745
appending output to nohup.out

$ jobs
[1]  + suspended  sleep 10000
[2]  - running    nohup sleep 2000

$ bg %1
[1]  - 18653 continued  sleep 10000

$ jobs
[1]  - running    sleep 10000
[2]  + running    nohup sleep 2000

$ kill -STOP %1
[1]  + 18653 suspended (signal)  sleep 10000

$ jobs
[1]  + suspended (signal)  sleep 10000
[2]  - running    nohup sleep 2000

$ kill -SIGHUP %1
[1]  + 18653 hangup     sleep 10000

$ jobs
[2]  + running    nohup sleep 2000

$ kill -SIGHUP %2

$ jobs
[2]  + running    nohup sleep 2000

$ kill %2
[2]  + 18745 terminated  nohup sleep 2000

$ jobs

```

一个特殊的信号是 `SIGKILL`，因为它无法被进程捕获，并且总是立即终止进程。然而，它可能会带来一些副作用，比如留下孤儿子进程。

你可以[在此](https://en.wikipedia.org/wiki/Signal_(IPC))或输入 [`man signal`](https://www.man7.org/linux/man-pages/man7/signal.7.html) 或 `kill -l` 来了解更多关于这些及其他信号的信息。


# 终端复用器

在使用命令行界面时，你通常需要同时运行多个任务。例如，你可能希望并排运行编辑器和程序。虽然可以通过打开新的终端窗口来实现，但使用终端复用器（terminal multiplexer）是更加灵活的解决方案。

像 [`tmux`](https://www.man7.org/linux/man-pages/man1/tmux.1.html) 这样的终端复用器，允许你使用窗格（panes）和标签页（tabs）来复用终端窗口，从而可以与多个 shell 会话进行交互。此外，终端复用器还允许你**分离（detach）**当前终端会话，并在稍后的时间**重新附加（reattach）**。当你在操作远程机器时，这能极大改善你的工作流程——因为它可以避免使用 `nohup` 之类的技巧。

如今最流行的终端复用器是 [`tmux`](https://www.man7.org/linux/man-pages/man1/tmux.1.html)。`tmux` 高度可配置，配合其关联的快捷键，你可以创建多个标签页和窗格，并在它们之间快速导航。

`tmux` 期望你记住它的快捷键，所有快捷键的格式都是 `<C-b> x`，含义是：（1）按下 `Ctrl+b`，（2）松开 `Ctrl+b`，然后（3）按 `x` 键。`tmux` 中存在如下对象层级：

- **会话（Sessions）**——一个独立的会话是一个独立的工作区，包含一个或多个窗口
    + `tmux` 启动一个新会话。
    + `tmux new -s NAME` 以指定名称启动。
    + `tmux ls` 列出当前会话。
    + 在 `tmux` 内部，键入 `<C-b> d` 可分离当前会话。
    + `tmux a` 附加最后一个会话。可以使用 `-t` 标志来指定要附加的会话。

- **窗口（Windows）**——相当于编辑器或浏览器中的标签页，它们是同一会话中视觉上独立的部分
    + `<C-b> c` 创建新窗口。要关闭它，只需通过 `<C-d>` 终止其中的 shell 即可。
    + `<C-b> N` 跳转到第 _N_ 个窗口。注意窗口是编号的。
    + `<C-b> p` 切换到上一个窗口。
    + `<C-b> n` 切换到下一个窗口。
    + `<C-b> ,` 重命名当前窗口。
    + `<C-b> w` 列出当前窗口。

- **窗格（Panes）**——类似于 vim 的分割窗口，窗格允许你在同一个可视区域内拥有多个 shell
    + `<C-b> "` 水平分割当前窗格。
    + `<C-b> %` 垂直分割当前窗格。
    + `<C-b> <方向>` 移动到指定 _方向_ 的窗格。这里的"方向"指的是方向键。
    + `<C-b> z` 切换当前窗格的缩放状态。
    + `<C-b> [` 开始进入滚动模式（scrollback）。之后可以按 `<space>` 开始选择，按 `<enter>` 复制所选内容。
    + `<C-b> <space>` 循环切换窗格布局。

如需进一步阅读，[这里](https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/)有一份 `tmux` 的快速入门教程，[这里](https://linuxcommand.org/lc3_adv_termmux.php) 则有更详细的解释，涵盖了原始的 `screen` 命令。你还应该熟悉 [`screen`](https://www.man7.org/linux/man-pages/man1/screen.1.html)，它在大多数 UNIX 系统上都有预装。


# 别名（Aliases）

输入包含大量标志（flags）或冗长选项的长命令可能会很烦人。因此，大多数 shell 支持**别名（aliasing）**。shell 别名是 shell 会自动帮你替换的另一个命令的简短形式。例如，bash 中的一个别名具有如下结构：

```bash
alias alias_name="command_to_alias arg1 arg2"
```

注意等号 `=` 周围没有空格，因为 [`alias`](https://www.man7.org/linux/man-pages/man1/alias.1p.html) 是一个接受单个参数的 shell 命令。

别名有很多方便的功能：

```bash
# 为常用标志创建简称
alias ll="ls -lh"

# 节省大量常见的输入
alias gs="git status"
alias gc="git commit"
alias v="vim"

# 避免打字错误
alias sl=ls

# 覆盖现有命令以获得更好的默认行为
alias mv="mv -i"           # -i 覆盖前会提示
alias mkdir="mkdir -p"     # -p 按需创建父目录
alias df="df -h"           # -h 以人类可读格式打印

# 别名可以组合
alias la="ls -A"
alias lla="la -l"

# 要忽略一个别名，可以在命令前加 \
\ls
# 或者用 unalias 完全禁用别名
unalias la

# 要获取某个别名的定义，直接调用 alias 即可
alias ll
# 将输出 ll='ls -lh'
```

注意，别名默认不会在不同 shell 会话之间持久保存。要使别名持久生效，你需要将其写入 shell 启动文件（如 `.bashrc` 或 `.zshrc`），下一节将对此进行介绍。


# 点文件（Dotfiles）

许多程序使用纯文本文件进行配置，这些文件被称为**点文件（dotfiles）**（因为文件名以 `.` 开头，例如 `~/.vimrc`，这样在默认的 `ls` 目录列表中它们会被隐藏）。

Shell 是此类配置文件的一个典型例子。启动时，你的 shell 会读取多个文件来加载其配置。根据你的 shell 类型以及你是以登录模式（login）还是交互式模式（interactive）启动，整个过程可能相当复杂。[这里](https://web.archive.org/web/20260329133158/https://blog.flowblok.id.au/2013-02/shell-startup-scripts.html) 是一份关于该主题的绝佳资料。

对于 `bash`，在大多数系统上编辑 `.bashrc` 或 `.bash_profile` 即可。你可以在这里写入启动时运行的命令，比如我们刚才描述的别名，或者对 `PATH` 环境变量的修改。事实上，许多程序会要求你在 shell 配置文件中添加类似 `export PATH="$PATH:/path/to/program/bin"` 的一行，以便找到它们的可执行文件。

其他一些可以通过点文件配置的工具示例：

- `bash` - `~/.bashrc`、`~/.bash_profile`
- `git` - `~/.gitconfig`
- `vim` - `~/.vimrc` 和 `~/.vim` 文件夹
- `ssh` - `~/.ssh/config`
- `tmux` - `~/.tmux.conf`

你该如何组织自己的点文件？它们应该放在一个独立的文件夹中，置于版本控制之下，并通过脚本报**符号链接（symlink）**到正确的位置。这样做有如下好处：

- **安装方便**：如果你登录到一台新机器，应用你的自定义配置只需几分钟。
- **可移植性**：你的工具在所有机器上的工作方式都相同。
- **同步**：你可以在任何地方更新点文件，并让它们保持同步。
- **变更追踪**：你可能会在整段编程生涯中维护自己的点文件，而版本历史对于长期项目来说是很有用的。

你应该在点文件中放些什么？
你可以通过阅读在线文档或[手册页（man pages）](https://en.wikipedia.org/wiki/Man_page)来了解工具的设置。另一个好方法是上网搜索关于特定程序的博客文章，作者会分享他们偏好的配置。还有一种了解配置的方式是查看别人的点文件：你可以在 GitHub 上找到大量的[点文件仓库](https://github.com/search?o=desc&q=dotfiles&s=stars&type=Repositories)——看看最受欢迎的[这个](https://github.com/mathiasbynens/dotfiles)（但我们不建议你盲目复制配置）。[这里](https://dotfiles.github.io/) 也是另一份关于该主题的良好资源。

所有课程讲师的点文件都在 GitHub 上公开：[Anish](https://github.com/anishathalye/dotfiles)、[Jon](https://github.com/jonhoo/configs)、[Jose](https://github.com/jjgo/dotfiles)。


## 可移植性

点文件的一个常见痛点是，当在多台机器上工作时（例如它们具有不同的操作系统或 shell），配置可能无法正常运行。有时你还希望某些配置仅在某台特定机器上生效。

这里有一些让事情变得更简单的技巧。如果配置文件支持的话，使用类似 if 语句的结构来应用针对特定机器的自定义配置。例如，你的 shell 配置可以这样写：

```bash
if [[ "$(uname)" == "Linux" ]]; then {do_something}; fi

# 在使用 shell 特定功能前进行检查
if [[ "$SHELL" == "zsh" ]]; then {do_something}; fi

# 也可以针对特定机器
if [[ "$(hostname)" == "myServer" ]]; then {do_something}; fi
```

如果配置文件支持，还可以使用 include（包含）机制。例如，`~/.gitconfig` 中可以包含一个设置：

```
[include]
    path = ~/.gitconfig_local
```

然后在每台机器上，`~/.gitconfig_local` 可以包含针对该机器的特定配置。你甚至可以将这些配置放在一个单独的仓库中进行管理。

这个思路也适用于不同程序共享某些配置的场景。例如，如果你希望 `bash` 和 `zsh` 共享同一组别名，可以将它们写入 `.aliases`，然后在两个配置文件中都加入如下代码块：

```bash
# 测试 ~/.aliases 是否存在并加载它
if [ -f ~/.aliases ]; then
    source ~/.aliases
fi
```


# 远程机器

程序员在日常工作中使用远程服务器的情况越来越普遍。如果你需要远程服务器来部署后端软件，或者你需要一台算力更强的服务器，你就最终会使用安全壳（Secure Shell，即 SSH）。像大多数被覆盖的工具一样，SSH 高度可配置，值得花时间去学习。

要 `ssh` 到一台服务器上，你执行的命令如下：

```bash
ssh foo@bar.mit.edu
```

这里我们尝试以用户 `foo` 的身份登录到服务器 `bar.mit.edu`。服务器可以通过 URL（如 `bar.mit.edu`）或 IP 地址（如 `192.168.1.42`）来指定。稍后我们会看到，如果你修改了 SSH 配置文件，甚至可以像 `ssh bar` 这样简单登录。

## 执行命令

`ssh` 有一个经常被忽略的功能——直接运行命令。
`ssh foobar@server ls` 将在 foobar 的主目录中执行 `ls`。
它与管道（pipe）配合良好，因此 `ssh foobar@server ls | grep PATTERN` 将在本地过滤远程 `ls` 的输出，而 `ls | ssh foobar@server grep PATTERN` 将在远程过滤本地 `ls` 的输出。


## SSH 密钥

基于密钥的身份验证利用了公钥密码学来向服务器证明客户端拥有正确的私钥，而无需暴露密钥本身。这样你就不需要每次重新输入密码了。不过，私钥（通常是 `~/.ssh/id_rsa`，较新的是 `~/.ssh/id_ed25519`）实质上就是你的密码，因此应当妥善保管。

### 密钥生成

要生成密钥对，可以运行 [`ssh-keygen`](https://www.man7.org/linux/man-pages/man1/ssh-keygen.1.html)。
```bash
ssh-keygen -a 100 -t ed25519 -f ~/.ssh/id_ed25519
```
你应该选择一个密码短语（passphrase），以防止他人获取你的私钥后访问已授权的服务器。使用 [`ssh-agent`](https://www.man7.org/linux/man-pages/man1/ssh-agent.1.html) 或 [`gpg-agent`](https://linux.die.net/man/1/gpg-agent) 可以避免每次都要输入密码短语。

如果你曾经使用 SSH 密钥配置过向 GitHub 推送代码，那你可能已经按照[这篇指南](https://help.github.com/articles/connecting-to-github-with-ssh/)中概述的步骤操作过，并且已经有一个有效的密钥对了。要检查你的密钥是否设置了密码短语并验证它，可以运行 `ssh-keygen -y -f /path/to/key`。

### 基于密钥的身份验证

`ssh` 会查阅 `.ssh/authorized_keys` 文件来确定应该允许哪些客户端连接。要将公钥复制到远程服务器上，可以使用：

```bash
cat .ssh/id_ed25519.pub | ssh foobar@remote 'cat >> ~/.ssh/authorized_keys'
```

如果可用的话，使用 `ssh-copy-id` 可以更加简便：

```bash
ssh-copy-id -i .ssh/id_ed25519 foobar@remote
```


## 通过 SSH 复制文件

有多种方式可以通过 SSH 复制文件：

- `ssh+tee`，最简单的方式是使用 `ssh` 命令执行功能和 STDIN 输入，即执行 `cat localfile | ssh remote_server tee serverfile`。回想一下，[`tee`](https://www.man7.org/linux/man-pages/man1/tee.1.html) 会将来自 STDIN 的输出写入文件。
- [`scp`](https://www.man7.org/linux/man-pages/man1/scp.1.html) 当需要复制大量文件/目录时，安全复制命令 `scp` 会更方便，因为它可以轻松地递归遍历路径。语法为 `scp path/to/local_file remote_host:path/to/remote_file`。
- [`rsync`](https://www.man7.org/linux/man-pages/man1/rsync.1.html) 改进了 `scp`，它可以检测本地和远程上相同的文件并避免重复复制。它还提供了对符号链接、权限更细粒度的控制，并且有一些额外功能，如 `--partial` 标志，可以从之前中断的复制处恢复。`rsync` 的语法与 `scp` 类似。


## 端口转发

在很多场景中，你会遇到监听机器上特定端口的软件。当这种情况发生在你本地机器上时，你可以输入 `localhost:PORT` 或 `127.0.0.1:PORT`。但对于一台端口没有通过网络/互联网直接暴露的远程服务器，你该怎么做呢？

这就是**端口转发（port forwarding）**，它分为两种形式：本地端口转发和远程端口转发（更多细节请参阅图片，图片来源自[这篇 StackOverflow 帖子](https://unix.stackexchange.com/questions/115897/whats-ssh-port-forwarding-and-whats-the-difference-between-ssh-local-and-remot)）。

**本地端口转发**
![Local Port Forwarding](/static/media/images/local-port-forwarding.png)

**远程端口转发**
![Remote Port Forwarding](/static/media/images/remote-port-forwarding.png)

最常见的场景是本地端口转发——即远程机器上的某个服务监听某个端口，而你希望将本地机器上的某个端口转发到远程端口。例如，我们在远程服务器上执行了监听 `8888` 端口的 `jupyter notebook`。要将它转发到本地端口 `9999`，我们可以执行 `ssh -L 9999:localhost:8888 foobar@remote_server`，然后在本地机器上访问 `localhost:9999`。


## SSH 配置

我们已经介绍了很多可以传递的参数。一个有吸引力的替代方案是创建看起来像这样的 shell 别名：
```bash
alias my_server="ssh -i ~/.ssh/id_ed25519 --port 2222 -L 9999:localhost:8888 foobar@remote_server"
```

不过，使用 `~/.ssh/config` 有一个更好的替代方案。

```bash
Host vm
    User foobar
    HostName 172.16.174.141
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
    LocalForward 9999 localhost:8888

# 配置也可以接受通配符
Host *.mit.edu
    User foobaz
```

与别名相比，使用 `~/.ssh/config` 文件的另一个好处是，`scp`、`rsync`、`mosh` 等其他程序也能够读取它，并将这些配置转换为相应的命令行参数。


请注意，`~/.ssh/config` 文件可以视为点文件，通常情况下将它与其他点文件放在一起没有问题。但是，如果你把它公开了，就要考虑你可能向互联网上的陌生人提供了什么信息：服务器的地址、用户名、开放的端口等。这可能会帮助某些类型的攻击，因此在分享你的 SSH 配置时要三思。

服务器端的配置通常在 `/etc/ssh/sshd_config` 中指定。你可以在这里进行修改，比如禁用密码认证、更改 SSH 端口、启用 X11 转发等。你可以按用户指定配置设置。


## 杂项

连接远程服务器时一个常见的痛点是，由于电脑关机、休眠或网络变更而导致的断连。此外，如果你的连接存在较大延迟，使用 SSH 可能会非常令人沮丧。[Mosh](https://mosh.org/)（移动 Shell）改进了 SSH，支持漫游连接（roaming connections）、间歇性连接，并提供智能本地回显（intelligent local echo）。

有时将远程文件夹挂载到本地会很方便。[sshfs](https://github.com/libfuse/sshfs) 可以在本地挂载远程服务器上的文件夹，然后你就可以使用本地编辑器。


# Shell 与框架

在之前的 shell 工具和脚本章节中，我们学习了 `bash` shell，因为它无疑是使用最广泛的 shell，并且大多数系统都以它作为默认选项。不过，它不是唯一的选择。

例如，`zsh` shell 是 `bash` 的超集，开箱即用地提供了许多方便的功能，例如：

- 更智能的路径扩展（globbing），`**`
- 内联 globbing/通配符扩展
- 拼写纠正
- 更好的 Tab 补全/选择
- 路径展开（`cd /u/lo/b` 会自动展开为 `/usr/local/bin`）

**框架（Frameworks）**也能改善你的 shell 体验。一些流行的通用框架包括 [prezto](https://github.com/sorin-ionescu/prezto) 或 [oh-my-zsh](https://ohmyz.sh/)，还有一些专注于特定功能的小型框架，如 [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting) 或 [zsh-history-substring-search](https://github.com/zsh-users/zsh-history-substring-search)。像 [fish](https://fishshell.com/) 这样的 shell 默认就包含了众多这些用户友好功能。其中一些功能包括：

- 右对齐提示符（right prompt）
- 命令语法高亮
- 历史子串搜索
- 基于手册页的 flag 补全
- 更智能的自动补全
- 提示符主题

使用这些框架时需要注意的一点是，它们可能会拖慢你的 shell 速度，尤其是如果它们运行的代码未经良好优化或者代码量过大。你可以始终对其进行性能分析（profile），并禁用那些你不常用或认为性能比功能更重要的特性。


# 终端模拟器

在自定义你的 shell 之外，花时间选择**终端模拟器（terminal emulator）**并调整其设置也是值得的。市面上有许多终端模拟器（这里有一份[对比](https://anarc.at/blog/2018-04-12-terminal-emulators-1/)）。

由于你可能在终端中花费数百到数千个小时，优化其设置是物有所值的。你可能希望修改的方面包括：

- 字体选择
- 配色方案（Color Scheme）
- 键盘快捷键
- 标签页/窗格支持
- 滚动历史记录配置
- 性能（一些较新的终端模拟器如 [Alacritty](https://github.com/jwilm/alacritty) 或 [kitty](https://sw.kovidgoyal.net/kitty/) 提供了 GPU 加速）。


# 练习

## 作业控制

1. 基于我们之前看到的，我们可以使用一些 `ps aux | grep` 命令来获取作业的 pid 然后杀掉它们，但有更好的方法。在一个终端中启动一个 `sleep 10000` 作业，通过 `Ctrl-Z` 将其放到后台，然后用 `bg` 继续执行。现在使用 [`pgrep`](https://www.man7.org/linux/man-pages/man1/pgrep.1.html) 查找它的 pid，再用 [`pkill`](https://man7.org/linux/man-pages/man1/pgrep.1.html) 杀掉它，整个过程不需要输入 pid 本身。（提示：使用 `-af` 标志）。

2. 假设你不想在另一个进程完成之前启动一个进程。你会怎么做？在这个练习中，我们的阻塞进程始终是 `sleep 60 &`。
    一种方法是使用 [`wait`](https://www.man7.org/linux/man-pages/man1/wait.1p.html) 命令。尝试先启动 sleep 命令，然后让 `ls` 等待后台进程完成。

    然而，如果你在一个不同的 bash 会话中启动，此策略会失败，因为 `wait` 只对子进程有效。我们在笔记中没有讨论的一个特性是：`kill` 命令在成功时退出状态为零，否则为非零。`kill -0` 不会发送信号，但如果进程不存在则会给出一个非零退出状态。
    编写一个名为 `pidwait` 的 bash 函数，它接受一个 pid 并等待给定进程完成。你应该使用 `sleep` 来避免不必要地浪费 CPU 资源。

## 终端复用器

1. 跟随这份 `tmux` [教程](https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/)，然后按照[这些步骤](https://www.hamvocke.com/blog/a-guide-to-customizing-your-tmux-conf/)学习如何进行一些基本的自定义配置。

## 别名

1. 创建一个别名 `dc`，当打错字时它可以解析为 `cd`。

2. 运行 `history | awk '{$1="";print substr($0,2)}' | sort | uniq -c | sort -n | tail -n 10` 来获取你使用频率最高的前 10 个命令，并考虑为它们编写更短的别名。注意：这适用于 Bash；如果你使用的是 ZSH，请改用 `history 1` 而不是仅 `history`。


## 点文件

下面让我们快速上手点文件的使用。

1. 为你的点文件创建一个文件夹并设置版本控制。
2. 为至少一个程序添加配置，例如你的 shell，并加入一些自定义配置（从简单的开始，比如通过设置 `$PS1` 来自定义你的 shell 提示符）。
3. 建立一种在新机器上快速（且无需手动操作）安装点文件的方法。这可以简单到一个调用 `ln -s` 为每个文件创建符号链接的 shell 脚本，你也可以使用[专用工具](https://dotfiles.github.io/utilities/)。
4. 在一台全新的虚拟机上测试你的安装脚本。
5. 将所有现有的工具配置迁移到你的点文件仓库中。
6. 在 GitHub 上公开发布你的点文件。

## 远程机器

为本练习安装一个 Linux 虚拟机（或者使用已有的虚拟机）。如果你不熟悉虚拟机，可以参考[这篇](https://hibbard.eu/install-ubuntu-virtual-box/)教程来安装一个。

1. 进入 `~/.ssh/`，检查那里是否有 SSH 密钥对。如果没有，使用 `ssh-keygen -a 100 -t ed25519` 生成它们。建议使用密码短语，并使用 `ssh-agent`，更多信息见[这里](https://www.ssh.com/ssh/agent)。
2. 编辑 `.ssh/config`，添加如下条目：

    ```bash
    Host vm
        User username_goes_here
        HostName ip_goes_here
        IdentityFile ~/.ssh/id_ed25519
        LocalForward 9999 localhost:8888
    ```
3. 使用 `ssh-copy-id vm` 将你的 SSH 密钥复制到服务器上。
4. 在 VM 中执行 `python -m http.server 8888` 启动一个 web 服务器。在你的机器上访问 `http://localhost:9999` 即可访问 VM 的 web 服务器。
5. 通过执行 `sudo vim /etc/ssh/sshd_config` 编辑你的 SSH 服务器配置，通过编辑 `PasswordAuthentication` 的值来禁用密码认证。通过编辑 `PermitRootLogin` 的值来禁用 root 登录。使用 `sudo service sshd restart` 重启 `ssh` 服务。然后再次尝试通过 SSH 登录。
6. （进阶）在 VM 中安装 [`mosh`](https://mosh.org/) 并建立连接。然后断开服务器/VM 的网络适配器。Mosh 能否从中正确恢复？
7. （进阶）查看 `ssh` 中 `-N` 和 `-f` 标志的作用，并找出一个可以实现后台端口转发的命令。