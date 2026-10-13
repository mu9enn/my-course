---
layout: lecture
title: "万花筒"
description: >
  了解多种有用主题，包括键盘重映射、守护进程、备份、API 等。
thumbnail: /static/assets/thumbnails/2020/lec10.png
date: 2020-01-29
ready: true
video:
  aspect: 56.25
  id: JZDt-PRq0uo
special: true
---

## 目录

- [键盘重映射](#keyboard-remapping)
- [守护进程](#daemons)
- [FUSE](#fuse)
- [备份](#backups)
- [API](#apis)
- [常用命令行标志/模式](#common-command-line-flagspatterns)
- [窗口管理器](#window-managers)
- [虚拟专用网络](#vpns)
- [Markdown](#markdown)
- [Hammerspoon（macOS 桌面自动化）](#hammerspoon-desktop-automation-on-macos)
- [开机 +  Live USB](#booting--live-usbs)
- [Docker、Vagrant、虚拟机、云、OpenStack](#docker-vagrant-vms-cloud-openstack)
- [笔记本编程](#notebook-programming)
- [GitHub](#github)

## 键盘重映射

作为程序员，键盘是你的主要输入设备。就像电脑里的大多数东西一样，它是可配置的（而且确实值得配置）。

最基本的改动是重新映射按键。这通常涉及一些监听软件：每当按下某个键时，它会拦截该事件，并用对应另一个键的事件来替换。举几个例子：
- 将 Caps Lock（大写锁定）映射为 Ctrl 或 Escape。我们（讲师）非常推荐这个设置，因为 Caps Lock 的位置很便利但很少被用到。
- 将 PrtSc（打印屏幕）映射为播放/暂停音乐。大多数操作系统都自带播放/暂停键。
- 交换 Ctrl 键和 Meta（Windows 或 Command）键。

你也可以将按键映射到你选择的任意命令。这对频繁执行的任务特别有用。在这种设置下，软件会监听特定的组合键，并在检测到该组合键时执行某个脚本。
- 打开新的终端或浏览器窗口。
- 输入一段特定的文本，比如你的长邮件地址或 MIT 学号。
- 让电脑或显示器进入睡眠状态。

还有一些更复杂的自定义方式：
- 映射按键序列，例如连续按 Shift 五次来切换 Caps Lock。
- 区分轻触和按住，例如快速按下 Caps Lock 键映射为 Esc，按住并用作修饰键时映射为 Ctrl。
- 让重映射仅对特定键盘或特定软件生效。

以下是该领域的一些入门工具：
- macOS — [karabiner-elements](https://karabiner-elements.pqrs.org/)、[skhd](https://github.com/koekeishiya/skhd) 或 [BetterTouchTool](https://folivora.ai/)
- Linux — [xmodmap](https://wiki.archlinux.org/index.php/Xmodmap) 或 [Autokey](https://github.com/autokey/autokey)
- Windows — 控制面板自带功能、[AutoHotkey](https://www.autohotkey.com/) 或 [SharpKeys](https://www.randyrants.com/category/sharpkeys/)
- QMK — 如果你的键盘支持自定义固件，可以使用 [QMK](https://docs.qmk.fm/) 配置硬件本身，这样重映射在你使用的任何机器上都会生效。

## 守护进程

你可能已经熟悉守护进程（daemons）的概念，即使这个词听起来比较陌生。大多数电脑都有一些始终在后台运行的进程，而不是等待用户启动并与其交互。这些进程被称为守护进程，作为守护进程运行的程序通常以字母 `d` 结尾以作标识。例如 `sshd`（SSH 守护进程）就是负责监听传入 SSH 请求并验证远程用户是否具有登录所需凭据的程序。

在 Linux 中，`systemd`（系统守护进程）是运行和配置守护进程最常见的方案。你可以运行 `systemctl status` 来列出当前正在运行的守护进程。大多数名称你可能没听说过，但它们负责系统的核心部分，比如管理网络、解析 DNS 查询或显示图形界面。你可以通过 `systemctl` 命令来 `enable`（启用）、`disable`（禁用）、`start`（启动）、`stop`（停止）、`restart`（重启）或检查服务的 `status`（状态）（这些就是 `systemctl` 的子命令）。

更有趣的是，`systemd` 提供了一个比较友好的接口来配置和启用新的守护进程（或服务）。下面是一个运行简单 Python 应用的守护进程配置示例。我们不会深入细节，但可以看到大部分字段都非常直观易懂。

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Custom App
After=network.target

[Service]
User=foo
Group=foo
WorkingDirectory=/home/foo/projects/mydaemon
ExecStart=/usr/bin/local/python3.7 app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

另外，如果你只是想以某个固定频率运行某个程序，无需构建自定义守护进程，你可以使用 [`cron`](https://www.man7.org/linux/man-pages/man8/cron.8.html)——一个系统已经运行的守护进程，用于执行定时任务。

## FUSE

现代软件系统通常由更小的构建模块组合而成。你的操作系统之所以支持使用不同的文件系统后端，是因为存在一套关于"文件系统支持哪些操作"的共同约定。例如，当你运行 `touch` 来创建文件时，`touch` 会向内核发起一次系统调用以创建文件，内核再执行相应的文件系统操作来创建指定文件。不过有一个需要注意的地方：UNIX 文件系统传统上作为内核模块实现，只有内核才被允许执行文件系统调用。

[FUSE](https://en.wikipedia.org/wiki/Filesystem_in_Userspace)（文件系统用户空间）允许文件系统由用户态程序来实现。FUSE 让用户空间的代码能够处理文件系统调用，并将必要的调用桥接到内核接口。这意味着用户可以为文件系统调用实现任意功能。

例如，FUSE 可以用于这样一种场景：当你对一个虚拟文件系统执行某个操作时，该操作通过 SSH 转发到远程机器执行，然后将结果返回给你。这样，本地程序就能将该文件看作存在于你的电脑上，而实际上它存储在远程服务器中。`sshfs` 正是这么做的。

以下是一些有趣的 FUSE 文件系统示例：
- [sshfs](https://github.com/libfuse/sshfs) — 通过 SSH 连接在本地打开远程文件或文件夹。
- [rclone](https://rclone.org/commands/rclone_mount/) — 挂载 Dropbox、GDrive、Amazon S3 或 Google Cloud Storage 等云存储，在本地打开数据。
- [gocryptfs](https://nuetzlich.net/gocryptfs/) — 加密覆盖系统。文件以加密形式存储，但挂载后在挂载点中以明文形式呈现。
- [kbfs](https://keybase.io/docs/kbfs) — 端到端加密的分布式文件系统。你可以创建私有、共享和公共文件夹。
- [borgbackup](https://borgbackup.readthedocs.io/en/stable/usage/mount.html) — 挂载去重、压缩和加密的备份，方便浏览。

> 译者注：FUSE 的核心价值在于它打破了"只有内核才能实现文件系统"的限制。传统 UNIX 文件系统中，文件系统代码必须作为内核模块编译加载，升级文件系统格式或调试都非常困难。FUSE 之后，你可以完全用 Python 或 Go 写一个挂载在某个路径上的文件系统——比如把加密的 S3 桶挂载成本地目录，而应用程序根本不需要修改。

## 备份

任何你没有备份的数据，都可能随时永远消失。把数据复制来复制去很容易，可靠地备份数据却很难。以下是一些基本的备份原则，以及某些方法的陷阱。

首先，同一块磁盘上的数据副本不是备份，因为这块磁盘是所有数据的单点故障。同样地，存放在家里的外置硬盘也是一种较弱的备份方案——它可能在火灾、被盗等情况下与主数据一起丢失。因此，建议采用异地备份（off-site backup）。

同步解决方案不是备份。例如，Dropbox / Google Drive 确实是便捷的方案，但它们会在数据被删除或损坏时同步这些变更。同样的原因，RAID 等磁盘镜像方案也不是备份。如果数据被删除、损坏或被勒索软件加密，镜像并不能帮你恢复。

好的备份解决方案有几个核心特性：**版本管理**、**去重**和**安全性**。版本管理确保你可以访问变更历史并高效恢复文件。高效的备份方案使用数据去重来只存储增量变更，从而降低存储开销。至于安全性，你应该思考：什么人需要知道什么信息才能读取你的数据，更重要的是，什么人需要知道什么信息才能删除你的数据和所有关联备份。最后，盲目信任备份是一个非常糟糕的想法，你应该定期验证自己能否使用备份恢复数据。

备份的范围不限于你电脑上的本地文件。随着 Web 应用的显著增长，你大量数据仅存储在云端。例如，如果你失去对相关账户的访问权限，你的网络邮件、社交媒体照片、流媒体服务的音乐歌单或在线文档都会随之消失。为这些信息保留一个离线副本才是正道，而网上已经有不少人为此构建了数据抓取和保存工具。

如需更详细的说明，请参阅 2019 年的课程笔记 [Backups](/2019/backups)。

## API

我们在本课程中讨论了很多关于更高效地使用电脑来完成**本地**任务的内容，但你会发现，其中许多经验也适用于更广阔的网络世界。大多数在线服务都会提供"API"（应用程序接口），让你可以编程式地访问它们的数据。例如，美国政府有一个 API，让你可以获取天气预报，这样你就能直接在 shell 中获取某个地区的天气预报。

大多数 API 的格式相似。它们是结构化的 URL，通常以 `api.service.com` 为根，路径和查询参数指示你要读取的数据或要执行的操作。以美国天气数据为例，要获取某个特定位置的预报，你可以发出一个 GET 请求（例如使用 `curl`）到 `https://api.weather.gov/points/42.3604,-71.094`。响应本身包含一组其他 URL，让你可以获取该区域的详细预报。通常，响应以 JSON 格式呈现，之后你可以使用 [`jq`](https://stedolan.github.io/jq/) 等工具将其处理为你需要的格式。

有些 API 需要认证，这通常表现为一个需要随请求附带的**token**（令牌）。你应该阅读 API 文档来了解具体服务使用何种认证方式，但你会经常见到 **[OAuth](https://www.oauth.com/)** 协议。从本质上说，OAuth 是一种让你获得 token 的方式，这些 token 可以"代表你"在某个服务上操作，并且仅限于特定用途。请记住，这些 token 是**秘密**的，任何获得你 token 的人都可以以你的账户执行该 token 允许的一切操作！

[IFTTT](https://ifttt.com/) 是一个围绕 API 理念构建的网站和服务——它与众多服务提供集成，并允许你将来自这些服务的事件以近乎任意的顺序串联起来。值得去探索一番。

## 常用命令行标志/模式

命令行工具千差万别，在使用它们之前，你经常需要查看其 `man` 页面。不过它们经常共享一些共同特性，了解这些可能对你有帮助：

- 大多数工具支持某种 `--help` 标志，用来显示该工具的简要使用说明。
- 许多可能产生不可逆变更的工具支持"干跑"（dry run）概念，即只打印它们**本会做什么**，而不实际执行变更。类似的，它们通常还有一个"交互式"标志，在执行每个破坏性操作前都会向你确认。
- 你通常可以使用 `--version` 或 `-V` 来让程序打印其自身版本（报告 bug 时非常有用）。
- 几乎所有工具都有 `--verbose` 或 `-v` 标志来产生更详细的输出。你通常可以多次使用该标志（`-vvv`）来得到**更多**详细输出，这在调试时很有用。类似的，许多工具还有 `--quiet` 标志，只允许在出错时打印内容。
- 在许多工具中，文件名位置用 `-` 表示"标准输入"或"标准输出"，具体取决于参数的上下文。
- 可能产生破坏性影响的工具通常默认不是递归的，但会支持一个"递归"标志（通常是 `-r`）来启用递归。
- 有时，你想把一个**看起来像标志**的东西当作普通参数传递。例如，想象你想删除一个名为 `-r` 的文件。或者你想"通过"另一个程序运行一个程序，如 `ssh machine foo`，而你想给"内部"程序（`foo`）传递一个标志。特殊的参数 `--` 会让程序**停止**处理后面出现的所有标志和选项（以 `-` 开头的内容），这样你就能传递看起来像标志的东西而不会被当作标志处理：`rm -- -r` 或 `ssh machine --for-ssh -- foo --for-foo`。

## 窗口管理器

大多数人都习惯了使用"拖放式"窗口管理器，就像 Windows、macOS 和 Ubuntu 默认自带的那样。窗口在屏幕上随意悬挂，你可以拖拽它们、调整大小，让它们互相重叠。但这只是**一种**窗口管理器，通常被称为"浮动式"窗口管理器。还有多种其他类型，在 Linux 上尤其常见。一个特别常见的替代方案是"平铺式"（tiling）窗口管理器。在平铺窗口管理器中，窗口从不重叠，而是像 tmux 中的面板一样以平铺方式排列在屏幕上。使用平铺窗口管理器时，屏幕总是被打开的窗口填满，按照某种**布局**排列。如果你只有一个窗口，它占满整个屏幕。如果你再打开一个，原来的窗口会缩小以腾出空间（通常是 2/3 和 1/3）。再打开第三个，其他窗口会再次缩小以适应新窗口。就像 tmux 面板一样，你可以用键盘在这些平铺窗口之间导航，也可以调整大小和移动它们，完全不需要碰鼠标。值得研究一下！

## 虚拟专用网络

VPNs 最近很火，但显然这不是因为 [任何好的理由](https://web.archive.org/web/20230710155258/https://gist.github.com/joepie91/5a9909939e6ce7d09e29)。你应该了解 VPN 能做什么、不能做什么。在最理想的情况下，VPN 本质上只是让你在互联网提供商的视角中改变了你的互联网服务提供商。你的所有流量看起来都来自 VPN 提供商，而不是你"真实"的位置，而你连接的网络只能看到加密的流量。

虽然这听起来很有吸引力，但请记住，使用 VPN 时，你实际上只是在将信任从当前的 ISP 转移到 VPN 托管公司。你的 ISP 能**看到**的东西，现在 VPN 提供商**取而代之**看到了。如果你比信任你的 ISP 更信任他们，那当然有利可图，否则就不一定了。如果你在机场的一个不安全的未加密公共 Wi-Fi 上，也许你确实不太信任这条连接，但在家里，这种权衡就不那么清晰了。

你还需要知道，如今你的很多流量——至少是敏感流量——已经通过 HTTPS 或更通用的 TLS**加密**。在这种情况下，无论你是否在"不安全"网络上通常差别不大——网络运营商只能知道你和哪些服务器通信，而不会知道交换的具体数据内容。

注意我上面说的是"在最理想的情况下"。VPN 提供商意外配置错误导致加密变弱甚至完全关闭的情况并不罕见。有些 VPN 提供商是恶意的（或者至少是机会主义者），它们会记录你的所有流量，并可能将有关信息出售给第三方。选择一个糟糕的 VPN 提供商，通常比根本不用一个更糟糕。

退一步说，MIT [运行了一个 VPN](https://ist.mit.edu/vpn) 供学生使用，所以值得一看。另外，如果你打算自己搭建，可以看看 [WireGuard](https://www.wireguard.com/)。

## Markdown

你在职业生涯中很可能会写一些文本，而且你通常希望对这些文本进行简单的标记。你可能想让某些文字加粗或斜体，或者添加标题、链接和代码片段。与其使用 Word 或 LaTeX 这样的重型工具，你可能更倾向于使用轻量级标记语言 [Markdown](https://commonmark.org/help/)。

你可能已经见过 Markdown，或者至少见过它的某种变体。它的子集被广泛使用和支持，即使不叫 Markdown 这个名字。从核心来看，Markdown 是对人们已经习惯于在纯文本文档中标记文本的方式的一种编码。强调（*斜体*）通过在单词两侧加上 `*` 来实现。强烈强调（**粗体**）使用 `**`。以 `#` 开头的行是标题（`#` 的数量表示子标题级别）。以 `-` 开头的行是项目符号列表项，以数字 + `.` 开头的行是编号列表项。反引号用于显示 `等宽代码`，代码块可以通过在行前缩进四个空格或将其包裹在三个反引号中来插入：

    ```
    code goes here
    ```

要添加链接，将链接的**文字**放在方括号中，URL 紧跟在括号后面：`[name](url)`。Markdown 上手很简单，你几乎可以在任何地方使用它。事实上，本课程所有讲义（包括这一篇）都是用 Markdown 编写的，你可以[在这里](https://raw.githubusercontent.com/missing-semester/missing-semester/master/_2020/potpourri.md)看到原始 Markdown 文件。

## Hammerspoon（macOS 桌面自动化）

[Hammerspoon](https://www.hammerspoon.org/) 是 macOS 的桌面自动化框架。它允许你编写 Lua 脚本，挂钩操作系统功能，从而与键盘/鼠标、窗口、显示器、文件系统等交互，甚至更多。

以下是你可以使用 Hammerspoon 做的事情的一些示例：

- 绑定热键将窗口移动到特定位置
- 创建一个菜单栏按钮，自动将窗口布局为特定排列
- 当你到达实验室时自动静音你的扬声器（通过检测 Wi-Fi 网络）
- 如果你不小心拿了朋友的电源适配器，给你一个警告

从高层次来看，Hammerspoon 允许你运行任意 Lua 代码，绑定到菜单栏按钮、按键或事件上，而 Hammerspoon 提供了广泛的系统交互库，所以基本上你用它做什么都行。很多人公开了自己的 Hammerspoon 配置，所以你通常可以通过搜索互联网找到所需的内容，但你也完全可以从零开始编写自己的代码。

### 资源

- [Hammerspoon 入门](https://www.hammerspoon.org/go/)
- [示例配置](https://github.com/Hammerspoon/hammerspoon/wiki/Sample-Configurations)
- [Anish 的 Hammerspoon 配置](https://github.com/anishathalye/dotfiles-local/tree/mac/hammerspoon)

## 开机 + Live USB

当你的机器启动时，在操作系统加载之前，[BIOS](https://en.wikipedia.org/wiki/BIOS)/[UEFI](https://en.wikipedia.org/wiki/Unified_Extensible_Firmware_Interface) 会初始化系统。在这个过程中，你可以按下特定的键组合来配置这层软件。例如，在启动过程中，你的电脑可能会显示"按 F9 配置 BIOS。按 F12 进入启动菜单"之类的信息。你可以在 BIOS 菜单中配置各种与硬件相关的设置。你也可以进入启动菜单从其他设备（而非你的硬盘）启动。

[Live USB](https://en.wikipedia.org/wiki/Live_USB) 是包含操作系统的 U 盘。你可以通过下载一个操作系统（例如某个 Linux 发行版）并将其烧录到 U 盘上来创建这样一个 Live USB。这个过程比简单地把 `.iso` 文件复制到磁盘要稍微复杂一些。有一些工具如 [UNetbootin](https://unetbootin.github.io/) 可以帮你创建 Live USB。

Live USB 有多种用途。其中一件有用的事情是：如果你的现有操作系统安装损坏到无法启动，你可以使用 Live USB 来恢复数据或修复操作系统。

## Docker、Vagrant、虚拟机、云、OpenStack

[虚拟机](https://en.wikipedia.org/wiki/Virtual_machine)和类似的工具（如容器）让你可以模拟整个计算机系统，包括操作系统。这在创建用于测试、开发或探索的隔离环境时非常有用（例如运行可能有问题的代码）。

[Vagrant](https://www.vagrantup.com/) 是一个工具，可以让你以代码描述机器配置（操作系统、服务、软件包等），然后通过一个简单的 `vagrant up` 实例化虚拟机。[Docker](https://www.docker.com/) 在概念上类似，但它使用容器而非虚拟机。

你也可以在云端租用虚拟机，这种方式可以让你快速获得：

- 一台廉价的常在线机器，具有公网 IP 地址，用于托管服务
- 一台拥有大量 CPU、磁盘、RAM 和/或 GPU 的机器
- 远超你物理访问能力的更多机器（计费通常按秒计算，因此如果你需要大量计算资源但只需很短时间，租用 1000 台电脑几分钟是完全可行的）

热门的服务包括 [Amazon AWS](https://aws.amazon.com/)、[Google Cloud](https://cloud.google.com/)、[Microsoft Azure](https://azure.microsoft.com/)、[DigitalOcean](https://www.digitalocean.com/)。

如果你是 MIT CSAIL 的成员，你可以通过 [CSAIL OpenStack 实例](https://tig.csail.mit.edu/shared-computing/open-stack/) 为研究目的免费获取虚拟机。

## 笔记本编程

[笔记本编程环境](https://en.wikipedia.org/wiki/Notebook_interface)在进行某些类型的交互式或探索式开发时可能非常有用。如今最受欢迎的笔记本编程环境可能是用于 Python（以及多种其他语言）的 [Jupyter](https://jupyter.org/)。[Wolfram Mathematica](https://www.wolfram.com/mathematica/) 是另一种优秀的笔记本编程环境，非常适合数学相关的编程。

## GitHub

[GitHub](https://github.com/) 是最流行的开源软件开发平台之一。我们在本课程中讨论的许多工具，从 [vim](https://github.com/vim/vim) 到 [Hammerspoon](https://github.com/Hammerspoon/hammerspoon)，都在 GitHub 上托管。开始为开源项目做贡献以改进你每天使用的工具，这并不困难。

人们为 GitHub 上的项目贡献主要有两种途径：

- 创建 [issue](https://help.github.com/en/github/managing-your-work-on-github/creating-an-issue)。这可以用来报告 bug 或请求新功能。这两种方式都不涉及阅读或编写代码，因此你可以非常轻量地参与。高质量的 bug 报告对开发者非常有价值。在已有讨论中发表评论也会有所帮助。
- 通过 [pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) 贡献代码。这通常比创建 issue 更复杂一些。你可以 [fork](https://help.github.com/en/github/getting-started-with-technology/fork-a-repo) GitHub 上的一个仓库，clone 你的 fork，创建一个新分支，做一些修改（例如修复 bug 或实现新功能），推送该分支，然后[创建一个 pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)。之后，项目维护者通常会和你来回沟通，对你的 patch 给出反馈。最后，如果一切顺利，你的 patch 会被合并到上游仓库。很多时候，较大的项目会有贡献指南、标记适合新手的 issue，甚至有些还有导师项目来帮助初次贡献者熟悉项目。

> 译者注：GitHub 的 fork-branch-pull request 工作流是开源协作的标准模式。初次参与时，建议先在 README 或 `CONTRIBUTING.md` 文件中寻找该项目对贡献流程的具体要求（比如代码风格、测试覆盖或 commit message 格式），这能大幅减少来回修改的次数。