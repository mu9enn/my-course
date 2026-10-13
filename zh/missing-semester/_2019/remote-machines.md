---
layout: lecture
title: "远程主机"
presenter: Jose
date: 2019-01-29
order: 4
video:
  aspect: 62.5
  id: X5c2Y8BCowM
---

程序员在日常工作中使用远程服务器的情况越来越普遍。如果你需要部署后端软件，或者需要一台计算能力更强的服务器，你就难免要用到安全外壳（Secure Shell，简称 SSH）。与本文讨论的多数工具一样，SSH 高度可配置，值得花时间去了解它。

## 执行命令

`ssh` 有一个经常被忽略的功能：直接执行远程命令。

- `ssh foobar@server ls` 会在 foobar 用户的主目录下执行 `ls`
- 它与管道配合同样有效，因此 `ssh foobar@server ls | grep PATTERN` 会在本地远程输出中匹配 `ls` 的结果，而 `ls | ssh foobar@server grep PATTERN` 则会在远程匹配本地 `ls` 的输出。

## SSH 密钥

基于密钥的身份验证利用公钥密码学，在不泄露密钥的前提下向服务器证明客户端持有对应的私钥。这样你就不必每次都重新输入密码。不过，私钥（例如 `~/.ssh/id_rsa`）实质上就是你的密码——请务必像保护密码一样保护它。

- 密钥生成。只需运行 `ssh-keygen -t rsa -b 4096` 即可生成一对密钥。如果你不设置密码短语（passphrase），那么任何人拿到你的私钥就能访问已授权的服务，因此**强烈建议**设置一个密码短语，并使用 `ssh-agent` 来管理 shell 会话中的密钥。

如果你已经使用 SSH 密钥配置过向 GitHub 推送代码，那你很可能已经按照[此处](https://help.github.com/articles/connecting-to-github-with-ssh/)的步骤操作过，并且已经拥有一对有效的密钥了。你可以运行 `ssh-keygen -y -f /path/to/key` 来检查密钥是否设置了密码短语并验证其有效性。

- 基于密钥的身份验证。`ssh` 会读取 `.ssh/authorized_keys` 来确定允许哪些客户端连接。要把公钥复制过去，我们可以用以下命令：

```bash
cat .ssh/id_dsa.pub | ssh foobar@remote 'cat >> ~/.ssh/authorized_keys'
```

如果系统上有 `ssh-copy-id` 命令，使用它会更为简单：

```bash
ssh-copy-id -i .ssh/id_dsa.pub foobar@remote
```

## 通过 SSH 传输文件

通过 SSH 传输文件有多种方式：

- `ssh+tee`：最简单的方式是使用 `ssh` 命令执行并结合标准输入：`cat localfile | ssh remote_server tee serverfile`
- `scp`：当需要传输大量文件或目录时，安全复制命令 `scp` 更为方便，因为它可以轻松递归遍历路径。语法为 `scp path/to/local_file remote_host:path/to/remote_file`
- `rsync`：在 `scp` 的基础上，`rsync` 能够检测本地和远程相同的文件从而避免重复拷贝。它还提供了更细粒度的符号链接和权限控制，并附带一些额外功能，例如 `--partial` 标志支持从之前中断的位置恢复传输。`rsync` 的语法与 `scp` 类似。

## 后台进程

默认情况下，当你中断一个 SSH 连接时，父 shell 的子进程也会连同它一起被杀死。以下是几种替代方案：

- `nohup` —— `nohup` 命令可以让进程在终端被关闭后继续运行。虽然使用 `&` 和 `disown` 有时也能达到类似效果，但 `nohup` 是更稳妥的默认选择。更多细节见[此处](https://unix.stackexchange.com/questions/3886/difference-between-nohup-disown-and)。

- `tmux`、`screen` —— 对于后台运行进程而言，`nohup` 虽然有效，但对交互式 shell 会话来说并不方便。此时使用终端复用器（terminal multiplexer）如 `screen` 或 `tmux` 是更合适的选择，因为它们允许你轻松分离（detach）和重新附加（reattach）相关的 shell 会话。

另外，如果你已经 disown 了一个程序，却想把它重新附加到当前终端上，可以使用 [reptyr](https://github.com/nelhage/reptyr)。执行 `reptyr PID` 即可将 PID 标识的进程抓取出来并附加到你的当前终端。

## 端口转发（Port Forwarding）

在很多场景中，你会遇到需要监听本机端口的软件。在本地机器上，你只需访问 `localhost:PORT` 或 `127.0.0.1:PORT` 即可，但如果对方是一台端口无法直接通过网络/互联网访问的远程服务器呢？——这就涉及到**端口转发**（Port Forwarding），它有两种形式：本地端口转发（Local Port Forwarding）和远程端口转发（Remote Port Forwarding）（详见下图，图片来源：[SO 帖子](https://unix.stackexchange.com/questions/115897/whats-ssh-port-forwarding-and-whats-the-difference-between-ssh-local-and-remot)）。

**本地端口转发**
![本地端口转发](https://i.stack.imgur.com/a28N8.png)

**远程端口转发**
![远程端口转发](https://i.stack.imgur.com/4iK3b.png)

最常见的场景是本地端口转发：远程机器上的某个服务监听了一个端口，而你想把本地机器的一个端口转发到远程端口。例如，如果你在远程服务器上执行了监听 `8888` 端口的 `jupyter notebook`，那么要将它转发到本地的 `9999` 端口，你可以执行 `ssh -L 9999:localhost:8888 foobar@remote_server`，然后在本地浏览器访问 `localhost:9999` 即可。

## 图形转发（Graphics Forwarding）

有时仅转发端口还不够——因为你想要在服务器上运行基于 GUI 的程序。你当然可以求助于远程桌面软件（例如 RealVNC、TeamViewer 等），它们会传输整个桌面环境。但对于单个 GUI 程序而言，SSH 提供了一个更好的替代方案：图形转发（X11 转发）。

使用 `-X` 标志即可告诉 SSH 转发图形界面。如需信任模式的 X11 转发（trusted X11 forwarding），可以使用 `-Y` 标志。

需要说明的是，要让转发工作，服务器上的 `sshd_config` 必须包含以下选项：

```bash
X11Forwarding yes
X11DisplayOffset 10
```

## 漫游（Roaming）

连接到远程服务器时，一个常见的痛点是电脑关机/睡眠或更换网络导致的断连。此外，如果你的连接存在明显延迟，使用 SSH 会变得非常令人沮丧。[Mosh](https://mosh.org/)（移动 shell）改进了 SSH，支持漫游连接、间歇性连接以及智能本地回显（local echo）。

Mosh 在所有常见发行版和包管理器中都可用。Mosh 要求在服务器上运行 SSH 服务。你不需要超级用户权限来安装 mosh，但需要确保服务器上的端口 60000 到 60010 处于开放状态（它们通常都是开放的，因为这些端口不在特权端口范围内）。

`mosh` 的一个缺点是它不支持漫游端口转发和图形转发，因此如果你经常使用这些功能，`mosh` 可能对你帮助有限。

## SSH 配置

### 客户端

我们介绍了许多可以传递给 `ssh` 的参数。一个诱人的替代方案是创建 shell 别名，例如 `alias my_server="ssh -X -i ~/.ssh/id_rsa -L 9999:localhost:8888 foobar@remote_server"`，但实际上有更好的选择——使用 `~/.ssh/config` 文件。

```bash
Host vm
    User foobar
    HostName 172.16.174.141
    Port 22
    IdentityFile ~/.ssh/id_rsa
    RemoteForward 9999 localhost:8888

# Configs can also take wildcards
Host *.mit.edu
    User foobaz
```

使用 `~/.ssh/config` 文件的另一个优势是，其他程序（如 `scp`、`rsync`、`mosh` 等）也能读取它，并自动将其转换为相应的参数。

需要注意，`~/.ssh/config` 文件可以被视为一个**隐藏配置文件**（dotfile）。通常来说，将它和其他 dotfile 放在一起管理没有问题。但如果你将其公开，请想想你可能向互联网上的陌生人暴露了哪些信息：你的服务器地址、你使用的用户名、开放的端口等。这可能会助长某些类型的攻击，因此在公开 SSH 配置时需要慎重。

**警告：绝对不要将你的 RSA 密钥（`~/.ssh/id_rsa*`）放在公开仓库中！**

### 服务端

服务端配置通常写在 `/etc/ssh/sshd_config` 中。你可以在这里做出如下变更：禁用密码认证、更改 SSH 端口、启用 X11 转发等。配置项也可以按用户单独指定。

## 远程文件系统

有时将远程文件夹挂载到本地会非常方便。[sshfs](https://github.com/libfuse/sshfs) 可以在本地挂载远程服务器上的文件夹，这样你就可以使用本地编辑器工作了。

## 练习

1. SSH 要能正常工作，目标主机需要运行 SSH 服务。在一台虚拟机上安装一个 SSH 服务端（例如 OpenSSH），以便完成后续练习。运行 `ip addr` 命令可以查看该机器的 IP 地址，并寻找 `inet` 字段（忽略 `127.0.0.1` 条目，那是回环接口）。

1. 进入 `~/.ssh/` 目录，检查是否有 SSH 密钥对。如果没有，使用 `ssh-keygen -t rsa -b 4096` 生成。建议设置一个密码，并配合 `ssh-agent` 使用。更多信息见[此处](https://www.ssh.com/ssh/agent)。

1. 使用 `ssh-copy-id` 将密钥复制到你的虚拟机。测试无密码 SSH 连接是否成功。然后，编辑服务器上的 `sshd_config`，修改 `PasswordAuthentication` 的值以禁用密码认证。同时修改 `PermitRootLogin` 的值以禁用 root 登录。

1. 修改服务器上的 `sshd_config` 来更改 SSH 端口，然后验证你仍然能够正常连接 SSH。如果你有一台面向公网的服务器，使用非默认端口和仅密钥登录将大幅减少恶意攻击的数量。

1. 在你的服务器/虚拟机上安装 mosh，建立连接后，断开服务器/虚拟机的网络适配器。观察 mosh 能否从断连中自动恢复。

1. 本地端口转发还有一种用途：将某个网站通过隧道转发到服务器。如果你的网络屏蔽了一些网站（例如 `reddit.com`），可以按照如下方式通过服务器进行隧道传输：

    - 运行 `ssh remote_server -L 80:reddit.com:80`
    - 在 `/etc/hosts` 中将 `reddit.com` 和 `www.reddit.com` 指向 `127.0.0.1`
    - 确认你正在通过服务器访问该网站
    - 如果结果不够直观，可以使用像 [ipinfo.io](https://ipinfo.io/) 这样的网站——它会随你主机的公网 IP 而变化

1. 后台端口转发可以借助几个额外标志轻松实现。查阅 `ssh` 的 `-N` 和 `-f` 标志分别做了什么，然后理解类似 `ssh -N -f -L 9999:localhost:8888 foobar@remote_server` 这样的命令整体做了什么。

## 参考资料

- [SSH Hacks](https://matt.might.net/articles/ssh-hacks/)
- [Secure Secure Shell](https://stribika.github.io/2015/01/04/secure-secure-shell.html)

{% comment %}
Lecture notes will be available by the start of lecture.
{% endcomment %}